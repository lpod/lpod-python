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
from os.path import isdir
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, BadZipfile

# Import from lpod
from manifest import odf_manifest
from utils import _get_abspath


# Types and their default template
ODF_TYPES = {
        'text': 'templates/text.ott',
        'spreadsheet': 'templates/spreadsheet.ots',
        'presentation': 'templates/presentation.otp',
        # Follow the spec
        'drawing': 'templates/drawing.otg',
        # Follow the mimetype
        'graphics': 'templates/drawing.otg',
        # TODO
        #'chart': 'templates/chart.otc',
        #'image': 'templates/image.oti',
        #'formula': 'templates/image.otf',
        #'master': 'templates/image.odm',
        #'web': 'templates/image.oth',
}


ODF_TEXT = 'application/vnd.oasis.opendocument.text'
ODF_TEXT_TEMPLATE = 'application/vnd.oasis.opendocument.text-template'
ODF_SPREADSHEET = 'application/vnd.oasis.opendocument.spreadsheet'
ODF_SPREADSHEET_TEMPLATE = 'application/vnd.oasis.opendocument.spreadsheet-template'
ODF_PRESENTATION = 'application/vnd.oasis.opendocument.presentation'
ODF_PRESENTATION_TEMPLATE = 'application/vnd.oasis.opendocument.presentation-template'
ODF_DRAWING = 'application/vnd.oasis.opendocument.graphics'
ODF_DRAWING_TEMPLATE = 'application/vnd.oasis.opendocument.graphics-template'
ODF_CHART = 'application/vnd.oasis.opendocument.chart'
ODF_CHART_TEMPLATE = 'application/vnd.oasis.opendocument.chart-template'
ODF_IMAGE = 'application/vnd.oasis.opendocument.image'
ODF_IMAGE_TEMPLATE = 'application/vnd.oasis.opendocument.image-template'
ODF_FORMULA = 'application/vnd.oasis.opendocument.formula'
ODF_FORMULA_TEMPLATE = 'application/vnd.oasis.opendocument.formula-template'
ODF_MASTER = 'application/vnd.oasis.opendocument.text-master'
ODF_WEB = 'application/vnd.oasis.opendocument.text-web'


# File extensions and their mimetype
ODF_EXTENSIONS = {
        'odt': ODF_TEXT,
        'ott': ODF_TEXT_TEMPLATE,
        'ods': ODF_SPREADSHEET,
        'ots': ODF_SPREADSHEET_TEMPLATE,
        'odp': ODF_PRESENTATION,
        'otp': ODF_PRESENTATION_TEMPLATE,
        'odg': ODF_DRAWING,
        'otg': ODF_DRAWING_TEMPLATE,
        'odc': ODF_CHART,
        'otc': ODF_CHART_TEMPLATE,
        'odi': ODF_IMAGE,
        'oti': ODF_IMAGE_TEMPLATE,
        'odf': ODF_FORMULA,
        'otf': ODF_FORMULA_TEMPLATE,
        'odm': ODF_MASTER,
        'oth': ODF_WEB,
}


# Mimetypes and their file extension
ODF_MIMETYPES = {
        ODF_TEXT: 'odt',
        ODF_TEXT_TEMPLATE: 'ott',
        ODF_SPREADSHEET: 'ods',
        ODF_SPREADSHEET_TEMPLATE: 'ots',
        ODF_PRESENTATION: 'odp',
        ODF_PRESENTATION_TEMPLATE: 'otp',
        ODF_DRAWING: 'odg',
        ODF_DRAWING_TEMPLATE: 'otg',
        ODF_CHART: 'odc',
        ODF_CHART_TEMPLATE: 'otc',
        ODF_IMAGE: 'odi',
        ODF_IMAGE_TEMPLATE: 'oti',
        ODF_FORMULA: 'odf',
        ODF_FORMULA_TEMPLATE: 'otf',
        ODF_MASTER: 'odm',
        ODF_WEB: 'oth',
}


# Standard parts in the container (other are regular paths)
ODF_PARTS = ('content', 'meta', 'settings', 'styles')


class odf_container(object):
    """Representation of the ODF file.
    """
    __zipfile = None
    __zip_packaging = None


    def __init__(self, path_or_file):
        if type(path_or_file) is str:
            # Path
            self.path = path = path_or_file
            if isdir(path):
                message = "reading uncompressed OpenDocument not supported"
                raise NotImplementedError, message
            file = open(path, 'rb')
        else:
            # File-like assumed
            self.path = None
            file = path_or_file
        self.__data = data = file.read()
        zip_expected = data[:4] == 'PK\x03\x04'
        # Most probably zipped document
        try:
            mimetype = self.__get_zip_part('mimetype')
            self.__zip_packaging = True
        except BadZipfile, e:
            if zip_expected:
                raise ValueError, "corrupted or not an OpenDocument archive"
            # Maybe XML document
            try:
                mimetype = self.__get_xml_part('mimetype')
            except ValueError:
                raise ValueError, "bad OpenDocument format"
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


    def __get_xml_part(self, name):
        """Get bytes of a part from the XML-only ODF. No cache.
        """
        if name not in ODF_PARTS and name != 'mimetype':
            raise ValueError, ("Third-party parts are not supported "
                               "in an XML-only ODF document")
        data = self.__get_data()
        if name == 'mimetype':
            start_attr = 'office:mimetype="'
            start = data.index(start_attr) + len(start_attr)
            end = data.index('"', start)
            part = data[start:end]
        else:
            start_tag = '<office:document-%s>' % name
            start = data.index(start_tag)
            end_tag = '</office:document-%s>' % name
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
            elif filename == 'META-INF/manifest.xml':
                result.append('manifest')
            else:
                result.append(filename)
        return result


    def __get_zip_part(self, name):
        """Get bytes of a part from the Zip ODF. No cache.
        """
        zipfile = self.__get_zipfile()
        if name in ODF_PARTS:
            name = name + '.xml'
        elif name == 'manifest':
            name = 'META-INF/manifest.xml'
        return zipfile.read(name)


    def __save_zip(self, file):
        """Save a Zip ODF from the available parts.
        """
        # Parts were loaded by "save"
        parts = self.__parts
        compression = ZIP_DEFLATED
        try:
            filezip = ZipFile(file, 'w', compression=compression)
        except RuntimeError:
            # No zlib module
            compression = ZIP_STORED
            filezip = ZipFile(file, 'w', compression=compression)
        # "Pretty-save" parts in some order
        # mimetype requires to be first and uncompressed
        filezip.compression = ZIP_STORED
        filezip.writestr('mimetype', parts['mimetype'])
        filezip.compression = compression
        # XML parts
        for name in ODF_PARTS:
            filezip.writestr(name + '.xml', parts[name])
        # Everything else
        for name, data in sorted(parts.iteritems()):
            if data is None:
                # Deleted
                continue
            elif name in ODF_PARTS or name in ('mimetype', 'manifest'):
                continue
            filezip.writestr(name, data)
        # Manifest
        filezip.writestr('META-INF/manifest.xml', parts['manifest'])
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


    def get_part(self, name):
        """Get the bytes of a part of the ODF.
        """
        loaded_parts = self.__parts
        if name in loaded_parts:
            part = loaded_parts[name]
            if part is None:
                raise ValueError, 'part "%s" is deleted' % name
            return part
        if self.__zip_packaging is True:
            part = self.__get_zip_part(name)
        else:
            part = self.__get_xml_part(name)
        loaded_parts[name] = part
        return part


    def set_part(self, name, data):
        """Replace or add a new part.
        """
        self.__parts[name] = data


    def del_part(self, name):
        """Mark a part for deletion.
        """
        self.__parts[name] = None


    def clone(self):
        """Make a copy of this container with no path.
        """
        # FIXME must load parts before?
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            # "__zipfile" is not safe to copy
            # but can be recreated from "__data"
            if name in ('path', '_odf_container__zipfile'):
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, target=None, packaging=None):
        """Save the container to the given target, a path or a file-like
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
        for name in self.get_parts():
            if name not in parts:
                self.get_part(name)
        # Open output file
        close_after = False
        if target is None:
            target = self.path
        if type(target) is str:
            file = open(target, 'wb')
            close_after = True
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



def odf_get_container(path_or_file):
    """Return an odf_container instance of the ODF document stored at the
    given local path or in the given (open) file-like object.
    """
    return odf_container(path_or_file)



def odf_new_container_from_template(template_path_or_file):
    """Return an odf_container instance based on the given template.
    """
    template_container = odf_get_container(template_path_or_file)
    # Return a copy of the template container
    clone = template_container.clone()
    # Change type from template to regular
    mimetype = clone.get_part('mimetype').replace('-template', '')
    clone.set_part('mimetype', mimetype)
    # Update the manifest
    manifest = odf_manifest('manifest', clone)
    manifest.set_media_type('/', mimetype)
    clone.set_part('manifest', manifest.serialize())
    return clone



def odf_new_container_from_type(odf_type):
    """Return an "odf_container" instance of the given type.
    """
    if odf_type not in ODF_TYPES:
        raise ValueError, 'unknown ODF type "%s"' % odf_type
    template_path = _get_abspath(ODF_TYPES[odf_type])
    return odf_new_container_from_template(template_path)
