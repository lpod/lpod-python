# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from lpod.section import odf_create_section


class TestSection(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.body = document.get_body()


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
        body = self.body
        sections = body.get_sections()
        self.assertEqual(len(sections), 2)
        second = sections[1]
        name = second.get_attribute('text:name')
        self.assertEqual(name, "Section2")


    def test_get_section_list_style(self):
        body = self.body
        sections = body.get_sections(style='Sect1')
        self.assertEqual(len(sections), 2)
        section = sections[0]
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section1")


    def test_get_section(self):
        body = self.body
        section = body.get_section(position=1)
        name = section.get_attribute('text:name')
        self.assertEqual(name, "Section2")



if __name__ == '__main__':
    main()
