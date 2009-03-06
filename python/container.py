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
        'application/vnd.oasis.opendocument.graphics-template': 'otg',
        # XML-only document
        'application/xml': 'xml',
}


# Standard parts in the container (other are regular paths)
ODF_PARTS = ['content', 'meta', 'mimetype', 'settings', 'styles']


class odf_container(object):
    """Representation of the ODF document.
    """

    def __init__(self, uri):
        if not vfs.exists(uri):
            raise ValueError, 'URI "%s" is not found' % uri
        if not vfs.can_read(uri):
            raise ValueError, 'URI "%s" is not readable' % uri
        if vfs.is_folder(uri):
            raise NotImplementedError, ("reading uncompressed ODF "
                                        "is not supported")

        mimetype = vfs.get_mimetype(uri)
        if not mimetype in ODF_MIMETYPES:
            raise ValueError, 'mimetype "%s" is unknown' % mimetype

        self.uri = uri
        self.mimetype = mimetype
        # Internal state
        self.__data = None
        self.__archive = None
        self.__parts = {}



    def clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'uri':
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)

        return clone


    def __get_data(self):
        if self.__data is None:
            file = vfs.open(self.uri)
            self.__data = file.read()
            file.close()
        return self.__data


    def __get_archive(self):
        if self.__archive is None:
            self.__archive = vfs.mount_archive(self.uri)
        return self.__archive


    def __get_part_xml(self, part_name):
        if part_name not in ODF_PARTS:
            raise ValueError, ("Third-party parts are not supported "
                               "in an XML-only ODF document")
        if part_name == 'mimetype':
            part = self.mimetype
        else:
            data = self.__get_data()
            start_tag = '<office:document-%s>' % part_name
            start = data.index(start_tag)
            end_tag = '</office:document-%s>' % part_name
            end = data.index(end_tag)
            part = data[start:end + len(end_tag)]
        return part



    def __get_part_zip(self, part_name):
        archive = self.__get_archive()
        if part_name in ODF_PARTS and part_name != 'mimetype':
            file = archive.open('%s.xml' % part_name)
            part = file.read()
            file.close()
        else:
            file = archive.open(part_name)
            part = file.read()
            file.close()
        return part


    def get_part(self, part_name):
        loaded_parts = self.__parts
        if part_name in loaded_parts:
            part = loaded_parts[part_name]
            if part is None:
                raise ValueError, "part is deleted"
            return part
        if self.mimetype == 'application/xml':
            part = self.__get_part_xml(part_name)
        else:
            part = self.__get_part_zip(part_name)
        loaded_parts[part_name] = part
        return part


    def set_part(self, part_name, data):
        self.__parts[part_name] = data


    def del_part(self, part_name):
        # Mark for deletion
        self.__parts[part_name] = None



def odf_get_container(uri):
    """Return an "odf_container" instance of the ODF document stored at the
    given URI.
    """
    return odf_container(uri)



def odf_new_container_from_template(template_uri):
    """Return an "odf_container" instance using the given template.
    """
    template_container = odf_get_container(template_uri)
    # Return a copy of the template container
    return template_container.clone()



def odf_new_container_from_class(odf_class):
    """Return an "odf_container" instance of the given class.
    """
    if odf_class not in ODF_CLASSES:
        raise ValueError, 'unknown ODF class "%s"' % odf_class
    template_path = ODF_CLASSES[odf_class]
    template_uri = get_abspath(template_path)
    return odf_new_container_from_template(template_uri)
