# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.container import odf_get_container
from lpod.document import odf_get_document
from lpod.style import odf_create_style, odf_style
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
        self.content = document.get_xmlpart('content')


    def test_get_style_list(self):
        content = self.content
        styles = content.get_style_list()
        self.assertEqual(len(styles), 3)


    def test_get_style_list_family(self):
        content = self.content
        styles = content.get_style_list(family='paragraph')
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
        auto_styles.append_element(style)
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
        self.content_part = content_part = odf_xmlpart('content', container)
        self.paragraph_element = content_part.get_element('//text:p[1]')
        query = '//style:style[@style:family="paragraph"][1]'
        self.style_element = content_part.get_element(query)


    def test_odf_style(self):
        style = self.style_element
        self.assert_(isinstance(style, odf_style))


    def test_get_style_properties(self):
        style = self.style_element
        properties = style.get_style_properties()
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 12)
        self.assertEqual(properties['fo:margin-left'], "0cm")


    def test_get_style_properties_area(self):
        style = self.style_element
        properties = style.get_style_properties(area='text')
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:hyphenate'], "false")


    def test_get_style_properties_bad_element(self):
        element = self.paragraph_element
        self.assertRaises(AttributeError, element.__getattribute__,
                          'get_style_properties')


    def test_get_style_properties_bad_area(self):
        style = self.style_element
        properties = style.get_style_properties(area='toto')
        self.assertEqual(properties, None)


    def test_set_style_properties(self):
        style = self.style_element.clone()
        style.set_style_properties({'fo:color': '#f00'})
        properties = style.get_style_properties()
        self.assertEqual(len(properties), 13)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_area(self):
        style = self.style_element.clone()
        style.set_style_properties({'fo:color': '#f00'}, area='text')
        properties = style.get_style_properties(area='text')
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_new_area(self):
        style = self.style_element.clone()
        properties = style.get_style_properties(area='toto')
        self.assertEqual(properties, None)
        style.set_style_properties({'fo:color': '#f00'}, area='toto')
        properties = style.get_style_properties(area='toto')
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_del_style_properties(self):
        style = self.style_element.clone()
        style.del_style_properties(['fo:margin-left'])
        properties = style.get_style_properties()
        self.assertEqual(len(properties), 11)
        self.assertRaises(KeyError, properties.__getitem__, 'fo:margin-left')


    def test_del_style_properties_bad_area(self):
        style = self.style_element
        self.assertRaises(ValueError, style.del_style_properties,
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



if __name__ == '__main__':
    main()
