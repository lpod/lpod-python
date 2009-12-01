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
from lpod.span import odf_create_span


class TestSpan(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/span_style.odt')
        self.body = document.get_body()


    def test_create_span(self):
        span = odf_create_span(u'my text', style='my_style')
        expected = ('<text:span text:style-name="my_style">'
                      'my text'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_get_span_list(self):
        body = self.body
        result = body.get_span_list()
        self.assertEqual(len(result), 2)
        element = result[0]
        expected = ('<text:span text:style-name="T1">'
                      'moustache'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span_list_style(self):
        body = self.body
        result = body.get_span_list(style='T2')
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span(self):
        body = self.body
        span = body.get_span_by_position(2)
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_insert_span(self):
        body = self.body.clone()
        span = odf_create_span('my_style', u'my text')
        paragraph = body.get_paragraph_by_position(1)
        paragraph.append_element(span)



if __name__ == '__main__':
    main()
