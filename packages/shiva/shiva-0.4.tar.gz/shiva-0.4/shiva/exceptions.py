# -*- coding: utf-8 -*-
class MetadataManagerReadError(Exception):
    pass


class InvalidMimeTypeError(Exception):
    def __init__(self, mimetype):
        msg = "Invalid mimetype '%s'" % str(mimetype)

        super(InvalidMimeTypeError, self).__init__(msg)
