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

import zope.interface
import zope.location.interfaces

import m01.mongo.interfaces
from m01.mongo import LOCAL
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.grid.base
from m01.grid import interfaces


class FileStorageItem(m01.grid.base.FileItemBase):
    """Simple mongo file item.
    
    This FileStorageItem will use the mongo ObjectId as the __name__. This
    means you can't set an own __name__ value for this object.

    Implement your own IFileStorageItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


class SecureFileStorageItem(m01.grid.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    zope.interface.implements(interfaces.ISecureFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


class FileContainerItem(m01.grid.base.FileItemBase):
    """File container item.

    Implement your own IFileContainerItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = []

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


class SecureFileContainerItem(m01.grid.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    zope.interface.implements(interfaces.ISecureFileContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


class FileObject(m01.grid.base.FileBase, m01.mongo.item.MongoObject):
    """MongoObject based file"""

    zope.interface.implements(interfaces.IFileObject)

    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed',
                  'chunkSize', 'numChunks', 'md5', 'uploadDate',
                  'filename', 'length', 'contentType']

    def getFileWriter(self):
        return m01.grid.chunker.ChunkWriter(self)

    def getFileReader(self):
        return m01.grid.chunker.ChunkReader(self)

    @property
    def _oid(self):
        try:
            return u'%s:%s' % (self.__parent__._moid, self._field)
        except AttributeError, e:
            if self.__parent__ is None:
                raise AttributeError("Missing __parent__ object")
            else:
                raise AttributeError(
                    '__parent__ "%s" does not provide an _moid' % (
                        self.__parent__))

    def doRemove(self):
        # never call remove without an _id, this whould remove the collection
        if self._id is None:
            raise ValueError("Empty _id given, this whould remove all objects")
        # first remove file chunk
        writer = self.getFileWriter()
        writer.remove()
        # remove ourself
        self.collection.remove({'_id': self._id})
        if self._oid in LOCAL.__dict__:
            del LOCAL.__dict__[self._oid]
