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
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_heading_list(self):
        content = self.content
        headings = content.get_heading_list()
        self.assertEqual(len(headings), 3)
        second = headings[1]
        text = second.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style(self):
        content = self.content
        headings = content.get_heading_list(style='Heading_20_2')
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_level(self):
        content = self.content
        headings = content.get_heading_list(level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style_level(self):
        content = self.content
        headings = content.get_heading_list(style='Heading_20_2', level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_context(self):
        content = self.content
        section2 = content.get_section_by_position(2)
        headings = content.get_heading_list(context=section2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_odf_heading(self):
        content = self.content
        heading = content.get_heading_by_position(1)
        self.assert_(isinstance(heading, odf_heading))


    def test_get_heading(self):
        content = self.content
        heading = content.get_heading_by_position(2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        content = self.content
        heading = content.get_heading_by_position(1, level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        content = self.content
        clone = content.clone()
        heading = odf_create_heading(2, u'An inserted heading',
                                     style='Heading_20_2')
        body = clone.get_body()
        body.insert_element(heading, LAST_CHILD)
        last_heading = clone.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



if __name__ == '__main__':
    main()
