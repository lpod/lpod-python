# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy

# Import from itools
from itools import vfs
from itools.core import get_abspath


# Classes and their default template
ODF_CLASSES = {
        'text': 'templates/text.ott',
        'spreadsheet': 'templates/spreadsheet.ots',
        'presentation': 'templates/presentation.otp',
        'drawing': 'templates/drawing.otg',
        # TODO
}


# File extensions and their mimetype
ODF_EXTENSIONS = {
        'odt': 'application/vnd.oasis.opendocument.text',
        'ott': 'application/vnd.oasis.opendocument.text-template',
        'ods': 'application/vnd.oasis.opendocument.spreadsheet',
        'ots': 'application/vnd.oasis.opendocument.spreadsheet-template',
        'odp': 'application/vnd.oasis.opendocument.presentation',
        'otp': 'application/vnd.oasis.opendocument.presentation-template',
        'odg': 'application/vnd.oasis.opendocument.graphics',
        'otg': 'application/vnd.oasis.opendocument.graphics-template'
}


# Mimetypes and their file extension
ODF_MIMETYPES = {
        'application/vnd.oasis.opendocument.text': 'odt',
        'application/vnd.oasis.opendocument.text-template': 'ott',
        'application/vnd.oasis.opendocument.spreadsheet': 'ods',
        'application/vnd.oasis.opendocument.spreadsheet-template': 'ots',
        'application/vnd.oasis.opendocument.presentation': 'odp',
        'application/vnd.oasis.opendocument.presentation-template': 'otp',
        'application/vnd.oasis.opendocument.graphics': 'odg',
        'application/vnd.oasis.opendocument.graphics-template': 'otg'
}


class odf_container(object):
    """Representation of the ODF document.
    """

    def __init__(self, uri):
        if not vfs.exists(uri):
            raise ValueError, "URI is not found"
        if not vfs.can_read(uri):
            raise ValueError, "URI is not readable"
        if vfs.is_folder(uri):
            raise NotImplementedError, ("reading uncompressed ODF "
                                        "is not supported")

        mimetype = vfs.get_mimetype(uri)
        if mimetype not in ODF_MIMETYPES:
            raise ValueError, "mimetype '%s' is unknown" % mimetype

        # If all is OK
        self.uri = uri
        self.mimetype = mimetype
        self.file = vfs.open(uri)


    def _clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name in ('uri', 'file'):
                setattr(clone, 'uri', None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)

        return clone



def new_odf_container(odf_class=None, template_uri=None):
    """Return an "odf_container" instance of a new ODF document, from a
    default template or from the given template.
    """
    if ((odf_class is None and template_uri is None)
         or (odf_class is not None and template_uri is not None)):
        raise ValueError, "either 'odf_class' or 'template_uri' is mandatory"
    if odf_class not in ODF_CLASSES:
        raise ValueError, "unknown ODF class '%s'" % odf_class

    if odf_class is not None:
        template_path = ODF_CLASSES[odf_class]
        template_uri = get_abspath(template_path)

    template = get_odf_container(template_uri)

    # Return a copy of the template
    return template._clone()



def get_odf_container(uri):
    """Return an "odf_container" instance of the ODF document stored at the
    given URI.
    """
    return odf_container(uri)
