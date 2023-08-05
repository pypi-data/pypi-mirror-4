# Copyright 2009 Canonical Ltd.  All rights reserved.

"""The file manager for the LAZR example web service."""

__metaclass__ = type
__all__ = ['FileManager',
           'ManagedFileResource']

import datetime
# Import SHA in a way compatible with both Python 2.4 and Python 2.6.
try:
    import hashlib
    sha_constructor = hashlib.sha1
except ImportError:
     import sha
     sha_constructor = sha.new

from zope.interface import implements

import grokcore.component

from lazr.restful import ReadOnlyResource
from lazr.restful.example.base.interfaces import IFileManager
from lazr.restful.utils import get_current_web_service_request


class FileManager:
    implements(IFileManager)

    def __init__(self):
        """Initialize with an empty list of files."""
        self.files = {}
        self.counter = 0

    def get(self, id):
        """See `IFileManager`."""
        return self.files.get(id)

    def put(self, mediaType, representation, filename):
        """See `IFileManager`."""
        id = str(self.counter)
        self.counter += 1
        self.files[id] = ManagedFileResource(
            representation, mediaType, filename, datetime.datetime.now())
        return id

    def delete(self, key):
        """See `IFileManager`."""
        if key in self.files:
            del self.files[key]
grokcore.component.global_utility(FileManager)


class ManagedFileResource(ReadOnlyResource):

    def __init__(self, representation, mediaType, filename, last_modified):
        """Initialize with a file to be managed."""
        self.representation = representation
        self.mediaType = mediaType
        self.filename = filename
        self.last_modified = last_modified
        sum = sha_constructor()
        sum.update(representation)
        self.etag = sum.hexdigest()

    def __call__(self):
        """Write the file to the current request."""
        request = get_current_web_service_request()
        response = request.response

        # Handle a conditional request
        incoming_etag = request.getHeader('If-None-Match')
        if incoming_etag == self.etag:
            response.setStatus(304)
            return

        response.setHeader("Content-Type", self.mediaType)
        response.setHeader(
           "Last-Modified", self.last_modified.isoformat())
        response.setHeader("ETag", self.etag)
        response.setHeader(
            "Content-Disposition",
            'attachment; filename="%s"' % self.filename)
        return self.representation
