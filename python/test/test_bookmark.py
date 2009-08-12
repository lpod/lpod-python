# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_bookmark, odf_create_bookmark_start
from lpod.document import odf_create_bookmark_end
from lpod.utils import convert_unicode


class BookmarkTest(TestCase):

    def setUp(self):
        clone = odf_get_document('samples/bookmark.odt').clone()
        self.content = clone.get_xmlpart('content')
        self.body = clone.get_body()


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
        bookmark = odf_create_bookmark(u'你好 Zoé')
        self.body.append_element(bookmark)

        get = self.content.get_bookmark_by_name(u'你好 Zoé')
        expected = ('<text:bookmark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_list(self):
        content = self.content
        result = self.content.get_bookmark_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = '<text:bookmark text:name="Rep&#232;re de texte"/>'
        self.assertEqual(element.serialize(), expected)


    def test_get_bookmark_start(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        self.body.append_element(bookmark_start)

        get = self.content.get_bookmark_start_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_start_list(self):
        bookmark_start = odf_create_bookmark_start(u'你好 Zoé')
        self.body.append_element(bookmark_start)

        get = self.content.get_bookmark_start_list()[0]
        expected = ('<text:bookmark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        self.body.append_element(bookmark_end)

        get = self.content.get_bookmark_end_by_name(u'你好 Zoé')
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_bookmark_end_list(self):
        bookmark_end = odf_create_bookmark_end(u'你好 Zoé')
        self.body.append_element(bookmark_end)

        get = self.content.get_bookmark_end_list()[0]
        expected = ('<text:bookmark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)



if __name__ == '__main__':
    main()
