# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.container import odf_get_container
from lpod.style import odf_style
from lpod.xmlpart import odf_xmlpart


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



if __name__ == '__main__':
    main()
