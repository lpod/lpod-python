# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
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

# Import from lpod
from element import odf_create_element
from xmlpart import odf_xmlpart


def odf_create_file_entry(full_path, media_type):
    data = ('<manifest:file-entry manifest:media-type="%s" '
            'manifest:full-path="%s"/>')
    return odf_create_element(data % (media_type, full_path))



class odf_manifest(odf_xmlpart):

    #
    # Public API
    #

    def get_path_list(self):
        """Return the list of full paths in the manifest.

        Return: list of unicode
        """
        expr = '//manifest:file-entry/attribute::manifest:full-path'
        return self.xpath(expr)


    def get_path_media_list(self):
        """Return the list of (full_path, media_type) pairs in the manifest.

        Return: list of (unicode, str) tuples
        """
        expr = '//manifest:file-entry'
        result = []
        for file_entry in self.xpath(expr):
            result.append((file_entry.get_attribute('manifest:full-path'),
                           file_entry.get_attribute('manifest:media-type')))
        return result


    def get_media_type(self, full_path):
        """Get the media type of an existing path.

        Return: str
        """
        expr = ('//manifest:file-entry[attribute::manifest:full-path="%s"]'
                '/attribute::manifest:media-type')
        result = self.xpath(expr % full_path)
        if not result:
            return None
        return result[0]


    def set_media_type(self, full_path, media_type):
        """Set the media type of an existing path.

        Arguments:

            full_path -- unicode

            media_type -- str
        """
        expr = '//manifest:file-entry[attribute::manifest:full-path="%s"]'
        result = self.xpath(expr % full_path)
        if not result:
            raise KeyError, 'path "%s" not found' % full_path
        file_entry = result[0]
        file_entry.set_attribute('manifest:media-type', str(media_type))


    def add_full_path(self, full_path, media_type=''):
        # Existing?
        existing = self.get_media_type(full_path)
        if existing is not None:
            self.set_media_type(full_path, media_type)
        root = self.get_root()
        file_entry = odf_create_file_entry(full_path, media_type)
        root.append(file_entry)


    def del_full_path(self, full_path):
        expr = '//manifest:file-entry[attribute::manifest:full-path="%s"]'
        result = self.xpath(expr % full_path)
        if not result:
            raise KeyError, 'path "%s" not found' % full_path
        file_entry = result[0]
        root = self.get_root()
        root.delete(file_entry)
