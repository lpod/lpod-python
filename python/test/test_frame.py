# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.frame import odf_create_frame, odf_create_image_frame
from lpod.frame import odf_create_text_frame, odf_frame
from lpod.heading import odf_create_heading


class TestFrame(TestCase):

    def setUp(self):
        document = odf_get_document('samples/frame_image.odp')
        self.body = document.get_body()


    def test_create_frame(self):
        frame = odf_create_frame(u"A Frame", size=('10cm', '10cm'),
                                 style='Graphics')
        expected = ('<draw:frame svg:width="10cm" svg:height="10cm" '
                      'text:anchor-type="paragraph" '
                      'draw:name="A Frame" draw:style-name="Graphics"/>')
        self.assertEqual(frame.serialize(), expected)


    def test_create_frame_page(self):
        frame = odf_create_frame(u"Another Frame", size=('10cm', '10cm'),
                                 anchor_type='page', page_number=1,
                                 position=('10mm', '10mm'), style='Graphics')
        expected = ('<draw:frame svg:width="10cm" svg:height="10cm" '
                      'text:anchor-type="page" draw:name="Another Frame" '
                      'text:anchor-page-number="1" svg:x="10mm" '
                      'svg:y="10mm" draw:style-name="Graphics"/>')
        self.assertEqual(frame.serialize(), expected)


    def test_get_frame_list(self):
        body = self.body
        result = body.get_frame_list()
        self.assertEqual(len(result), 4)


    def test_get_frame_list_title(self):
        body = self.body
        result = body.get_frame_list(title=u"Intitulé")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get_tagname(), 'draw:frame')


    def test_get_frame_by_name(self):
        body = self.body
        frame = body.get_frame_by_name(u"Logo")
        self.assertEqual(frame.get_tagname(), 'draw:frame')


    def test_get_frame_by_position(self):
        body = self.body
        frame = body.get_frame_by_position(4)
        self.assertEqual(frame.get_attribute('presentation:class'), u'notes')


    def test_get_frame_by_description(self):
        body = self.body
        frame = body.get_frame_by_description(u"描述")
        self.assertEqual(frame.get_tagname(), 'draw:frame')


    def test_insert_frame(self):
        body = self.body.clone()
        frame1 = odf_create_frame(u"frame1", size=('10cm', '10cm'),
                                  style='Graphics')
        frame2 = odf_create_frame(u"frame2", size=('10cm', '10cm'),
                                  page_number=1, position=('10mm', '10mm'),
                                  style='Graphics')
        body.append_element(frame1)
        body.append_element(frame2)
        result = body.get_frame_list(style='Graphics')
        self.assertEqual(len(result), 2)
        element = body.get_frame_by_name(u"frame1")
        self.assertEqual(element.get_tagname(), 'draw:frame')
        element = body.get_frame_by_name(u"frame2")
        self.assertEqual(element.get_tagname(), 'draw:frame')



class TestImageFrame(TestCase):

    def test_create_image_frame(self):
        frame = odf_create_image_frame('Pictures/zoe.jpg')
        expected = ('<draw:frame svg:width="1cm" svg:height="1cm" '
                      'text:anchor-type="paragraph">'
                      '<draw:image xlink:href="Pictures/zoe.jpg"/>'
                    '</draw:frame>')
        self.assertEqual(frame.serialize(), expected)


    def test_create_image_frame_text(self):
        frame = odf_create_image_frame('Pictures/zoe.jpg',
                                         text=u"Zoé")
        expected = ('<draw:frame svg:width="1cm" svg:height="1cm" '
                      'text:anchor-type="paragraph">'
                      '<draw:image xlink:href="Pictures/zoe.jpg">'
                        '<text:p>Zo&#233;</text:p>'
                      '</draw:image>'
                    '</draw:frame>')
        self.assertEqual(frame.serialize(), expected)


class TestTextFrame(TestCase):

    def test_create_text_frame(self):
        frame = odf_create_text_frame(u"Zoé")
        expected = ('<draw:frame svg:width="1cm" svg:height="1cm" '
                      'text:anchor-type="paragraph">'
                      '<draw:text-box>'
                        '<text:p>Zo&#233;</text:p>'
                      '</draw:text-box>'
                    '</draw:frame>')
        self.assertEqual(frame.serialize(), expected)


    def test_create_text_frame_element(self):
        heading = odf_create_heading(1, u"Zoé")
        frame = odf_create_text_frame(heading)
        expected = ('<draw:frame svg:width="1cm" svg:height="1cm" '
                      'text:anchor-type="paragraph">'
                      '<draw:text-box>'
                        '<text:h text:outline-level="1">Zo&#233;</text:h>'
                      '</draw:text-box>'
                    '</draw:frame>')
        self.assertEqual(frame.serialize(), expected)



class TestOdfFrame(TestCase):

    def setUp(self):
        document = odf_get_document('samples/frame_image.odp')
        self.body = document.get_body()
        self.size = size = ('1cm', '2mm')
        self.position = position = ('3in', '4pt')
        self.frame = odf_create_frame(size=size, position=position)


    def test_get_frame(self):
        body = self.body
        frame = body.get_frame_by_position(1)
        self.assert_(isinstance(frame, odf_frame))


    def test_get_size(self):
        self.assertEqual(self.frame.get_size(), self.size)


    def test_set_size(self):
        frame = self.frame.clone()
        frame.set_size(self.position)
        self.assertEqual(frame.get_size(), self.position)


    def test_get_position(self):
        self.assertEqual(self.frame.get_position(), self.position)


    def test_set_position(self):
        frame = self.frame.clone()
        frame.set_position(self.size)
        self.assertEqual(frame.get_position(), self.size)



if __name__ == '__main__':
    main()
