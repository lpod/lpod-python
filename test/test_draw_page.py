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
                                       presentation_page_layout='AL1T0',
                                       style='dp1')
        expected = ('<draw:page draw:id="id1" draw:name="Introduction" '
                    'draw:style-name="dp1" '
                    'draw:master-page-name="prs-novelty" '
                    'presentation:presentation-page-layout-name="AL1T0"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_draw_page_list(self):
        body = self.body
        result = body.get_draw_pages()
        self.assertEqual(len(result), 2)


    def test_get_draw_page_list_style(self):
        body = self.body.clone()
        result = body.get_draw_pages(style='dp1')
        self.assertEqual(len(result), 2)
        result = body.get_draw_pages(style='dp2')
        self.assertEqual(len(result), 0)


    def test_odf_draw_page(self):
        body = self.body
        draw_page = body.get_draw_page()
        self.assert_(isinstance(draw_page, odf_draw_page))


    def test_get_draw_page_by_name(self):
        body = self.body.clone()
        good = body.get_draw_page(name=u"Titre")
        self.assertNotEqual(good, None)
        bad = body.get_draw_page(name=u"Conclusion")
        self.assertEqual(bad, None)


    def test_get_page_name(self):
        body = self.body
        page = body.get_draw_page(name=u"Titre")
        self.assertEqual(page.get_name(), u"Titre")


    def test_set_page_name(self):
        body = self.body.clone()
        page = body.get_draw_page(position=0)
        name = u"Intitulé"
        self.assertNotEqual(page.get_name(), name)
        page.set_name(u"Intitulé")
        self.assertEqual(page.get_name(), name)



if __name__ == '__main__':
    main()
