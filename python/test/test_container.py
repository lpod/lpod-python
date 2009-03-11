# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from itools
from itools import vfs

# Import from lpod
from lpod.container import ODF_EXTENSIONS
from lpod.container import odf_new_container_from_template
from lpod.container import odf_new_container_from_class
from lpod.container import odf_get_container


class NewContainerFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(ValueError, odf_new_container_from_template,
                          '../templates/notexisting')

    def test_text_template(self):
        uri = '../templates/text.ott'
        self.assert_(odf_new_container_from_template(uri))


    def test_spreadsheet_template(self):
        uri = '../templates/spreadsheet.ots'
        self.assert_(odf_new_container_from_template(uri))


    def test_presentation_template(self):
        uri = '../templates/presentation.otp'
        self.assert_(odf_new_container_from_template(uri))


    def test_drawing_template(self):
        uri = '../templates/drawing.otg'
        self.assert_(odf_new_container_from_template(uri))



class NewContainerFromClassTestCase(TestCase):

    def test_bad_class(self):
        self.assertRaises(ValueError, odf_new_container_from_class,
                          'foobar')


    def test_text_class(self):
        self.assert_(odf_new_container_from_class('text'))


    def test_spreadsheet_class(self):
        self.assert_(odf_new_container_from_class('spreadsheet'))


    def test_presentation_class(self):
        self.assert_(odf_new_container_from_class('presentation'))


    def test_drawing_class(self):
        self.assert_(odf_new_container_from_class('drawing'))



class GetContainerTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        self.assert_(odf_get_container(path))


    def test_odf_xml(self):
        path = 'samples/example.xml'
        self.assert_(odf_get_container(path))


    def test_http(self):
        uri = 'http://test.lpod-project.org/example.odt'
        self.assert_(odf_get_container(uri))


    def test_ftp(self):
        uri = 'ftp://test.lpod-project.org/example.odt'
        self.assert_(odf_get_container(uri))



class ContainerTestCase(TestCase):

    def test_clone(self):
        container = odf_new_container_from_class('text')
        clone = container.clone()
        self.assertEqual(clone.uri, None)


    def test_get_part_xml(self):
        container = odf_get_container('samples/example.odt')
        content = container.get_part('content')
        xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
        self.assert_(content.startswith(xml_decl))


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
        vfs.make_folder('trash')


    def tearDown(self):
        vfs.remove('trash')


    def test_save_zip(self):
        """TODO: 2 cases
           1. from "zip" to "zip"
           2. from "flat" to "zip"
        """
        container = odf_get_container('samples/example.odt')
        container.save('trash/example.odt')
        # TODO FINISH ME


    def test_save_flat(self):
        """TODO: 2 cases
           1. from "zip" to "flat"
           2. from "flat" to "flat"
        """
        raise NotImplementedError



if __name__ == '__main__':
    main()
