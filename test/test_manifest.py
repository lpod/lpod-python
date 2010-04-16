# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.manifest import odf_manifest


ODP_MEDIA_TYPE = 'application/vnd.oasis.opendocument.presentation'


class ManifestTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/frame_image.odp')
        self.manifest = self.document.get_manifest()
        self.image_path = 'Pictures/10000000000001D40000003C8B3889D9.png'


    def test_get_manifest(self):
        self.assert_(type(self.manifest) is odf_manifest)


    def test_get_path_list(self):
        results = self.manifest.get_path_list()
        self.assertEqual(len(results), 20)


    def test_get_path_media_list(self):
        results = self.manifest.get_path_media_list()
        self.assertEqual(len(results), 20)
        root = results[0]
        self.assertEqual(root, ('/', ODP_MEDIA_TYPE))


    def test_get_media_type_root(self):
        self.assertEqual(self.manifest.get_media_type('/'), ODP_MEDIA_TYPE)


    def test_get_media_type_directory(self):
        self.assertEqual(self.manifest.get_media_type('Pictures/'), '')


    def test_get_media_type_other(self):
        path = self.image_path
        self.assertEqual(self.manifest.get_media_type(path), 'image/png')


    def test_get_media_type_missing(self):
        self.assert_(self.manifest.get_media_type('LpOD') is None)


    def test_set_media_type(self):
        manifest = self.manifest.clone()
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), 'image/png')
        manifest.set_media_type(path, 'image/jpeg')
        self.assertEqual(manifest.get_media_type(path), 'image/jpeg')


    def test_set_media_type_missing(self):
        manifest = self.manifest.clone()
        self.assertRaises(KeyError, manifest.set_media_type, 'LpOD', '')


    def test_add_full_path(self):
        manifest = self.manifest.clone()
        self.assert_(manifest.get_media_type('LpOD') is None)
        manifest.add_full_path('LpOD', '')
        self.assertEqual(manifest.get_media_type('LpOD'), '')


    def test_add_full_path_existing(self):
        manifest = self.manifest.clone()
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), 'image/png')
        manifest.add_full_path(path, 'image/jpeg')
        self.assertEqual(manifest.get_media_type(path), 'image/jpeg')


    def test_del_full_path(self):
        manifest = self.manifest.clone()
        path = self.image_path
        self.assertEqual(manifest.get_media_type(path), 'image/png')
        manifest.del_full_path(path)
        self.assert_(manifest.get_media_type(path) is None)



if __name__ == '__main__':
    main()
