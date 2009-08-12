# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_frame, odf_create_image
from lpod.xmlpart import LAST_CHILD, NEXT_SIBLING


class TestImage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/frame_image.odp')
        self.content = document.get_xmlpart('content')
        self.path = 'Pictures/10000000000001D40000003C8B3889D9.png'


    def tearDown(self):
        del self.content
        del self.document


    def test_create_image(self):
        image = odf_create_image(self.path)
        expected = '<draw:image xlink:href="%s"/>' % self.path
        self.assertEqual(image.serialize(), expected)


    def test_get_image_list(self):
        content = self.content
        result = content.get_image_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_get_image_name(self):
        content = self.content
        element = content.get_image_by_name(u"Logo")
        # Searched by frame but got the inner image with no name
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_get_image_position(self):
        content = self.content
        element = content.get_image_by_position(1)
        self.assertEqual(element.get_attribute('xlink:href'), self.path)


    def test_insert_image(self):
        clone = self.content.clone()
        path = 'a/path'
        image = odf_create_image(path)
        frame = odf_create_frame(u"Image Frame", size=('0cm', '0cm'),
                                 style='Graphics')
        frame.insert_element(image, LAST_CHILD)
        clone.get_frame_by_position(1).insert_element(frame, NEXT_SIBLING)
        element = clone.get_image_by_name(u"Image Frame")
        self.assertEqual(element.get_attribute('xlink:href'), path)
        element = clone.get_image_by_position(2)
        self.assertEqual(element.get_attribute('xlink:href'), path)



if __name__ == '__main__':
    main()
