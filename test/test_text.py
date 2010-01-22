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
from lpod.element import odf_text, odf_create_element


class TextTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.results = element.xpath('descendant::text()')


    def test_nodes(self):
        self.assertEqual(len(self.results), 2)


    def test_type(self):
        self.assert_(type(self.results[0]) is odf_text)


    def test_text(self):
        text = self.results[0]
        self.assertEqual(text, u"text")
        self.assert_(text.is_text() is True)
        self.assert_(text.is_tail() is False)


    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail, u"tail")
        self.assert_(tail.is_text() is False)
        self.assert_(tail.is_tail() is True)



class ParentTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.results = element.xpath('descendant::text()')

    def test_text(self):
        text = self.results[0]
        self.assertEqual(text.get_parent().get_tagname(), 'text:p')


    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail.get_parent().get_tagname(), 'text:span')



if __name__ == '__main__':
    main()
