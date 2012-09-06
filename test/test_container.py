# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
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
import os
from cStringIO import StringIO
from ftplib import FTP
from os import mkdir
from shutil import rmtree
from unittest import TestCase, main
from urllib import urlopen

# Import from lpod
from lpod.const import ODF_EXTENSIONS, ODF_CONTENT, ODF_META
from lpod.container import odf_get_container, odf_new_container


class NewContainerFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(IOError, odf_new_container,
                '../templates/notexisting')

    def test_text_template(self):
        path = '../templates/text.ott'
        container = odf_new_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_spreadsheet_template(self):
        path = '../templates/spreadsheet.ots'
        container = odf_new_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['ods'])


    def test_presentation_template(self):
        path = '../templates/presentation.otp'
        container = odf_new_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odp'])


    def test_drawing_template(self):
        path = '../templates/drawing.otg'
        container = odf_new_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odg'])



class NewContainerFromTypeTestCase(TestCase):

    def test_bad_type(self):
        self.assertRaises(IOError, odf_new_container, 'foobar')


    def test_text_type(self):
        container = odf_new_container('text')
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_spreadsheet_type(self):
        container = odf_new_container('spreadsheet')
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['ods'])


    def test_presentation_type(self):
        container = odf_new_container('presentation')
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odp'])


    def test_drawing_type(self):
        container = odf_new_container('drawing')
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odg'])



class GetContainerTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        container = odf_get_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_odf_xml(self):
        path = 'samples/example.xml'
        container = odf_get_container(path)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])



class ContainerTestCase(TestCase):

    def test_clone(self):
        container = odf_new_container('text')
        clone = container.clone()
        self.assertEqual(clone.path, None)
        self.assertNotEqual(clone._odf_container__data, None)


    def test_get_part_xml(self):
        container = odf_get_container('samples/example.odt')
        content = container.get_part(ODF_CONTENT)
        self.assert_('<office:document-content' in content)


    def test_get_part_mimetype(self):
        container = odf_get_container('samples/example.odt')
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_odf_xml_bad_part(self):
        container = odf_get_container('samples/example.xml')
        self.assertRaises(ValueError, container.get_part, 'Pictures/a.jpg')


    def test_odf_xml_part_xml(self):
        container = odf_get_container('samples/example.xml')
        meta = container.get_part('meta')
        self.assert_(meta.startswith('<office:document-meta>'))


    def test_set_part(self):
        container = odf_get_container('samples/example.odt')
        path = 'Pictures/a.jpg'
        data = 'JFIFIThinkImAnImage'
        container.set_part(path, data)
        self.assertEqual(container.get_part(path), data)


    def test_del_part(self):
        container = odf_get_container('samples/example.odt')
        # Not a realistic test
        path = 'content'
        container.del_part(path)
        self.assertRaises(ValueError, container.get_part, path)



class ContainerSaveTestCase(TestCase):

    def setUp(self):
        mkdir('trash')


    def tearDown(self):
        rmtree('trash')


    def test_save_zip(self):
        """TODO: 2 cases
           1. from "zip" to "zip"
           2. from "flat" to "zip"
        """
        container = odf_get_container('samples/example.odt')
        container.save('trash/example.odt')
        new_container = odf_get_container('trash/example.odt')
        mimetype = new_container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_save_folder(self):
        container = odf_get_container('samples/example.odt')
        container.save('trash/example.odt', packaging='folder')
        path = os.path.join('trash', 'example.odt' + '.folder', 'mimetype')
        self.assertEqual(os.path.isfile(path), True)
        path = os.path.join('trash', 'example.odt' + '.folder', 'content.xml')
        self.assertEqual(os.path.isfile(path), True)
        path = os.path.join('trash', 'example.odt' + '.folder', 'meta.xml')
        self.assertEqual(os.path.isfile(path), True)
        path = os.path.join('trash', 'example.odt' + '.folder', 'styles.xml')
        self.assertEqual(os.path.isfile(path), True)
        path = os.path.join('trash', 'example.odt' + '.folder', 'settings.xml')
        self.assertEqual(os.path.isfile(path), True)


    def test_save_folder_to_zip(self):
        container = odf_get_container('samples/example.odt')
        container.save('trash/example.odt', packaging='folder')
        path = os.path.join('trash', 'example.odt' + '.folder', 'mimetype')
        self.assertEqual(os.path.isfile(path), True)
        new_container = odf_get_container('trash/example.odt.folder')
        new_container.save('trash/example_bis.odt', packaging='zip')
        new_container_zip = odf_get_container('trash/example_bis.odt')
        mimetype = new_container_zip.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_load_folder(self):
        container = odf_get_container('samples/example.odt')
        container.save('trash/example_f.odt', packaging='folder')
        new_container = odf_get_container('trash/example_f.odt.folder')
        content = new_container.get_part(ODF_CONTENT)
        self.assert_('<office:document-content' in content)
        mimetype = new_container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])
        path = 'Pictures/a.jpg'
        data = 'JFIFIThinkImAnImage'
        new_container.set_part(path, data)
        self.assertEqual(new_container.get_part(path), data)
        # Not a realistic test
        path = 'content'
        new_container.del_part(path)
        self.assertRaises(ValueError, new_container.get_part, path)



    # XXX We must implement the flat xml part
    def xtest_save_flat(self):
        """TODO: 2 cases
           1. from "zip" to "flat"
           2. from "flat" to "flat"
        """
        raise NotImplementedError



if __name__ == '__main__':
    main()
