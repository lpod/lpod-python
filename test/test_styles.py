# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from lpod.const import ODF_STYLES
from lpod.document import odf_get_document
from lpod.style import odf_create_style



class TestStyle(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odt')
        self.styles = document.get_part(ODF_STYLES)


    def tearDown(self):
        del self.styles
        del self.document


    def test_create_style(self):
        style = odf_create_style('paragraph', 'style1')
        expected = ('<style:style style:name="style1" '
                      'style:family="paragraph"/>')
        self.assertEqual(style.serialize(), expected)


    def test_get_styles(self):
        style_list = self.styles.get_styles()
        self.assertEqual(len(style_list), 22)


    def test_get_styles_paragraph(self):
        style_list = self.styles.get_styles(family='paragraph')
        self.assertEqual(len(style_list), 10)


    def test_get_styles_master_page(self):
        style_list = self.styles.get_styles(family='master-page')
        self.assertEqual(len(style_list), 1)


    def test_get_style_automatic(self):
        style = self.styles.get_style('page-layout', u'Mpm1')
        self.assertNotEqual(style, None)


    def test_get_style_named(self):
        style = self.styles.get_style('paragraph', u'Heading_20_1')
        self.assertEqual(style.get_display_name(), u"Heading 1")


    def test_get_style_display_name(self):
        style = self.styles.get_style('paragraph', display_name=u"Text body")
        self.assertEqual(style.get_name(), u"Text_20_body")


    def test_insert_style(self):
        styles = self.styles.clone()
        style = odf_create_style('paragraph', u'style1', area='text',
                                 **{'fo:color': '#0000ff',
                                    'fo:background-color': '#ff0000'})
        context = styles.get_element('//office:styles')
        context.append(style)

        expected = ('<style:style style:name="style1" '
                                  'style:family="paragraph">\n'
                    '  <style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>\n'
                    '</style:style>\n')
        get1 = styles.get_style('paragraph', u'style1')
        self.assertEqual(get1.serialize(pretty=True), expected)



class TestInsertStyleCase(TestCase):

    def setUp(self):
        self.doc = odf_get_document('samples/example.odt')


    def test_insert_common_style(self):
        doc = self.doc

        style = odf_create_style('paragraph', u'MyStyle')
        doc.insert_style(style)
        inserted_style = doc.get_style('paragraph', u'MyStyle')

        self.assertEqual(style.serialize(), inserted_style.serialize())


    def test_insert_default_style(self):
        doc = self.doc

        style = odf_create_style('paragraph', u'MyStyle')
        doc.insert_style(style, default=True)

        inserted_style = doc.get_style('paragraph')
        expected = '<style:default-style style:family="paragraph"/>'

        self.assertEqual(inserted_style.serialize(), expected)


    def test_insert_automatic_style(self):
        doc = self.doc

        style = odf_create_style('paragraph')
        doc.insert_style(style, automatic=True)
        self.assertNotEqual(style.get_name(), None)


    def test_insert_with_error(self):
        doc = self.doc

        style = odf_create_style('paragraph', u'MyStyle')
        self.assertRaises(AttributeError, doc.insert_style,
                          style=style, automatic=True, default=True)


    def test_insert_master_page_style(self):
        doc = self.doc

        style = odf_create_style('master-page', u'MyPageStyle')
        doc.insert_style(style)

        inserted_style = doc.get_style('master-page',  u'MyPageStyle')
        self.assertEqual(style.serialize(), inserted_style.serialize())



if __name__ == '__main__':
    main()
