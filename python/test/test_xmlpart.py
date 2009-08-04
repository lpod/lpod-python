# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from the XML Library
from lxml.etree import _ElementTree

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


    def setUp(self):
        container = odf_get_container('samples/example.odt')
        self.container = container
        content_part = odf_xmlpart('content', container)
        self.content_part = content_part
        self.paragraph_element = content_part.get_element('//text:p[1]')
        self.annotation_element = (
                content_part.get_element('//office:annotation[1]'))
        query = '//style:style[@style:family="paragraph"][1]'
        self.style_element = content_part.get_element(query)


    def tearDown(self):
        del self.annotation_element
        del self.paragraph_element
        del self.content_part
        del self.container


    def test_bad_python_element(self):
        self.assertRaises(TypeError, odf_element, '<text:p/>')


    def test_get_element_list(self):
        content_part = self.content_part
        elements = content_part.get_element_list('//text:p')
        # The annotation paragraph is counted
        self.assertEqual(len(elements), 8)


    def test_get_name(self):
        element = self.paragraph_element
        self.assertEqual(element.get_name(), 'text:p')


    def test_get_attributes(self):
        element = self.paragraph_element
        attributes = element.get_attributes()
        excepted = {'text:style-name': "Text_20_body"}
        self.assertEqual(attributes, excepted)


    def test_get_attribute(self):
        element = self.paragraph_element
        unknown = element.get_attribute('style-name')
        self.assertEqual(unknown, None)


    def test_get_attribute_namespace(self):
        element = self.paragraph_element
        text = element.get_attribute('text:style-name')
        self.assert_(isinstance(text, unicode))
        self.assertEqual(text, "Text_20_body")


    def test_get_attribute_none(self):
        element = self.paragraph_element
        dummy = element.get_attribute('and_now_for_sth_completely_different')
        self.assertEqual(dummy, None)


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
        text = element.get_text()
        self.assertEqual(text, u"This is the first paragraph.")


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
        self.assertEqual(element.get_text(), self.special_text)
        element.set_text(old_text)


    def test_get_parent(self):
        paragraph = self.paragraph_element
        parent = paragraph.get_parent()
        self.assertEqual(parent.get_name(), 'text:section')


    def test_get_parent_root(self):
        content = self.content_part
        root = content.get_root()
        parent = root.get_parent()
        self.assertEqual(parent, None)


    def test_get_text_content(self):
        element = self.annotation_element
        text = element.get_text_content()
        self.assertEqual(text, u"This is an annotation.")


    def test_set_text_content(self):
        element = self.annotation_element
        old_text = element.get_text_content()
        text = u"Have a break"
        element.set_text_content(text)
        self.assertEqual(element.get_text_content(), text)
        element.set_text_content


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
        self.assertRaises(AttributeError, element.insert_element, '<b/>',
                          FIRST_CHILD)


    def test_insert_element_bad_position(self):
        element = odf_create_element('<a/>')
        child = odf_create_element('<b/>')
        self.assertRaises(ValueError, element.insert_element, child, 999)


    def test_wrap_text_offset(self):
        paragraph = self.paragraph_element.clone()
        text = paragraph.get_text()
        offset = text.index("first")
        annotation = odf_create_element('<office:annotation/>')
        paragraph.wrap_text(annotation, offset)
        expected = ('<text:p text:style-name="Text_20_body">This is the '
                      '<office:annotation/>first paragraph.</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_wrap_text_offset_length(self):
        paragraph = self.paragraph_element.clone()
        text = paragraph.get_text()
        offset = text.index(u"first")
        length = len(u"first")
        span = odf_create_element('<text:span text:style-name="T1"/>')
        paragraph.wrap_text(span, offset, length)
        expected = ('<text:p text:style-name="Text_20_body">This is the '
                      '<text:span text:style-name="T1">first</text:span> '
                      'paragraph.</text:p>')
        self.assertEqual(paragraph.serialize(), expected)


    def test_get_children(self):
        element = self.annotation_element
        children = element.get_children()
        self.assertEqual(len(children), 4)
        child = children[0]
        self.assertEqual(child.get_name(), 'dc:creator')
        child = children[-1]
        self.assertEqual(child.get_name(), 'text:p')


    def test_get_style_properties(self):
        style = self.style_element
        self.assert_(style.is_style())
        properties = style.get_style_properties()
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 12)
        self.assertEqual(properties['fo:margin-left'], "0cm")


    def test_get_style_properties_area(self):
        style = self.style_element
        properties = style.get_style_properties(area='text')
        self.assert_(isinstance(properties, dict))
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:hyphenate'], "false")


    def test_get_style_properties_bad_element(self):
        element = self.paragraph_element
        self.assertRaises(TypeError, element.get_style_properties)


    def test_get_style_properties_bad_area(self):
        style = self.style_element
        properties = style.get_style_properties(area='toto')
        self.assertEqual(properties, None)


    def test_set_style_properties(self):
        style = self.style_element.clone()
        style.set_style_properties({'fo:color': '#f00'})
        properties = style.get_style_properties()
        self.assertEqual(len(properties), 13)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_area(self):
        style = self.style_element.clone()
        style.set_style_properties({'fo:color': '#f00'}, area='text')
        properties = style.get_style_properties(area='text')
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_set_style_properties_new_area(self):
        style = self.style_element.clone()
        properties = style.get_style_properties(area='toto')
        self.assertEqual(properties, None)
        style.set_style_properties({'fo:color': '#f00'}, area='toto')
        properties = style.get_style_properties(area='toto')
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties['fo:color'], "#f00")


    def test_del_style_properties(self):
        style = self.style_element.clone()
        style.del_style_properties(['fo:margin-left'])
        properties = style.get_style_properties()
        self.assertEqual(len(properties), 11)
        self.assertRaises(KeyError, properties.__getitem__, 'fo:margin-left')


    def test_del_style_properties_bad_area(self):
        style = self.style_element
        self.assertRaises(ValueError, style.del_style_properties,
                          area='toto')


    def test_clone(self):
        element = self.paragraph_element
        copy = element.clone()
        self.assertNotEqual(id(element), id(copy))
        self.assertEqual(element.get_text(), copy.get_text())


    def test_delete(self):
        element = odf_create_element('<a><b/></a>')
        child = element.get_element('//b')
        element.delete(child)
        self.assertEqual(element.serialize(), '<a/>')



class XmlNamespaceTestCase(TestCase):
    """We must be able to use the API with unknown prefix/namespace"""



class XmlPartTestCase(TestCase):

    def setUp(self):
        self.container = odf_get_container('samples/example.odt')


    def tearDown(self):
        del self.container


    def test_get_element_list(self):
        content_part = odf_xmlpart('content', self.container)
        elements = content_part.get_element_list('//text:p')
        # The annotation paragraph is counted
        self.assertEqual(len(elements), 8)


    def test_tree(self):
        # Testing a private but important method
        content = odf_xmlpart('content', self.container)
        tree = content._odf_xmlpart__get_tree()
        self.assert_(isinstance(tree, _ElementTree))
        self.assertNotEqual(content._odf_xmlpart__tree, None)


    def test_root(self):
        content = odf_xmlpart('content', self.container)
        root = content.get_root()
        self.assert_(isinstance(root, odf_element))
        self.assertEqual(root.get_name(), "office:document-content")
        self.assertNotEqual(content._odf_xmlpart__root, None)


    def test_serialize(self):
        container = self.container
        content_bytes = container.get_part('content')
        content_part = odf_xmlpart('content', container)
        # differences with lxml
        serialized = content_part.serialize().replace("'", "&apos;")
        self.assertEqual(content_bytes, serialized)


    def test_clone(self):
        # Testing that the clone works on subclasses too
        from lpod.content import odf_content
        container = self.container
        content = odf_content('content', container)
        clone = content.clone()
        self.assertEqual(clone.part_name, content.part_name)
        self.assertNotEqual(id(container), id(clone.container))
        self.assertEqual(clone._odf_xmlpart__tree, None)


    def test_delete(self):
        container = self.container
        content = odf_xmlpart('content', container)
        paragraphs = content.get_element_list('//text:p')
        for paragraph in paragraphs:
            content.delete(paragraph)
        serialized = content.serialize()
        self.assertEqual(serialized.count('<text:p'), 0)



if __name__ == '__main__':
    main()
