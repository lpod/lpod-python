# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main
from re import compile

# Import from lxml
from lxml.etree import _ElementStringResult, _ElementUnicodeResult

# Import from lpod
from lpod.element import odf_text, odf_create_element


class NewTextTestCase(TestCase):

    def test_str(self):
        text = odf_text(_ElementStringResult("dummy"))
        self.assert_(text.get_parent() is None)
        self.assert_(text.is_text() is None)
        self.assert_(text.is_tail() is None)



    def test_unicode(self):
        text = odf_text(_ElementUnicodeResult(u"dummy"))
        self.assert_(text.get_parent() is None)
        self.assert_(text.is_text() is None)
        self.assert_(text.is_tail() is None)



class TextTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.result = element.xpath('descendant::text()')


    def test_nodes(self):
        self.assertEqual(len(self.result), 2)


    def test_text(self):
        text = self.result[0]
        self.assertEqual(text, u"text")
        self.assert_(text.is_text() is True)
        self.assert_(text.is_tail() is False)


    def test_tail(self):
        tail = self.result[1]
        self.assertEqual(tail, u"tail")
        self.assert_(tail.is_text() is False)
        self.assert_(tail.is_tail() is True)



class ParentTestCase(TestCase):

    def setUp(self):
        element = odf_create_element('<text:p>text<text:span/>tail</text:p>')
        self.result = element.xpath('descendant::text()')

    def test_text(self):
        text = self.result[0]
        self.assertEqual(text.get_parent().get_tagname(), 'text:p')


    def test_tail(self):
        tail = self.result[1]
        self.assertEqual(tail.get_parent().get_tagname(), 'text:span')



if __name__ == '__main__':
    main()
