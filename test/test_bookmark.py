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
from lpod.bookmark import odf_create_bookmark, odf_create_bookmark_start
from lpod.bookmark import odf_create_bookmark_end
from lpod.paragraph import odf_create_paragraph
from lpod.utils import convert_unicode


class BookmarkTest(TestCase):

    def setUp(self):
        document = odf_get_document('samples/bookmark.odt')
        self.body = document.get_body()


    def test_create_bookmark(self):
        bookmark = odf_create_bookmark(u'你好 Zoé')
        expected = ('<text:bookmark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark.serialize(), expected)


    def test_create_bookmark_start(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark_start.serialize(), expected)


    def test_create_bookmark_end(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(bookmark_end.serialize(), expected)


    def test_get_bookmark(self):
        body = self.body
        bookmark = odf_create_bookmark(u'你好 Zoé')
        body.append(bookmark)
        get = body.get_bookmark_by_name(u'你好 Zoé')
        expected = ('<text:bookmark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_list(self):
        body = self.body
        result = self.body.get_bookmark_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = '<text:bookmark text:name="Rep&#232;re de texte"/>'
        self.assertEqual(element.serialize(), expected)


    def test_get_bookmark_start(self):
        body = self.body
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        body.append(bookmark_start)
        get = body.get_bookmark_start_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_start_list(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        self.body.append(bookmark_start)
        get = self.body.get_bookmark_start_list()[0]
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end(self):
        body = self.body
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        body.append(bookmark_end)
        get = body.get_bookmark_end_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end_list(self):
        body = self.body
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        body.append(bookmark_end)
        get = body.get_bookmark_end_list()[0]
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_set_bookmark_simple(self):
        body = self.body
        paragraph = body.get_paragraph_by_position(-1)
        paragraph.set_bookmark("A bookmark")
        bookmark = paragraph.get_bookmark_by_name("A bookmark")
        self.assertNotEqual(bookmark, None)


    def test_set_bookmark_with_after_without_position(self):
        paragraph = odf_create_paragraph(u"aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", after="aa")
        expected = ('<text:p>aa<text:bookmark text:name="bookmark"/> '
                      '<text:span text:style-name="style">bb aa aa'
                      '</text:span>'
                    ' cc aa <text:span text:style-name="style">dd</text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_before(self):
        paragraph = odf_create_paragraph(u"aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", before="aa", position=1)
        expected = ('<text:p>aa '
                      '<text:span text:style-name="style">bb '
                      '<text:bookmark text:name="bookmark"/>aa aa'
                      '</text:span>'
                    ' cc aa <text:span text:style-name="style">dd</text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_after(self):
        paragraph = odf_create_paragraph(u"aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark", after="aa", position=1)
        expected = ('<text:p>aa '
                      '<text:span text:style-name="style">bb '
                      'aa<text:bookmark text:name="bookmark"/> aa'
                      '</text:span>'
                    ' cc aa <text:span text:style-name="style">dd</text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_position(self):
        paragraph = odf_create_paragraph(u"aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark1", position=0)
        paragraph.set_bookmark("bookmark2", position=2)
        paragraph.set_bookmark("bookmark3",
                               position=len(u"aa bb aa aa cc aa dd"))
        expected = ('<text:p><text:bookmark text:name="bookmark1"/>aa'
                      '<text:bookmark text:name="bookmark2"/> '
                      '<text:span text:style-name="style">bb aa aa</text:span>'
                      ' cc aa <text:span text:style-name="style">dd'
                      '<text:bookmark text:name="bookmark3"/></text:span>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_end(self):
        paragraph = odf_create_paragraph(u"aa bb aa aa cc aa dd")
        paragraph.set_span(style="style", regex="bb aa aa")
        paragraph.set_span(style="style", regex="dd")
        paragraph.set_bookmark("bookmark1", after="cc", position=-1)
        paragraph.set_bookmark("bookmark2", position=-1)
        expected = ('<text:p>aa '
                      '<text:span text:style-name="style">'
                      'bb aa aa'
                      '</text:span>'
                    ' cc<text:bookmark text:name="bookmark1"/> aa '
                    '<text:span text:style-name="style">dd</text:span>'
                    '<text:bookmark text:name="bookmark2"/>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_role(self):
        paragraph = odf_create_paragraph(u"aa")
        paragraph.set_bookmark("bookmark", role="start")
        paragraph.set_bookmark("bookmark", role="end", position=-1)
        expected = ('<text:p>'
                      '<text:bookmark-start text:name="bookmark"/>'
                      'aa'
                      '<text:bookmark-end text:name="bookmark"/>'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_content(self):
        paragraph = odf_create_paragraph(u"aa bb bb aa")
        paragraph.set_bookmark("bookmark", content="bb", position=1)
        expected = ('<text:p>aa bb '
                      '<text:bookmark-start text:name="bookmark"/>'
                      'bb'
                      '<text:bookmark-end text:name="bookmark"/>'
                      ' aa'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_set_bookmark_with_limits(self):
        paragraph = odf_create_paragraph(u"aa bb bb aa")
        paragraph.set_bookmark("bookmark", limits=(6, 8))
        expected = ('<text:p>aa bb '
                      '<text:bookmark-start text:name="bookmark"/>'
                      'bb'
                      '<text:bookmark-end text:name="bookmark"/>'
                      ' aa'
                    '</text:p>')
        self.assertEqual(paragraph.serialize(), expected)



if __name__ == '__main__':
    main()
