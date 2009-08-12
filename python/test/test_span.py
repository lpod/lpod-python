# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_span


class TestSpan(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/span_style.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_span(self):
        span = odf_create_span(u'my text', style='my_style')
        expected = ('<text:span text:style-name="my_style">'
                      'my text'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_get_span_list(self):
        content = self.content
        result = content.get_span_list()
        self.assertEqual(len(result), 2)
        element = result[0]
        expected = ('<text:span text:style-name="T1">'
                      'moustache'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span_list_style(self):
        content = self.content
        result = content.get_span_list(style='T2')
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(element.serialize(), expected)


    def test_get_span(self):
        content = self.content
        span = content.get_span_by_position(2)
        expected = ('<text:span text:style-name="T2">'
                      'rouge'
                    '</text:span>')
        self.assertEqual(span.serialize(), expected)


    def test_insert_span(self):
        span = odf_create_span('my_style', u'my text')
        clone = self.content.clone()
        paragraph = clone.get_paragraph_by_position(1)
        paragraph.append_element(span)



if __name__ == '__main__':
    main()
