# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from lpod.element import odf_create_element
from lpod.link import odf_create_link


class TestLinks(TestCase):

    def setUp(self):
        document = odf_get_document('samples/base_text.odt')
        self.body = body = document.get_body().clone()
        self.paragraph = body.get_paragraph()


    def test_create_link1(self):
        link = odf_create_link('http://example.com/')
        expected = '<text:a xlink:href="http://example.com/"/>'
        self.assertEqual(link.serialize(), expected)


    def test_create_link2(self):
        link = odf_create_link('http://example.com/', name=u'link2',
                               target_frame='_blank', style='style1',
                               visited_style='style2')
        expected = ('<text:a xlink:href="http://example.com/" '
                      'office:name="link2" office:target-frame-name="_blank" '
                      'xlink:show="new" text:style-name="style1" '
                      'text:visited-style-name="style2"/>')
        self.assertEqual(link.serialize(), expected)


    def test_get_link(self):
        link1 = odf_create_link('http://example.com/', name='link1')
        link2 = odf_create_link('http://example.com/', name='link2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        element = self.body.get_link(name=u'link2')
        expected = ('<text:a xlink:href="http://example.com/" '
                      'office:name="link2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list(self):
        link1 = odf_create_link('http://example.com/', name='link1')
        link2 = odf_create_link('http://example.com/', name='link2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        element = self.body.get_links()[1]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_name(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # name
        element = self.body.get_links(name='link1')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link1" office:title="title1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_title(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # title
        element = self.body.get_links(title='title2')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link2" office:title="title2"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_list_href(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # href
        elements = self.body.get_links(href=ur'\.com')
        self.assertEqual(len(elements), 2)


    def test_href_from_existing_document(self):
        body = self.body
        links = body.get_links(href=ur'lpod')
        self.assertEqual(len(links), 1)


    def test_get_link_list_name_and_title(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # name and title
        element = self.body.get_links(name='link1', title='title1')[0]
        expected = ('<text:a xlink:href="http://example.com/" '
                    'office:name="link1" office:title="title1"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_link_by_href(self):
        body = self.body
        link = body.get_link(href=ur'lpod')
        href = link.get_attribute('xlink:href')
        self.assertEqual(href, u'http://lpod-project.org/')


    def test_get_link_by_path_context(self):
        body = self.body
        section2 = body.get_section(position=1)
        link = section2.get_link(href=ur'\.org')
        href = link.get_attribute('xlink:href')
        self.assertEqual(href, u'http://lpod-project.org/')


    def test_get_link_list_not_found(self):
        link1 = odf_create_link('http://example.com/', name='link1',
                                title='title1')
        link2 = odf_create_link('http://example.com/', name='link2',
                                title='title2')
        paragraph = self.paragraph
        paragraph.append(link1)
        paragraph.append(link2)
        # Not found
        element = self.body.get_links(name='link1', title='title2')
        self.assertEqual(element, [])



class TestInsertLink(object): #TestCase):

    def test_insert_link_simple(self):
        paragraph = odf_create_element('<text:p>toto tata titi</text:p>')
        paragraph.insert_link("http://", from_=u"tata", to=u"tata")
        expected = ('<text:p>toto '
                      '<text:a xlink:href="http://">tata</text:a> '
                      'titi</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_insert_link_medium(self):
        paragraph = odf_create_element('<text:p><text:span>toto</text:span> '
                                         'tata titi</text:p>')
        paragraph.insert_link("http://", from_=u"tata", to=u"tata")
        expected = ('<text:p><text:span>toto</text:span> '
                      '<text:a xlink:href="http://">tata</text:a> '
                      'titi</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_insert_link_complex(self):
        paragraph = odf_create_element('<text:p>toto '
                                         '<text:span> tata </text:span> '
                                         'titi</text:p>')
        paragraph.insert_link("http://", from_=u"tata", to=u"titi")
        expected = ('<text:p>toto <text:span> </text:span>'
                      '<text:a xlink:href="http://">'
                        '<text:span>tata </text:span> titi'
                      '</text:a>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_insert_link_horrible(self):
        paragraph = odf_create_element('<text:p>toto '
                                         '<text:span>tata titi</text:span>'
                                         ' tutu </text:p>')
        paragraph.insert_link("http://", from_=u"titi", to=u"tutu")
        expected = ('<text:p>toto <text:span>tata </text:span>'
                      '<text:a xlink:href="http://">'
                        '<text:span>titi</text:span> tutu'
                      '</text:a> '
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_insert_link_hideous(self):
        paragraph = odf_create_element('<text:p>toto '
                                         '<text:span>tata titi</text:span>'
                                         ' <text:span>tutu tyty</text:span>'
                                         '</text:p>')
        paragraph.insert_link("http://", from_=u"titi", to=u"tutu")
        expected = ('<text:p>toto <text:span>tata </text:span>'
                      '<text:a xlink:href="http://">'
                        '<text:span>titi</text:span> '
                        '<text:span>tutu</text:span>'
                      '</text:a>'
                      '<text:span> tyty</text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)



if __name__ == '__main__':
    main()
