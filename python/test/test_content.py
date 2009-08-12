# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document


class ContentTestCase(TestCase):
    # TODO test "get_body"
    pass


class GetElementTestCase(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/basetext.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_element_missed(self):
        content = self.content
        paragraph = content.get_paragraph_by_position(999)
        self.assertEqual(paragraph, None)


    def test_get_element_list(self):
        content = self.content
        regex = ur'(first|second|a) paragraph'
        paragraphs = content._get_element_list('//text:p', regex=regex)
        self.assertEqual(len(paragraphs), 4)



if __name__ == '__main__':
    main()
