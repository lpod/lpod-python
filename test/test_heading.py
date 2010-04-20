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
from lpod.heading import odf_create_heading, odf_heading


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
        headings = body.get_heading_list(outline_level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_style_level(self):
        body = self.body
        headings = body.get_heading_list(style='Heading_20_2', outline_level=2)
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_list_context(self):
        body = self.body
        section2 = body.get_section_by_position(1)
        headings = section2.get_heading_list()
        self.assertEqual(len(headings), 1)
        heading = headings[0]
        text = heading.get_text()
        self.assertEqual(text, u"First Title of the Second Section");


    def test_odf_heading(self):
        body = self.body
        heading = body.get_heading_by_position(0)
        self.assert_(isinstance(heading, odf_heading))


    def test_get_heading(self):
        body = self.body
        heading = body.get_heading_by_position(1)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_get_heading_level(self):
        body = self.body
        heading = body.get_heading_by_position(0, outline_level=2)
        text = heading.get_text()
        self.assertEqual(text, u'Level 2 Title')


    def test_insert_heading(self):
        body = self.body.clone()
        heading = odf_create_heading(2, u'An inserted heading',
                                     style='Heading_20_2')
        body.append_element(heading)
        last_heading = body.get_heading_list()[-1]
        self.assertEqual(last_heading.get_text(), u'An inserted heading')



if __name__ == '__main__':
    main()
