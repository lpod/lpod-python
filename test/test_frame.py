# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
                      'text:anchor-type="page" text:anchor-page-number="1" '
                      'draw:name="Another Frame" svg:x="10mm" '
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
        self.assertEqual(result[0].get_tag(), 'draw:frame')


    def test_get_frame_by_name(self):
        body = self.body
        frame = body.get_frame(name=u"Logo")
        self.assertEqual(frame.get_tag(), 'draw:frame')


    def test_get_frame_by_position(self):
        body = self.body
        frame = body.get_frame(position=3)
        self.assertEqual(frame.get_attribute('presentation:class'), u'notes')


    def test_get_frame_by_description(self):
        body = self.body
        frame = body.get_frame(description=u"描述")
        self.assertEqual(frame.get_tag(), 'draw:frame')


    def test_insert_frame(self):
        body = self.body.clone()
        frame1 = odf_create_frame(u"frame1", size=('10cm', '10cm'),
                                  style='Graphics')
        frame2 = odf_create_frame(u"frame2", size=('10cm', '10cm'),
                                  page_number=1, position=('10mm', '10mm'),
                                  style='Graphics')
        body.append(frame1)
        body.append(frame2)
        result = body.get_frame_list(style='Graphics')
        self.assertEqual(len(result), 2)
        element = body.get_frame(name=u"frame1")
        self.assertEqual(element.get_tag(), 'draw:frame')
        element = body.get_frame(name=u"frame2")
        self.assertEqual(element.get_tag(), 'draw:frame')



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
        frame = body.get_frame()
        self.assert_(isinstance(frame, odf_frame))


    def test_get_frame_size(self):
        self.assertEqual(self.frame.get_size(), self.size)


    def test_set_size(self):
        frame = self.frame.clone()
        frame.set_size(self.position)
        self.assertEqual(frame.get_size(), self.position)


    def test_get_frame_position(self):
        self.assertEqual(self.frame.get_position(), self.position)


    def test_set_frame_position(self):
        frame = self.frame.clone()
        frame.set_position(self.size)
        self.assertEqual(frame.get_position(), self.size)


    def test_get_frame_anchor_type(self):
        self.assertEqual(self.frame.get_anchor_type(), 'paragraph')


    def test_set_frame_anchor_type(self):
        frame = self.frame.clone()
        self.assertEqual(frame.get_page_number(), None)
        frame.set_anchor_type('page', 3)
        self.assertEqual(frame.get_anchor_type(), 'page')
        self.assertEqual(frame.get_page_number(), 3)



if __name__ == '__main__':
    main()
