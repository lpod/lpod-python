# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.draw_page import odf_create_draw_page, odf_draw_page


class TestDrawPage(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/example.odp')
        self.body = document.get_body()


    def test_create_simple_page(self):
        element = odf_create_draw_page('id1')
        expected = '<draw:page draw:id="id1"/>'
        self.assertEqual(element.serialize(), expected)


    def test_create_complex_page(self):
        element = odf_create_draw_page('id1', name=u"Introduction",
                                       master_page='prs-novelty',
                                       page_layout='AL1T0', style='dp1')
        expected = ('<draw:page draw:id="id1" draw:name="Introduction" '
                    'draw:style-name="dp1" '
                    'draw:master-page-name="prs-novelty" '
                    'presentation:presentation-page-layout-name="AL1T0"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_draw_page_list(self):
        body = self.body
        result = body.get_draw_page_list()
        self.assertEqual(len(result), 2)


    def test_get_draw_page_list_style(self):
        body = self.body.clone()
        result = body.get_draw_page_list(style='dp1')
        self.assertEqual(len(result), 2)
        result = body.get_draw_page_list(style='dp2')
        self.assertEqual(len(result), 0)


    def test_odf_draw_page(self):
        body = self.body
        draw_page = body.get_draw_page_by_name(u"Titre")
        self.assert_(isinstance(draw_page, odf_draw_page))


    def test_get_draw_page_by_name(self):
        body = self.body.clone()
        good = body.get_draw_page_by_name(u"Titre")
        self.assertNotEqual(good, None)
        bad = body.get_draw_page_by_name(u"Conclusion")
        self.assertEqual(bad, None)


    def test_get_page_name(self):
        body = self.body
        page = body.get_draw_page_by_position(1)
        self.assertEqual(page.get_page_name(), u"Titre")


    def test_set_page_name(self):
        body = self.body.clone()
        page = body.get_draw_page_by_position(1)
        name = u"Intitulé"
        self.assertNotEqual(page.get_page_name(), name)
        page.set_page_name(u"Intitulé")
        self.assertEqual(page.get_page_name(), name)



if __name__ == '__main__':
    main()
