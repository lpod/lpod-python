# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy

# Import from itools
from itools import vfs
from itools.core import get_abspath
from itools.xml import XMLParser


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


# Standard parts in the archive (other are regular paths)
ODF_PARTS = ['content', 'meta', 'mimetype', 'settings', 'styles']


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

        self.uri = uri
        # TODO XML
        self.file = vfs.mount_archive(uri)

        mimetype = self.get_part('mimetype')
        if mimetype is None:
            mimetype = vfs.get_mimetype(uri)
        if not mimetype in ODF_MIMETYPES:
            raise ValueError, "mimetype '%s' is unknown" % mimetype

        self.mimetype = mimetype


    def clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name in ('uri', 'file'):
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)

        return clone


    def get_part(self, part_name):
        archive = self.file
        if part_name in ODF_PARTS and part_name != 'mimetype':
            # TODO XML
            file = archive.open('%s.xml' % part_name)
            part = XMLParser(file)
            file.close()
        else:
            # TODO XML
            file = archive.open(part_name)
            part = file.read()
            file.close()

        return part


    def __del__(self):
        if getattr(self, 'file', None) is not None:
            self.file.unmount()



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
    return template.clone()



def get_odf_container(uri):
    """Return an "odf_container" instance of the ODF document stored at the
    given URI.
    """
    return odf_container(uri)
