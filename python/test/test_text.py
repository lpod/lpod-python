# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.element import odf_text, odf_create_element


class TextTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.results = element.xpath('descendant::text()')


    def test_nodes(self):
        self.assertEqual(len(self.results), 2)


    def test_type(self):
        self.assert_(type(self.results[0]) is odf_text)


    def test_text(self):
        text = self.results[0]
        self.assertEqual(text, u"text")
        self.assert_(text.is_text() is True)
        self.assert_(text.is_tail() is False)


    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail, u"tail")
        self.assert_(tail.is_text() is False)
        self.assert_(tail.is_tail() is True)



class ParentTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.results = element.xpath('descendant::text()')

    def test_text(self):
        text = self.results[0]
        self.assertEqual(text.get_parent().get_tagname(), 'text:p')


    def test_tail(self):
        tail = self.results[1]
        self.assertEqual(tail.get_parent().get_tagname(), 'text:span')



if __name__ == '__main__':
    main()
