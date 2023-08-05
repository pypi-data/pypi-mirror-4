###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import datetime
import hashlib
import logging
import math
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from bson.binary import Binary

import zope.interface
from zope.contenttype import guess_content_type

from m01.mongo import UTC

import m01.grid.exceptions
from m01.grid import interfaces


logger = logging.getLogger('m01.grid')

_SEEK_SET = os.SEEK_SET
_SEEK_CUR = os.SEEK_CUR
_SEEK_END = os.SEEK_END


def extractFileName(filename):
    """Stip out path in filename (happens in IE upload)"""
    # strip out the path section even if we do not remove them
    # later, because we just need to check the filename extension.
    cleanFileName = filename.split('\\')[-1]
    cleanFileName = cleanFileName.split('/')[-1]
    dottedParts = cleanFileName.split('.')
    if len(dottedParts) <= 1:
        raise m01.grid.exceptions.MissingFileNameExtension()
    return cleanFileName


def getContentType(filename):
    """Returns the content type based on the given filename"""
    return guess_content_type(filename)[0]


class ChunkIterator(object):
    """Chunk iterator"""

    zope.interface.implements(interfaces.IChunkIterator)

    def __init__(self, reader, chunks):
        self.__id = reader._id
        self.__chunks = chunks
        self.__current_chunk = 0
        self.__max_chunk = math.ceil(float(reader.length) / reader.chunkSize)

    def __iter__(self):
        return self

    def next(self):
        if self.__current_chunk >= self.__max_chunk:
            raise StopIteration
        chunk = self.__chunks.find_one({"files_id": self.__id,
                                        "n": self.__current_chunk})
        if not chunk:
            raise m01.grid.exceptions.CorruptFile(
                "no chunk #%d" % self.__current_chunk)
        self.__current_chunk += 1
        return str(chunk["data"])


class ChunkLogging(object):
    """Logging support"""

    def _doLog(self, msg, level=logging.DEBUG):
        logger.log(level, '%s %s %s %s' % (self._id, self._chunks.name,
            self.__class__.__name__, msg))

    def info(self, msg):
        self._doLog(msg, logging.INFO)

    def debug(self, msg):
        self._doLog(msg, logging.DEBUG)

    def error(self, msg):
        self._doLog(msg, logging.ERROR)
    

class ChunkWriterBase(ChunkLogging):
    """File chunk writer base class

    The mongodb GirdFS specification defines the following key/value:

    {
    "_id" : <unspecified>,      // unique ID for this file
    "length" : data_number,     // size of the file in bytes
    "chunkSize" : data_number,  // size of each of the chunks. (default 256k)
    "uploadDate" : data_date,   // date when object first stored
    "md5" : data_string         // result of running the "filemd5" command
    }

    Another requirement is, that the file and chunk collections must use the
    same prefix and use files and chunks as appendix. This means we need to
    use dotted collection names. 

    doc.files
    doc.chunks

    Probably this is for hook up some server side miracles. At least the
    filemd5 database command requires that we use the collection name prefix
    as root name. e.g.

    md5 = database.command("filemd5", self._id, root='doc')["md5"]

    A ChunkWriterBase based implementation must provide the following
    attributes based on the processing file:

    _id
    _chunks
    chunkSize
    maxFileSize
    removed

    """
    zope.interface.implements(interfaces.IChunkWriter)

    def __init__(self):
        """Setup ChunkWriterBase basics"""
        self._chunkNumber = 0
        self._buffer = StringIO()
        self._length = 0
        self._closed = False

    @property
    def closed(self):
        """Return close marker"""
        return self._closed

    def close(self):
        """Flush the file and close it.

        A closed file cannot be written any more. Calling `close` more than
        once is allowed.
        """
        if not self._closed:
            self._closed = True

    def validate(self, fileUpload):
        """Validate file upload item"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        elif not fileUpload or not fileUpload.filename:
            # empty string or None or missing filename means no upload given
            raise ValueError("Missing file upload data")
        elif self.removed:
            raise ValueError("Can't store data for removed files")

    def validateSize(self, data):
        if self.maxFileSize is not None:
            size = self._length + len(data)
            if size > self.maxFileSize:
                raise m01.grid.exceptions.TooLargeFile()

    def makeTMPChunk(self):
        """Move existing chunks away till we uploaded new data"""
        self.debug('make tmp chunk')
        _id = '%s-tmp' % self._id
        self._chunks.update({"files_id": self._id},
                            {"$set": {'files_id': _id}}, safe=True)
    
    def revertTMPChunk(self):
        """Revert tmp chunk"""
        self.debug('revert tmp chunk')
        _id = '%s-tmp' % self._id
        self._chunks.update({"files_id": _id},
                            {"$set": {'files_id': self._id}}, safe=True)

    def removeTMPChunk(self):
        """Remove tmp chunk"""
        self.debug('remove tmp chunk')
        _id = '%s-tmp' % self._id
        self._chunks.remove({"files_id": _id}, safe=True)

    def setFileName(self, filename):
        """Set filename (hook for adjust the given filename)"""
        self.context.filename = unicode(filename)

    def setContentType(self, contentType):
        """Set content type (hook for adjust the given type)"""
        self.context.contentType = unicode(contentType)

    # mongo upload helper
    def _flushData(self, data):
        """Flush data to a chunk"""
        if not data:
            return
        assert(len(data) <= self.chunkSize)

        self.validateSize(data)

        self.debug('flush data')
        chunk = {"files_id": self._id,
                 "n": self._chunkNumber,
                 "data": Binary(data)}

        self._chunks.insert(chunk)
        self._chunkNumber += 1
        self._length += len(data)

    def _flushBuffer(self):
        """Flush the buffer out to a chunk"""
        self._flushData(self._buffer.getvalue())
        self._buffer.close()
        self._buffer = StringIO()

    def write(self, data):
        """Write data to mongodb"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        digester = hashlib.md5()
        try:
            # file-like
            read = data.read
        except AttributeError:
            # string
            if not isinstance(data, basestring):
                raise TypeError("can only write strings or file-like objects")
            if isinstance(data, unicode):
                try:
                    data = data.encode(self.encoding)
                except AttributeError:
                    raise TypeError("must specify an encoding for file in "
                                    "order to write unicode")
            read = StringIO(data).read

        if self._buffer.tell() > 0:
            # flush only when _buffer is full
            space = self.chunkSize - self._buffer.tell()
            if space:
                to_write = read(space)
                self._buffer.write(to_write)
                digester.update(to_write)
                if len(to_write) < space:
                    return # EOF or incomplete
            self._flushBuffer()
        to_write = read(self.chunkSize)
        while to_write and len(to_write) == self.chunkSize:
            self._flushData(to_write)
            digester.update(to_write)
            to_write = read(self.chunkSize)
        self._buffer.write(to_write)
        digester.update(to_write)
        self._flushBuffer()
        return digester

    def add(self, fileUpload):
        """Upload file data as chunk"""
        success = False
        self.validate(fileUpload)
        filename = extractFileName(fileUpload.filename)
        contentType = getContentType(filename)
        # first find out if we have existing chunk data
        isUpdate = self._chunks.find({"files_id": self._id}).count()
        if isUpdate:
            self.debug('update')
        else:
            self.debug('add')
        try:
            if isUpdate:
                self.makeTMPChunk()
            # make sure we begin at the start
            fileUpload.seek(0)
            digester = self.write(fileUpload)
            # filemd5 returns the following data
            # {u'md5': u'b10a8db164e0754105b7a99be72e3fe5',
            #  u'ok': 1.0,
            #  u'numChunks': 1}
            # get root collection name by strip '.chunks' from chunks 
            # collection name e.g. self._chunks.name[:-len('.chunks')]
            rootCollectionName = str(self._chunks.name[:-7])
            filemd5 = self._chunks.database.command("filemd5", self._id,
                root=rootCollectionName)
            numChunks = filemd5['numChunks']
            _md5 = filemd5["md5"]
            if _md5 != digester.hexdigest():
                # raise exception
                raise ValueError("MD5 hex digest does not match for uploaded data")
            if self._chunkNumber != numChunks:
                raise ValueError("Not correct number of chunks stored")
            # marker for successfully added chunk
            success = True
        except Exception, e:
            self.error('add caused an error')
            logger.exception(e)
            # on any exception, we will remove new added chunks
            self._chunks.remove({"files_id": self._id}, safe=True)
            # on update, we revert our TMP chunk
            if isUpdate:
                self.revertTMPChunk()
            # and raise the exception
            raise e
        finally:
            if isUpdate:
                self.removeTMPChunk()
            self.close()

        if success:
            # apply chunk metadata to adapted FileItem
            self.context.uploadDate = datetime.datetime.now(UTC)
            self.context.md5 = unicode(_md5)
            self.context.numChunks = numChunks
            self.context.length = self._length
            self.setFileName(filename)
            self.setContentType(contentType)
            self.debug('success')

    def remove(self):
        """Mark chunk data as removed"""
        self._chunks.update({"files_id": self._id},
                            {"$set": {'removed': True}}, safe=True)

    def __enter__(self):
        """Support for the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for the context manager protocol.

        Close the file and allow exceptions to propogate.
        """
        self.close()
        # propogate exceptions
        return False


class ChunkWriter(ChunkWriterBase):
    """File chunk writer adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context):
        """Setup ChunkWriter based on adapted context"""
        super(ChunkWriter, self).__init__()
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        if not self.context.chunkCollection.name.endswith('.chunks'):
            raise ValueError("Chunks collection name must end with .chunks")
        self._chunks = self.context.chunkCollection
        self.chunkSize = self.context.chunkSize
        self.maxFileSize = self.context.maxFileSize
        self.removed = self.context.removed


class ChunkReaderBase(ChunkLogging):
    """File chunk reader adapter

    A ChunkReaderBase absed implementation must provide the following
    attributes:

    _id          file _id
    _chunks      (chunk collection, must end with ``.chunks``)
    chunkSize    chunk size
    numChunks    number of chunks
    length       file size
    contentType  content type
    removed      marker for removed files
    
    """

    zope.interface.implements(interfaces.IChunkReader)

    def __init__(self):
        self._buffer = ""
        self._position = 0

    @property
    def size(self):
        """simply map length as size (common in zope)"""
        return self.length

    @property
    def __name__(self):
        """simply map filename as __name__ (common in zope)"""
        return self.filename

    def validate(self):
        if self.removed:
            raise ValueError("Can't read data from removed files")

    def read(self, size=-1):
        """Read at most `size` bytes from the file

        If size is negative or omitted all data is read
        """
        # validate read operation
        self.validate()

        if size == 0:
            return ""

        remainder = int(self.length) - self._position
        if size < 0 or size > remainder:
            size = remainder

        received = len(self._buffer)
        chunkNumber = (received + self._position) / self.chunkSize
        chunks = []

        while received < size:
            chunk = self._chunks.find_one({"files_id": self._id, 
                "n": chunkNumber})
            if not chunk:
                raise m01.grid.exceptions.CorruptFile(
                    "no chunk #%d" % chunkNumber)
            if received:
                chunk_data = chunk["data"]
            else:
                chunk_data = chunk["data"][self._position % self.chunkSize:]

            received += len(chunk_data)
            chunks.append(chunk_data)
            chunkNumber += 1

        if self.numChunks != chunkNumber:
            raise m01.grid.exceptions.CorruptFile(
                "Used chunk number '%s' does not fit" % chunkNumber,
                    self.numChunks)

        data = "".join([self._buffer] + chunks)
        self._position += size
        to_return = data[:size]
        self._buffer = data[size:]
        return to_return

    def readline(self, size=-1):
        """Read one line or up to `size` bytes from the file"""
        bytes = ""
        while len(bytes) != size:
            byte = self.read(1)
            bytes += byte
            if byte == "" or byte == "\n":
                break
        return bytes

    def tell(self):
        """Return the current position of this file"""
        return self._position

    def seek(self, pos, whence=_SEEK_SET):
        """Set the current position of this file"""
        if whence == _SEEK_SET:
            new_pos = pos
        elif whence == _SEEK_CUR:
            new_pos = self._position + pos
        elif whence == _SEEK_END:
            new_pos = int(self.length) + pos
        else:
            raise IOError(22, "Invalid value for `whence`")
        if new_pos < 0:
            raise IOError(22, "Invalid value for `pos` - must be positive")
        self._position = new_pos
        self._buffer = ""

    def __iter__(self):
        """Return an iterator over all of this file's data"""
        # validate read operation
        self.validate()
        # return iterator
        return ChunkIterator(self, self._chunks)

    def close(self):
        """Support file-like API"""
        pass

    def __enter__(self):
        """Makes it possible to use with the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Makes it possible to use with the context manager protocol"""
        return False


class ChunkReader(ChunkReaderBase):
    """File chunk reader adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context):
        """Setup chunk reader based on adapted context"""
        super(ChunkReader, self).__init__()
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        if not self.context.chunkCollection.name.endswith('.chunks'):
            raise ValueError("Chunks collection name must end with .chunks")
        self._chunks = self.context.chunkCollection

        # IGridFSSpecification
        self.length = self.context.length
        self.chunkSize = self.context.chunkSize
        self.uploadDate = self.context.uploadDate
        self.md5 = self.context.md5
        self.filename = self.context.filename
        self.contentType = self.context.contentType
        # IFile
        self.numChunks = self.context.numChunks
        self.removed = self.context.removed


class ChunkDataReader(ChunkReaderBase):
    """Chunk data reader based on given mongodb file data"""

    def __init__(self, chunkCollection, data):
        """Setup chunk reader based on given file data"""
        super(ChunkDataReader, self).__init__()
        self._id = data['_id']
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        if not chunkCollection.name.endswith('.chunks'):
            raise ValueError("Chunks collection name must end with .chunks")
        self._chunks = self.chunkCollection

        # IGridFSSpecification
        self.length = data['length']
        self.chunkSize = data['chunkSize']
        self.uploadDate = data['uploadDate']
        self.md5 = data['md5']
        self.filename = data['filename']
        self.contentType = data['contentType']
        # IFile
        self.numChunks = data['numChunks']
        self.removed = data['removed']


def getChunkDataReader(collection, query):
    """Lookup a file and return a ChunkDataReader"""
    # get chunks collection
    rootCollectionName = str(collection.name[:-7])
    chunksName = '%s.chunks' % rootCollectionName
    database = collection.database
    chunks = collection.database[chunksName]
    # get data
    data = collection.find_one(query)
    return ChunkDataReader(collection, data)


def getChunkDataReaders(collection, query):
    """Lookup one or more file and return the chunk readers
    
    This is usefull for get files and process them later e.g. collect
    email attachements for processing. But take care, there is no filename or
    other file meta data such chunks. Only use a such chunk reader if you know
    what you are doing ;-). Probably a better idea is to use a ChunkReader.
    """
    # get chunks collection
    rootCollectionName = str(collection.name[:-7])
    chunksName = '%s.chunks' % rootCollectionName
    database = collection.database
    chunks = collection.database[chunksName]
    # get data
    for data in collection.find(query):
        yield ChunkDataReader(collection, data)
