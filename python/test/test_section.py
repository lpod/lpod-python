# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.section import odf_create_section


class TestSection(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_simple_section(self):
        """The idea is to test only with the mandatory arguments (none
        in this case), not to test odf_create_element which is done in
        test_xmlpart.
        """
        element = odf_create_section()
        excepted = '<text:section/>'
        self.assertEqual(element.serialize(), excepted)


    def test_create_complex_section(self):
        """The idea is to test with all possible arguments. If some arguments
        are contradictory or trigger different behaviours, test all those
        combinations separately.
        """
        element = odf_create_section(style='Standard')
        excepted = '<text:section text:style-name="Standard"/>'
        self.assertEqual(element.serialize(), excepted)


    def test_get_section_list(self):
        content = self.content
        sections = content.get_section_list()
        self.assertEqual(len(sections), 2)
        second = sections[1]
        name = second.get_attribute('text:name')
        self.assertEqual(name, "Section2")


    def test_get_section_list_style(self):
        content = self.content
        sections = content.get_section_list(style='Sect1')
        self.assertEqual(len(sections), 2)
        section = sections[0]
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section1")


    def test_get_section(self):
        content = self.content
        section = content.get_section_by_position(2)
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section2")



if __name__ == '__main__':
    main()
