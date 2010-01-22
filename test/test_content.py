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


class ContentTestCase(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_text.odt')


    def tearDown(self):
        del self.document


    def test_get_body(self):
        body = self.document.get_body()
        expected = ('<office:text>\n'
                    '   <text:sequence-decls>\n'
                    '    <text:sequence-decl text:display-outline-level="0" '
                    'text:name="Illustration"/>\n'
                    '    <text:sequence-decl text:display-outline-level="0" '
                    'text:name="Table"/>\n'
                    '    <text:sequence-decl text:display-outline-level="0" '
                    'text:name="Text"/>\n'
                    '    <text:sequence-decl text:display-outline-level="0" '
                    'text:name="Drawing"/>\n'
                    '   </text:sequence-decls>\n'
                    '   <text:section text:style-name="Sect1" '
                    'text:name="Section1">\n'
                    '    <text:h text:style-name="Heading_20_1" '
                    'text:outline-level="1">LpOD Test Case Document</text:h>\n'
                    '    <text:p text:style-name="Text_20_body">This is the '
                    'first paragraph.</text:p>\n'
                    '    <text:p text:style-name="Text_20_body">This is the '
                    'second paragraph.</text:p>\n'
                    '    <text:p text:style-name="Hanging_20_indent">This is '
                    'a paragraph with a named style.</text:p>\n'
                    '    <text:h text:style-name="Heading_20_2" '
                    'text:outline-level="2">Level 2 Title</text:h>\n'
                    '    <text:p text:style-name="Text_20_body">This is the '
                    'first paragraph of the second title.</text:p>\n'
                    '    <text:p text:style-name="Text_20_body">This is the '
                    'last paragraph with diacritical signs: '
                    '&#233;&#232;</text:p>\n'
                    '   </text:section>\n'
                    '   <text:section text:style-name="Sect1" '
                    'text:name="Section2">\n'
                    '    <text:h text:style-name="Heading_20_1" '
                    'text:outline-level="1" text:restart-numbering="true" '
                    'text:start-value="-1">First Title of the '
                    'Second Section</text:h>\n'
                    '    <text:p text:style-name="Text_20_body">First '
                    'paragraph of the second section.</text:p>\n'
                    '    <text:p text:style-name="Text_20_body">This is '
                    'the second paragraph with <text:a xlink:type="simple" '
                    'xlink:href="http://lpod-project.org/" office:name="Link '
                    'to the lpod project">an external link</text:a> inside.'
                    '</text:p>\n'
                    '   </text:section>\n'
                    '  </office:text>\n')
        self.assertEqual(body.serialize(pretty=True), expected)



if __name__ == '__main__':
    main()
