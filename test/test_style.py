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
from lpod.const import ODF_CONTENT
from lpod.container import odf_get_container
from lpod.document import odf_get_document
from lpod.style import odf_create_style, odf_style
from lpod.style import odf_list_level_style_number
from lpod.xmlpart import odf_xmlpart


class TestCreateStyle(TestCase):

    def test_create_style_paragraph(self):
        style = odf_create_style('paragraph', 'style1')
        expected = ('<style:style style:name="style1" '
                      'style:family="paragraph"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_text(self):
        style = odf_create_style('text')
        expected = ('<style:style style:family="text"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_graphic(self):
        style = odf_create_style('graphic')
        expected = ('<style:style style:family="graphic"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_table(self):
        style = odf_create_style('table')
        expected = ('<style:style style:family="table"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_table_column(self):
        style = odf_create_style('table-column')
        expected = ('<style:style style:family="table-column"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_table_row(self):
        style = odf_create_style('table-row')
        expected = ('<style:style style:family="table-row"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_table_cell(self):
        style = odf_create_style('table-cell')
        expected = ('<style:style style:family="table-cell"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_section(self):
        style = odf_create_style('section')
        expected = ('<style:style style:family="section"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_list(self):
        style = odf_create_style('list')
        expected = ('<text:list-style/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_outline(self):
        style = odf_create_style('outline')
        expected = ('<text:outline-style/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_page_layout(self):
        style = odf_create_style('page-layout')
        expected = ('<style:page-layout/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_master_page(self):
        style = odf_create_style('master-page')
        expected = ('<style:master-page/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_display_name(self):
        style = odf_create_style('paragraph', display_name=u"Heading 1")
        expected = ('<style:style style:family="paragraph" '
                    'style:display-name="Heading 1"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_parent(self):
        style = odf_create_style('paragraph', parent=u"Heading 1")
        expected = ('<style:style style:family="paragraph" '
                    'style:parent-style-name="Heading 1"/>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_properties(self):
        style = odf_create_style('paragraph', **{'fo:margin-top': "0cm"})
        expected = ('<style:style style:family="paragraph">'
                      '<style:paragraph-properties fo:margin-top="0cm"/>'
                    '</style:style>')
        self.assertEqual(style.serialize(), expected)


    def test_create_style_properties_shorcut(self):
        style = odf_create_style('paragraph', area='text', color='#ff0000')
        expected = ('<style:style style:family="paragraph">'
                      '<style:text-properties fo:color="#ff0000"/>'
                    '</style:style>')
        self.assertEqual(style.serialize(), expected)



class TestStyle(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/span_style.odt')
        self.content = document.get_part(ODF_CONTENT)


    def test_get_style_list(self):
        content = self.content
        styles = content.get_styles()
        self.assertEqual(len(styles), 6)


    def test_get_style_list_family(self):
        content = self.content
        styles = content.get_styles(family='paragraph')
        self.assertEqual(len(styles), 1)


    def test_get_style_automatic(self):
        content = self.content
        style = content.get_style('paragraph', u'P1')
        self.assertNotEqual(style, None)


    def test_insert_style(self):
        content = self.content.clone()
        style = odf_create_style('paragraph', 'style1', area='text',
                **{'fo:color': '#0000ff',
                   'fo:background-color': '#ff0000'})
        auto_styles = content.get_element('//office:automatic-styles')
        auto_styles.append(style)
        expected = ('<style:style style:name="style1" '
                                 'style:family="paragraph">'
                      '<style:text-properties fo:color="#0000ff" '
                                             'fo:background-color="#ff0000"/>'
                    '</style:style>')
        get1 = content.get_style('paragraph', u'style1')
        self.assertEqual(get1.serialize(), expected)



class StylePropertiesTestCase(TestCase):

    def setUp(self):
        self.container = container = odf_get_container('samples/example.odt')
        self.content_part = content_part = odf_xmlpart(ODF_CONTENT, container)
        self.paragraph_element = content_part.get_element('//text:p[1]')
        query = '//style:style[@style:family="paragraph"][1]'
        self.style_element = content_part.get_element(query)


    def test_odf_style(self):
        style = self.style_element
        self.assert_(isinstance(style, odf_style))


    def test_get_style_properties(self):
        style = self.style_element
        properties = style.get_properties()
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 12)
        self.assertEqual(properties['fo:margin-left'], "0cm")


    def test_get_style_properties_area(self):
        style = self.style_element
        properties = style.get_properties(area='text')
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:hyphenate'], "false")


    def test_get_style_properties_bad_element(self):
        element = self.paragraph_element
        self.assertRaises(AttributeError, element.__getattribute__,
                          'get_properties')


    def test_get_style_properties_bad_area(self):
        style = self.style_element
        properties = style.get_properties(area='toto')
        self.assertEqual(properties, None)


    def test_set_style_properties(self):
        style = self.style_element.clone()
        style.set_properties({'fo:color': '#f00'})
        properties = style.get_properties()
        self.assertEqual(len(properties), 13)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_area(self):
        style = self.style_element.clone()
        style.set_properties({'fo:color': '#f00'}, area='text')
        properties = style.get_properties(area='text')
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_new_area(self):
        style = self.style_element.clone()
        properties = style.get_properties(area='toto')
        self.assertEqual(properties, None)
        style.set_properties({'fo:color': '#f00'}, area='toto')
        properties = style.get_properties(area='toto')
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_del_style_properties(self):
        style = self.style_element.clone()
        style.del_properties(['fo:margin-left'])
        properties = style.get_properties()
        self.assertEqual(len(properties), 11)
        self.assertRaises(KeyError, properties.__getitem__, 'fo:margin-left')


    def test_del_style_properties_bad_area(self):
        style = self.style_element
        self.assertRaises(ValueError, style.del_properties,
                          area='toto')



class StyleBackgroundTestCase(TestCase):

    def setUp(self):
        self.style = odf_create_style('paragraph')


    def test_bad_family(self):
        style = odf_create_style('master-page')
        self.assertRaises(TypeError, style.set_background)


    def test_color(self):
        style = self.style.clone()
        style.set_background(color='#abcdef')
        expected = ('<style:style style:family="paragraph">'
                      '<style:paragraph-properties '
                        'fo:background-color="#abcdef"/>'
                    '</style:style>')
        self.assertEqual(style.serialize(), expected)


    def test_image(self):
        style = self.style.clone()
        style.set_background(uri='Pictures/toto')
        expected = ('<style:style style:family="paragraph">'
                      '<style:paragraph-properties '
                        'fo:background-color="transparent">'
                        '<style:background-image '
                          'xlink:href="Pictures/toto" '
                          'style:position="center"/>'
                      '</style:paragraph-properties>'
                    '</style:style>')
        self.assertEqual(style.serialize(), expected)


    def test_image_full(self):
        style = self.style.clone()
        style.set_background(uri='Pictures/toto', position='top left',
                             repeat='no-repeat', opacity=50,
                             filter='myfilter')
        expected = ('<style:style style:family="paragraph">'
                      '<style:paragraph-properties '
                        'fo:background-color="transparent">'
                        '<style:background-image '
                          'xlink:href="Pictures/toto" '
                          'style:position="top left" '
                          'style:repeat="no-repeat" '
                          'draw:opacity="50" '
                          'style:filter-name="myfilter"/>'
                      '</style:paragraph-properties>'
                    '</style:style>')
        self.assertEqual(style.serialize(), expected)



class LevelStyleTestCase(TestCase):

    def setUp(self):
        self.style = odf_create_style('list')


    def test_get_level_style(self):
        level_style = self.style.get_level_style(1)
        self.assert_(level_style is None)


    def test_set_level_style(self):
        self.style.set_level_style(1, num_format='1')
        level_style = self.style.get_level_style(1)
        self.assert_(level_style is not None)


    def test_set_level_style_number_missing_format(self):
        self.assertRaises(ValueError, self.style.set_level_style, 1)


    def test_set_level_style_number(self):
        level_style = self.style.set_level_style(1, num_format='1')
        self.assert_(type(level_style) is odf_list_level_style_number)
        expected = ('<text:list-level-style-number '
                      'text:level="1" fo:num-format="1"/>')
        self.assertEqual(level_style.serialize(), expected)


    def test_set_level_style_bullet(self):
        level_style = self.style.set_level_style(2, bullet_char=u"·")
        self.assert_(type(level_style) is odf_style)
        expected = ('<text:list-level-style-bullet '
                      'text:level="2" text:bullet-char="&#183;"/>')
        self.assertEqual(level_style.serialize(), expected)


    def test_set_level_style_image(self):
        level_style = self.style.set_level_style(3, uri='bullet.png')
        self.assert_(type(level_style) is odf_style)
        expected = ('<text:list-level-style-image '
                      'text:level="3" xlink:href="bullet.png"/>')
        self.assertEqual(level_style.serialize(), expected)


    def test_set_level_style_full(self):
        level_style = self.style.set_level_style(3, num_format='1',
                prefix=u" ", suffix=u".", display_levels=3, start_value=2,
                style=u'MyList')
        expected = ('<text:list-level-style-number '
                      'text:level="3" fo:num-format="1" '
                      'style:num-prefix=" " style:num-suffix="." '
                      'text:display-levels="3" text:start-value="2" '
                      'text:style-name="MyList"/>')
        self.assertEqual(level_style.serialize(), expected)



    def test_set_level_style_clone(self):
        level_1 = self.style.set_level_style(1, num_format='1')
        level_2 = self.style.set_level_style(2, display_levels=2,
                                             clone=level_1)
        expected = ('<text:list-level-style-number '
                      'text:level="2" fo:num-format="1" '
                      'text:display-levels="2"/>')
        self.assertEqual(level_2.serialize(), expected)



class TableStyleTestCase(TestCase):

    def test_table_cell_border(self):
        style = odf_create_style('table-cell', border="0.002cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-cell"><style:table-cell-properties '
            'fo:border="0.002cm"/></style:style>'))


    def test_table_cell_border_border_left(self):
        style = odf_create_style('table-cell', border="0.002cm",
                border_left="0.002cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-cell"><style:table-cell-properties '
            'fo:border="0.002cm"/></style:style>'))


    def test_table_cell_border_top(self):
        style = odf_create_style('table-cell', border_top="0.002cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-cell"><style:table-cell-properties '
            'fo:border-top="0.002cm" fo:border-left="none" '
            'fo:border-right="none" fo:border-bottom="none"/>'
            '</style:style>'))


    def test_table_cell_border_all(self):
        style = odf_create_style('table-cell', border_top="0.001cm",
                border_right="0.002cm", border_bottom="0.003cm",
                border_left="0.004cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-cell"><style:table-cell-properties '
            'fo:border-top="0.001cm" fo:border-left="0.004cm" '
            'fo:border-right="0.002cm" fo:border-bottom="0.003cm"/>'
            '</style:style>'))


    def test_table_cell_shadow(self):
        style = odf_create_style('table-cell',
                shadow="#808080 0.176cm 0.176cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-cell"><style:table-cell-properties '
            'style:shadow="#808080 0.176cm 0.176cm"/></style:style>'))


    def test_table_row_height(self):
        style = odf_create_style('table-row', height="5cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-row"><style:table-row-properties '
            'style:row-height="5cm"/></style:style>'))


    def test_table_column_width(self):
        style = odf_create_style('table-column', width="5cm")
        self.assertEqual(style.serialize(), ('<style:style '
            'style:family="table-column"><style:table-column-properties '
            'style:column-width="5cm"/></style:style>'))



if __name__ == '__main__':
    main()
