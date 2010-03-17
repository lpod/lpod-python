# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the Standard Library
from copy import deepcopy
from zipfile import ZipFile
from cStringIO import StringIO

# Import from lpod
from utils import _get_abspath
from vfs import vfs, WRITE


# Types and their default template
ODF_TYPES = {
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
ODF_PARTS = ['content', 'meta', 'settings', 'styles'] # + 'mimetype'


class odf_container(object):
    """Representation of the ODF file.
    """
    def __init__(self, uri_or_file):
        # Internal state
        self.__zipfile = None
        self.__parts = {}
        # URI
        if type(uri_or_file) is str:
            self.uri = uri_or_file
            if not vfs.exists(uri_or_file):
                raise ValueError, 'URI "%s" is not found' % uri_or_file
            if vfs.is_folder(uri_or_file):
                raise NotImplementedError, ("reading uncompressed ODF "
                                            "is not supported")
            mimetype = vfs.get_mimetype(uri_or_file)
            if not mimetype in ODF_MIMETYPES:
                raise ValueError, 'mimetype "%s" is unknown' % mimetype
            self.mimetype = mimetype
            self.__data = None
        # File-like assumed
        else:
            self.uri = None
            self.__data = uri_or_file.read()
            # FIXME Zip format assumed
            self.mimetype = self.__get_part_zip('mimetype')


    #
    # Private API (internal helpers)
    #

    def __get_data(self):
        """Store bytes of the ODF in memory.
        """
        if self.__data is None:
            file = vfs.open(self.uri)
            self.__data = file.read()
            file.close()
        return self.__data


    def __get_zipfile(self):
        """Open a Zip object on the archive ODF.
        """
        if self.__zipfile is None:
            data = self.__get_data()
            # StringIO will not duplicate the string, how big it is
            filelike = StringIO(data)
            self.__zipfile = ZipFile(filelike)
        return self.__zipfile


    def __get_part_xml(self, part_name):
        """Get bytes of a part from the XML-only ODF.
        """
        if part_name not in ODF_PARTS and part_name != 'mimetype':
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
        """Get bytes of a part from the archive ODF.
        """
        zipfile = self.__get_zipfile()
        if part_name in ODF_PARTS:
            file = zipfile.open('%s.xml' % part_name)
            part = file.read()
            file.close()
        else:
            file = zipfile.open(part_name)
            part = file.read()
            file.close()
        return part


    def __get_xml_contents(self):
        """Get the list of members in the XML-only ODF.
        """
        raise NotImplementedError


    def __get_zip_contents(self):
        """Get the list of members in the archive ODF.
        """
        zipfile = self.__get_zipfile()
        result = []
        for part in zipfile.infolist():
            filename = part.filename
            if filename[-4:] == '.xml' and filename[:-4] in ODF_PARTS:
                result.append(filename[:-4])
            else:
                result.append(filename)
        return result


    def __save_xml(self, file):
        """Save an XML-only ODF from the available parts.
        """
        raise NotImplementedError


    def __save_zip(self, file):
        """Save an archive ODF from the available parts.
        """
        # Parts were loaded by "save"
        parts = self.__parts
        filezip = ZipFile(file, 'w')
        # "Pretty"-save parts in some order
        # mimetype first
        filezip.writestr('mimetype', parts['mimetype'])
        # XML parts
        for part_name in ODF_PARTS:
            filezip.writestr(part_name + '.xml', parts[part_name])
        # Everything else
        for part_name, part_data in parts.iteritems():
            if part_name not in ODF_PARTS and part_name != 'mimetype':
                filezip.writestr(part_name, part_data)
        filezip.close()


    #
    # Public API
    #

    def get_contents(self):
        """Get the list of members.
        """
        if self.mimetype == 'application/xml':
            return self.__get_xml_contents()
        else:
            return self.__get_zip_contents()


    def clone(self):
        """Make a copy of this container with no URI.
        """
        clone = object.__new__(self.__class__)
        # Load state
        self.__get_data()
        for name in self.__dict__:
            # "__zipfile" is not safe to copy
            # but can be recreated from "__data"
            if name in ('uri', '_odf_container__zipfile'):
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def get_part(self, part_name):
        """Get the bytes of a part of the ODF.
        """
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
        """Replace or add a new part.
        """
        self.__parts[part_name] = data


    def del_part(self, part_name):
        """Mark a part for deletion.
        """
        self.__parts[part_name] = None


    def save(self, target=None, packaging=None):
        """Save the container to the given URI (target) or into this file like
        object (if supported).
        """
        parts = self.__parts
        # Load parts
        for part in self.get_contents():
            if part not in parts:
                self.get_part(part)
        # Packaging
        if packaging is None:
            packaging = ('flat' if self.mimetype == 'application/xml' else
                         'zip')
        # Open output file
        close_after = False
        if target is None:
            file = vfs.open(self.uri, WRITE)
            close_after = True
        elif isinstance(target, str):
            close_after = True
            file = vfs.open(target, WRITE)
        else:
            file = target
        # Serialize
        if packaging == 'flat':
            self.__save_xml(file)
        elif packaging == 'zip':
            self.__save_zip(file)
        else:
            raise ValueError, '"%s" packaging type not supported' % packaging
        # Close files we opened ourselves
        if close_after:
            file.close()



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
    clone = template_container.clone()
    # Change type from template to regular
    mimetype = clone.get_part('mimetype')
    clone.set_part('mimetype', mimetype.replace('-template', ''))
    return clone



def odf_new_container_from_type(odf_type):
    """Return an "odf_container" instance of the given type.
    """
    if odf_type not in ODF_TYPES:
        raise ValueError, 'unknown ODF type "%s"' % odf_type
    template_path = ODF_TYPES[odf_type]
    template_uri = _get_abspath(template_path)
    return odf_new_container_from_template(template_uri)
