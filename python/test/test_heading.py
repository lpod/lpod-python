# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.heading import odf_create_heading, odf_heading
from lpod.xmlpart import LAST_CHILD


class TestHeading(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.body = document.get_body()


    def test_get_heading_list(self):
        body = self.body
        headings = body.get_heading_list()
        self.assertEqual(len(headings), 3)
        second = headings[1]
        text = second.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style(self):
        body = self.body
        headings = body.get_heading_list(style='Heading_20_2')
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_level(self):
        body = self.body
        headings = body.get_heading_list(level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style_level(self):
        body = self.body
        headings = body.get_heading_list(style='Heading_20_2', level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_context(self):
        body = self.body
        section2 = body.get_section_by_position(2)
        headings = section2.get_heading_list()
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_odf_heading(self):
        body = self.body
        heading = body.get_heading_by_position(1)
        self.assert_(isinstance(heading, odf_heading))


    def test_get_heading(self):
        body = self.body
        heading = body.get_heading_by_position(2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        body = self.body
        heading = body.get_heading_by_position(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        body = self.body.clone()
        heading = odf_create_heading(2, u'An inserted heading',
                                     style='Heading_20_2')
        body.insert_element(heading, LAST_CHILD)
        last_heading = body.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



if __name__ == '__main__':
    main()
