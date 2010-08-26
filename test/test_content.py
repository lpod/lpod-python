# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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
from lpod.content import odf_content


class ContentTestCase(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')
        self.content = document.get_part('content')


    def test_get_content(self):
        self.assert_(type(self.content) is odf_content)


    def test_get_body(self):
        body = self.content.get_body()
        self.assertEqual(body.get_tag(), 'office:text')


    def test_get_style_list(self):
        result = self.content.get_styles()
        self.assertEqual(len(result), 4)


    def test_get_style_list_family(self):
        result = self.content.get_styles('font-face')
        self.assertEqual(len(result), 3)


    def test_get_style(self):
        style = self.content.get_style('section', u"Sect1")
        self.assertEqual(style.get_name(), u"Sect1")
        self.assertEqual(style.get_family(), 'section')



if __name__ == '__main__':
    main()
