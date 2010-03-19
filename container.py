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
from cStringIO import StringIO
from time import localtime, time
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo, BadZipfile

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
}


# Standard parts in the container (other are regular paths)
ODF_PARTS = ['content', 'meta', 'settings', 'styles']


class odf_container(object):
    """Representation of the ODF file.
    """
    __zipfile = None
    __zip_packaging = None


    def __init__(self, uri_or_file):
        if type(uri_or_file) is str:
            # URI
            self.uri = uri = uri_or_file
            if not vfs.exists(uri):
                raise ValueError, 'URI "%s" is not found' % uri
            if vfs.is_folder(uri):
                message = "reading uncompressed ODF is not supported"
                raise NotImplementedError, message
            file = vfs.open(uri)
        else:
            # File-like assumed
            self.uri = None
            file = uri_or_file
        self.__data = file.read()
        # Most probably zipped document
        try:
            mimetype = self.__get_zip_part('mimetype')
            self.__zip_packaging = True
        except BadZipfile:
            # Maybe XML document
            mimetype = self.__get_xml_part('mimetype')
            self.__zip_packaging = False
        if mimetype not in ODF_MIMETYPES:
            message = 'Document of unknown type "%s"' % mimetype
            raise ValueError, message
        self.__parts = {'mimetype': mimetype}



    #
    # Private API (internal helpers)
    #

    def __get_data(self):
        """Return bytes of the ODF in memory.
        """
        return self.__data


    # XML implementation

    def __get_xml_parts(self):
        """Get the list of members in the XML-only ODF.
        """
        raise NotImplementedError


    def __get_xml_part(self, part_name):
        """Get bytes of a part from the XML-only ODF. No cache.
        """
        if part_name not in ODF_PARTS and part_name != 'mimetype':
            raise ValueError, ("Third-party parts are not supported "
                               "in an XML-only ODF document")
        data = self.__get_data()
        if part_name == 'mimetype':
            start_attr = 'office:mimetype="'
            start = data.index(start_attr) + len(start_attr)
            end = data.index('"', start)
            part = data[start:end]
        else:
            start_tag = '<office:document-%s>' % part_name
            start = data.index(start_tag)
            end_tag = '</office:document-%s>' % part_name
            end = data.index(end_tag) + len(end_tag)
            part = data[start:end]
        return part


    def __save_xml(self, file):
        """Save an XML-only ODF from the available parts.
        """
        raise NotImplementedError


    # Zip implementation

    def __get_zipfile(self):
        """Open a Zip object on the Zip ODF.
        """
        if self.__zipfile is None:
            data = self.__get_data()
            # StringIO will not duplicate the string, how big it is
            filelike = StringIO(data)
            self.__zipfile = ZipFile(filelike)
        return self.__zipfile


    def __get_zip_parts(self):
        """Get the list of members in the Zip ODF.
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


    def __get_zip_part(self, part_name):
        """Get bytes of a part from the Zip ODF. No cache.
        """
        zipfile = self.__get_zipfile()
        if part_name in ODF_PARTS:
            part_name = '%s.xml' % part_name
        file = zipfile.open(part_name)
        part = file.read()
        file.close()
        return part


    def __save_zip(self, file):
        """Save a Zip ODF from the available parts.
        """
        # Parts were loaded by "save"
        parts = self.__parts
        try:
            filezip = ZipFile(file, 'w', ZIP_DEFLATED)
        except RuntimeError:
            # No zlib module
            filezip = ZipFile(file, 'w', ZIP_STORED)
        # "Pretty"-save parts in some order
        # mimetype requires to be first and uncompressed
        # XXX Taken from zipfile.py just because "writestr" doesn't have
        # "compress_type" argument
        zinfo = ZipInfo(filename='mimetype',
                date_time=localtime(time())[:6])
        zinfo.external_attr = 0600 << 16
        zinfo.compress_type = ZIP_STORED
        filezip.writestr(zinfo, parts['mimetype'])
        # XML parts
        for part_name in ODF_PARTS:
            filezip.writestr(part_name + '.xml', parts[part_name])
        # Everything else
        for part_name, part_data in sorted(parts.iteritems()):
            if part_data is None:
                # Deleted
                continue
            elif part_name == 'mimetype' or part_name in ODF_PARTS:
                continue
            elif part_name == 'META-INF/manifest.xml':
                continue
            filezip.writestr(part_name, part_data)
        parts['META-INF/manifest.xml'] = manifest = self.__get_manifest()
        filezip.writestr('META-INF/manifest.xml', manifest)
        filezip.close()


    #
    # Public API
    #

    def get_parts(self):
        """Get the list of members.
        """
        if self.__zip_packaging is True:
            return self.__get_zip_parts()
        return self.__get_xml_parts()


    def get_part(self, part_name):
        """Get the bytes of a part of the ODF.
        """
        loaded_parts = self.__parts
        if part_name in loaded_parts:
            part = loaded_parts[part_name]
            if part is None:
                raise ValueError, "part is deleted"
            return part
        if self.__zip_packaging is True:
            part = self.__get_zip_part(part_name)
        else:
            part = self.__get_xml_part(part_name)
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


    def __get_manifest(self):
        # Parts were loaded by "save"
        parts = self.__parts
        ns = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
        pattern = (' <manifest:file-entry manifest:media-type="%s" '
                'manifest:full-path="%s"/>')
        conf_ns = 'application/vnd.sun.xml.ui.configuration'
        manifest = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<manifest:manifest xmlns:manifest="%s">' % ns,
                pattern % (parts['mimetype'], '/')]
        # Follow save order
        # XML parts
        for part_name in ODF_PARTS:
            manifest.append(pattern % ('text/xml', part_name + '.xml'))
        # Everything else
        dirs_done = set()
        for part_name, part_data in sorted(parts.iteritems()):
            if part_data is None:
                # Deleted
                continue
            elif part_name == 'mimetype' or part_name in ODF_PARTS:
                continue
            elif part_name == 'META-INF/manifest.xml':
                continue
            elif part_name[-1] == '/' and not part_name in dirs_done:
                manifest.append(pattern % ('', part_name))
                dirs_done.add(part_name)
                continue
            media_type = ''
            if part_name == 'manifest.rdf':
                media_type = 'application/rdf+xml'
            manifest.append(pattern % (media_type, part_name))
            while '/' in part_name:
                dirname, basename = part_name.rsplit('/', 1)
                part_name = dirname + '/'
                if dirname not in dirs_done:
                    media_type = ''
                    if part_name == 'Configurations2/':
                        media_type = conf_ns
                    manifest.append(pattern % (media_type, dirname))
                    dirs_done.add(dirname)
                part_name = dirname
        manifest.append('</manifest:manifest>')
        return '\n'.join(manifest)


    def clone(self):
        """Make a copy of this container with no URI.
        """
        clone = object.__new__(self.__class__)
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


    def save(self, target=None, packaging=None):
        """Save the container to the given target, a URI or a file-like
        object.

        Package the output document in the same format than this document,
        unless "packaging" is different.

        Arguments:

            target -- str or file-like

            packaging -- 'zip' or 'flat'
        """
        parts = self.__parts
        # Packaging
        if packaging is None:
            packaging = 'zip' if self.__zip_packaging is True else 'flat'
        if packaging not in ('zip', 'flat'):
            raise ValueError, 'packaging type "%s" not supported' % packaging
        # Load parts
        for part_name in self.get_parts():
            if part_name not in parts:
                self.get_part(part_name)
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
        if packaging == 'zip':
            self.__save_zip(file)
        else:
            self.__save_xml(file)
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
