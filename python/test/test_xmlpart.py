# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.container import get_odf_container
from lpod.context import create_element, odf_context
from lpod.context import CHILD, NEXT_SIBLING, PREV_SIBLING


class CreateElementTestCase(TestCase):

    def test_simple(self):
        data = '<p>Template Element</p>'
        element = create_element(data)
        self.assertEqual(element.serialize(), data)


    def test_namespace(self):
        ns = 'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
        data = '<text:p %s>Template Element</text:p>' % ns
        element = create_element(data)
        self.assertEqual(element.serialize(), data)



class ElementTestCase(TestCase):

    special_text = 'using < & " characters'
    quoted_text = 'using &lt; &amp; " characters'


    def setUp(self):
        container = get_odf_container('samples/example.odt')
        self.container = container
        content_context = odf_context('content', container)
        self.content_context = content_context
        paragraph_element = content_context.get_element_list('//text:p[1]')
        self.paragraph_element = paragraph_element[0]


    def tearDown(self):
        del self.paragraph_element
        del self.content_context
        del self.container


    def test_get_element_list(self):
        elements = self.content_context.get_element_list('//text:p')
        self.assertEqual(len(elements), 1)


    def test_get_attribute(self):
        element = self.paragraph_element
        text = element.get_attribute('style-name')
        self.assert_(isinstance(text, str))
        self.assertEqual(text, 'Standard')


    def test_set_attribute(self):
        element = self.paragraph_element
        element.set_attribute('test', 'a value')
        self.assertEqual(element.get_attribute('test'), 'a value')
        element.del_attribute('test')


    def test_set_attribute_special(self):
        element = self.paragraph_element
        element.set_attribute('test', self.special_text)
        self.assertEqual(element.get_attribute('test'), self.special_text)
        element.del_attribute('test')


    def test_del_attribute(self):
        element = self.paragraph_element
        element.set_attribute('test', 'test')
        self.assertEqual(element.get_attribute('test'), 'test')
        element.del_attribute('test')
        self.assertEqual(element.get_attribute('test'), None)


    def test_get_text(self):
        element = self.paragraph_element
        self.assertEqual(element.get_text(), u"This is an example.")


    def test_set_text(self):
        element = self.paragraph_element
        old_text = element.get_text()
        new_text = u'A test'
        element.set_text(new_text)
        self.assertEqual(element.get_text(), new_text)
        element.set_text(old_text)
        self.assertEqual(element.get_text(), old_text)


    def test_set_text_special(self):
        element = self.paragraph_element
        old_text = element.get_text()
        element.set_text(self.special_text)
        self.assertEqual(element.get_text(), self.quoted_text)
        element.set_text(old_text)


    def test_insert_element_child(self):
        element = create_element('<toto/>')
        child = create_element('<titi/>')
        element.insert_element(child, CHILD)
        self.assertEqual(element.serialize(), '<toto><titi/></toto>')


    def test_insert_element_next_sibling(self):
        element = create_element('<toto/>')
        sibling = create_element('<titi/>')
        element.insert_element(sibling, NEXT_SIBLING)
        self.assertEqual(element.serialize(), '<toto/><titi/>')


    def test_insert_element_prev_sibling(self):
        element = create_element('<toto/>')
        sibling = create_element('<titi/>')
        element.insert_element(sibling, PREV_SIBLING)
        self.assertEqual(element.serialize(), '<titi/><toto/>')


    def test_insert_element_bad_element(self):
        element = create_element('<toto/>')
        self.assertRaises(TypeError, element.insert_element, None, CHILD)


    def test_insert_element_bad_position(self):
        element = create_element('<toto/>')
        child = create_element('<titi/>')
        self.assertRaises(ValueError, element.insert_element, child, None)


    def test_copy(self):
        element = self.paragraph_element
        copy = element.copy()
        self.assertNotEqual(id(element), id(copy))
        self.assertEqual(element.get_text(), copy.get_text())


    def test_delete(self):
        element = create_element('<toto><titi/></toto>')
        titi = element.get_element_list('//titi')[0]
        titi.delete()
        self.assertEqual(element.serialize(), '<toto/>')



class ContextTestCase(TestCase):

    def setUp(self):
        self.container = get_odf_container('samples/example.odt')


    def tearDown(self):
        del self.container


    def test_get_element_list(self):
        content_context = odf_context('content', self.container)
        elements = content_context.get_element_list('//text:p')
        self.assertEqual(len(elements), 1)


    def serialize(self):
        container = self.container
        content_bytes = container.get_part('content')
        content_context = odf_context('content', container)
        self.assertEqual(content_bytes, content_context.serialize())



if __name__ == '__main__':
    main()
