# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.container import odf_get_container
from lpod.xmlpart import odf_create_element, odf_element, odf_xmlpart
from lpod.xmlpart import FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING


class CreateElementTestCase(TestCase):

    def test_simple(self):
        data = '<p>Template Element</p>'
        element = odf_create_element(data)
        self.assertEqual(element.serialize(), data)


    def test_namespace(self):
        data = '<text:p>Template Element</text:p>'
        element = odf_create_element(data)
        self.assertEqual(element.serialize(), data)



class ElementTestCase(TestCase):

    special_text = 'using < & " characters'
    quoted_text = 'using &lt; &amp; " characters'


    def setUp(self):
        container = odf_get_container('samples/example.odt')
        self.container = container
        content_context = odf_xmlpart('content', container)
        self.content_context = content_context
        paragraph_element = content_context.get_element_list('//text:p[1]')
        self.paragraph_element = paragraph_element[0]


    def tearDown(self):
        del self.paragraph_element
        del self.content_context
        del self.container


    def test_bad_python_element(self):
        self.assertRaises(TypeError, odf_element, '<text:p/>')


    def test_bad_native_element(self):
        # XXX this test purposely knows the XML library behind
        element = self.paragraph_element
        element_node = element._odf_element__element
        text_node = element_node.children
        self.assertRaises(TypeError, odf_element, text_node)


    def test_get_element_list(self):
        elements = self.content_context.get_element_list('//text:p')
        self.assertEqual(len(elements), 1)


    def test_get_attribute(self):
        element = self.paragraph_element
        text = element.get_attribute('style-name')
        self.assert_(isinstance(text, str))
        self.assertEqual(text, "Standard")


    def test_get_attribute_namespace(self):
        element = self.paragraph_element
        text = element.get_attribute('text:style-name')
        self.assert_(isinstance(text, str))
        self.assertEqual(text, "Standard")


    def test_set_attribute(self):
        element = self.paragraph_element
        element.set_attribute('test', "a value")
        self.assertEqual(element.get_attribute('test'), "a value")
        element.del_attribute('test')


    def test_set_attribute_namespace(self):
        element = self.paragraph_element
        element.set_attribute('text:style-name', "Note")
        self.assertEqual(element.get_attribute('text:style-name'), "Note")
        element.del_attribute('text:style-name')


    def test_set_attribute_special(self):
        element = self.paragraph_element
        element.set_attribute('test', self.special_text)
        self.assertEqual(element.get_attribute('test'), self.special_text)
        element.del_attribute('test')


    def test_del_attribute(self):
        element = self.paragraph_element
        element.set_attribute('test', "test")
        element.del_attribute('test')
        self.assertEqual(element.get_attribute('test'), None)


    def test_del_attribute_namespace(self):
        element = self.paragraph_element
        element.set_attribute('text:style-name', "Note")
        element.del_attribute('text:style-name')
        self.assertEqual(element.get_attribute('text:style-name'), None)


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


    def test_insert_element_first_child(self):
        element = odf_create_element('<root><a/></root>')
        child = odf_create_element('<b/>')
        element.insert_element(child, FIRST_CHILD)
        self.assertEqual(element.serialize(), '<root><b/><a/></root>')


    def test_insert_element_last_child(self):
        element = odf_create_element('<root><a/></root>')
        child = odf_create_element('<b/>')
        element.insert_element(child, LAST_CHILD)
        self.assertEqual(element.serialize(), '<root><a/><b/></root>')


    def test_insert_element_next_sibling(self):
        root = odf_create_element('<root><a/><b/></root>')
        element = root.get_element_list('//a')[0]
        sibling = odf_create_element('<c/>')
        element.insert_element(sibling, NEXT_SIBLING)
        self.assertEqual(root.serialize(), '<root><a/><c/><b/></root>')


    def test_insert_element_prev_sibling(self):
        root = odf_create_element('<root><a/><b/></root>')
        element = root.get_element_list('//a')[0]
        sibling = odf_create_element('<c/>')
        element.insert_element(sibling, PREV_SIBLING)
        self.assertEqual(root.serialize(), '<root><c/><a/><b/></root>')


    def test_insert_element_bad_element(self):
        element = odf_create_element('<a/>')
        self.assertRaises(TypeError, element.insert_element, '<b/>',
                          FIRST_CHILD)


    def test_insert_element_bad_position(self):
        element = odf_create_element('<a/>')
        child = odf_create_element('<b/>')
        self.assertRaises(ValueError, element.insert_element, child, 999)


    def test_copy(self):
        element = self.paragraph_element
        copy = element.copy()
        self.assertNotEqual(id(element), id(copy))
        self.assertEqual(element.get_text(), copy.get_text())


    def test_delete(self):
        element = odf_create_element('<a><b/></a>')
        child = element.get_element_list('//b')[0]
        child.delete()
        self.assertEqual(element.serialize(), '<a/>')



class XmlPartTestCase(TestCase):

    def setUp(self):
        self.container = odf_get_container('samples/example.odt')


    def tearDown(self):
        del self.container


    def test_get_element_list(self):
        content_context = odf_xmlpart('content', self.container)
        elements = content_context.get_element_list('//text:p')
        self.assertEqual(len(elements), 1)


    def serialize(self):
        container = self.container
        content_bytes = container.get_part('content')
        content_context = odf_xmlpart('content', container)
        self.assertEqual(content_bytes, content_context.serialize())



if __name__ == '__main__':
    main()
