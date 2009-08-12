# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document, odf_create_draw_page
from lpod.draw_page import odf_draw_page


class TestDrawPage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odp')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_simple_page(self):
        element = odf_create_draw_page(u"Page de titre")
        expected = '<draw:page draw:name="Page de titre"/>'
        self.assertEqual(element.serialize(), expected)


    def test_create_complex_page(self):
        element = odf_create_draw_page(u"Introduction", page_id='id1',
                                       master_page='prs-novelty',
                                       page_layout='AL1T0', style='dp1')
        expected = ('<draw:page draw:name="Introduction" '
                    'draw:style-name="dp1" '
                    'draw:master-page-name="prs-novelty" '
                    'presentation:presentation-page-layout-name="AL1T0" '
                    'draw:id="id1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_draw_page_list(self):
        content = self.content
        result = content.get_draw_page_list()
        self.assertEqual(len(result), 2)


    def test_get_draw_page_list_style(self):
        content = self.content.clone()
        result = content.get_draw_page_list(style='dp1')
        self.assertEqual(len(result), 2)
        result = content.get_draw_page_list(style='dp2')
        self.assertEqual(len(result), 0)


    def test_get_draw_page(self):
        content = self.content.clone()
        result = content.get_draw_page_by_name(u"Titre")
        self.assert_(isinstance(result, odf_draw_page))
        result = content.get_draw_page_by_name(u"Conclusion")
        self.assertEqual(result, None)



if __name__ == '__main__':
    main()
