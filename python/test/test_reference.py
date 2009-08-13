# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.reference import odf_create_reference_mark
from lpod.reference import odf_create_reference_mark_start
from lpod.reference import odf_create_reference_mark_end
from lpod.utils import convert_unicode


class reference_markTest(TestCase):

    def setUp(self):
        clone = odf_get_document('samples/bookmark.odt').clone()
        self.content = clone.get_xmlpart('content')
        self.body = clone.get_body()


    def test_create_reference_mark(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark.serialize(), expected)


    def test_create_reference_mark_start(self):
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_start.serialize(), expected)


    def test_create_reference_mark_end(self):
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_end.serialize(), expected)


    def test_get_reference_mark(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        self.body.append_element(reference_mark)

        get = self.content.get_reference_mark_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_list(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        self.body.append_element(reference_mark)

        get = self.content.get_reference_mark_list()[0]
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start(self):
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        self.body.append_element(reference_mark_start)

        get = self.content.get_reference_mark_start_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start_list(self):
        content = self.content
        result = content.get_reference_mark_start_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-start '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_reference_mark_end(self):
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        self.body.append_element(reference_mark_end)

        get = self.content.get_reference_mark_end_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_end_list(self):
        content = self.content
        result = content.get_reference_mark_end_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-end '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)



if __name__ == '__main__':
    main()
