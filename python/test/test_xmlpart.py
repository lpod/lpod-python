# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from the XML Library
from lxml.etree import _ElementTree

# Import from lpod
from lpod.container import odf_get_container
from lpod.element import odf_create_element, odf_element
from lpod.xmlpart import odf_xmlpart


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
        self.assertEqual(root.get_tagname(), "office:document-content")
        self.assertNotEqual(content._odf_xmlpart__root, None)


    def test_serialize(self):
        container = self.container
        content_bytes = container.get_part('content')
        content_part = odf_xmlpart('content', container)
        # differences with lxml
        serialized = content_part.serialize().replace("'", "&apos;")
        # XXX OOo is adding two carriage returns behind the XML declaration
        serialized = serialized.replace('<?xml version="1.0" encoding="UTF-8"?>\n',
                                        '<?xml version="1.0" encoding="UTF-8"?>\n\n')
        self.assertEqual(content_bytes, serialized)


    def test_pretty_serialize(self):
        # With pretty = True
        element = odf_create_element('<root><a>spam</a><b/></root>')
        serialized = element.serialize(pretty=True)
        expected = ('<root>\n'
                    '  <a>spam</a>\n'
                    '  <b/>\n'
                    '</root>\n')
        self.assertEqual(serialized, expected)


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
