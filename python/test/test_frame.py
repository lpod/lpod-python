# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_frame


class TestFrame(TestCase):

    def setUp(self):
        document = odf_get_document('samples/frame_image.odp').clone()
        self.content = document.get_xmlpart('content')


    def test_create_frame1(self):
        frame1 = odf_create_frame(u"A Frame", size=('10cm', '10cm'),
                                  style='Graphics')
        expected = ('<draw:frame draw:name="A Frame" svg:width="10cm" '
                    'svg:height="10cm" text:anchor-type="paragraph" '
                    'draw:style-name="Graphics"/>')
        self.assertEqual(frame1.serialize(), expected)


    def test_create_frame2(self):
        frame2 = odf_create_frame(u"Another Frame", size=('10cm', '10cm'),
                                  anchor_type='page', page_number=1,
                                  position=('10mm', '10mm'), style='Graphics')
        expected = ('<draw:frame draw:name="Another Frame" svg:width="10cm" '
                      'svg:height="10cm" text:anchor-type="page" '
                      'text:anchor-page-number="1" svg:x="10mm" '
                      'svg:y="10mm" draw:style-name="Graphics"/>')
        self.assertEqual(frame2.serialize(), expected)


    def test_get_frame_list(self):
        content = self.content
        result = content.get_frame_list()
        self.assertEqual(len(result), 2)


    def test_get_frame_list_title(self):
        content = self.content
        result = content.get_frame_list(title=u"Intitulé")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get_name(), 'draw:frame')


    def test_get_frame_by_name(self):
        content = self.content
        frame = content.get_frame_by_name(u"Logo")
        self.assertEqual(frame.get_name(), 'draw:frame')


    def test_get_frame_by_position(self):
        content = self.content
        frame = content.get_frame_by_position(2)
        self.assertEqual(frame.get_attribute('presentation:class'), u'notes')


    def test_get_frame_by_description(self):
        content = self.content
        element = content.get_frame_by_description(u"描述")
        self.assertEqual(element.get_name(), 'draw:frame')


    def test_insert_frame(self):
        clone = self.content.clone()
        frame1 = odf_create_frame(u"frame1", size=('10cm', '10cm'),
                                  style='Graphics')
        frame2 = odf_create_frame(u"frame2", size=('10cm', '10cm'),
                                  page_number=1, position=('10mm', '10mm'),
                                  style='Graphics')
        body = clone.get_body()
        body.append_element(frame1)
        body.append_element(frame2)
        result = clone.get_frame_list(style='Graphics')
        self.assertEqual(len(result), 2)
        element = clone.get_frame_by_name(u"frame1")
        self.assertEqual(element.get_name(), 'draw:frame')
        element = clone.get_frame_by_name(u"frame2")
        self.assertEqual(element.get_name(), 'draw:frame')



if __name__ == '__main__':
    main()
