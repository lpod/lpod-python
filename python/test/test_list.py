# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.element import LAST_CHILD
from lpod.list import odf_create_list, odf_create_list_item
from lpod.utils import convert_unicode


class TestList(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/list.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_item(self):
        item = odf_create_list_item()
        expected = '<text:list-item/>'
        self.assertEqual(item.serialize(), expected)


    def test_create_list(self):
        item = odf_create_list_item()
        a_list = odf_create_list([u'你好 Zoé'])
        expected = (('<text:list>'
                       '<text:list-item>'
                         '<text:p>%s</text:p>'
                       '</text:list-item>'
                     '</text:list>') % convert_unicode(u'你好 Zoé'))
        self.assertEqual(a_list.serialize(), expected)


    def test_insert_list(self):
        content = self.content
        clone = content.clone()
        item = odf_create_list_item()
        a_list = odf_create_list(style='a_style')
        a_list.insert_element(item, LAST_CHILD)
        body = clone.get_body()
        body.insert_element(a_list, LAST_CHILD)

        expected = ('<text:list text:style-name="a_style">'
                    '<text:list-item/>'
                    '</text:list>')
        self.assertEqual(a_list.serialize(), expected)


    def test_insert_item(self):
        breakfast = odf_create_list()
        breakfast.insert_item(u'spam', 1)
        breakfast.insert_item(u'eggs', 2)
        item = odf_create_list_item(u'ham')
        breakfast.insert_item(item, -1)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>ham</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>eggs</text:p>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)


    def test_append_item(self):
        breakfast = odf_create_list()
        breakfast.append_item(u'spam')
        breakfast.append_item(u'ham')
        item = odf_create_list_item(u'eggs')
        breakfast.append_item(item)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>ham</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>eggs</text:p>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)


    def test_insert_sub_item(self):
        spam = odf_create_list([u'spam'])
        ham = odf_create_list([u'ham'])
        eggs = odf_create_list([u'eggs'])

        spam.insert_item(ham, 1)
        ham.insert_item(eggs, 1)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:list>'
                          '<text:list-item>'
                            '<text:p>ham</text:p>'
                          '</text:list-item>'
                          '<text:list-item>'
                            '<text:list>'
                              '<text:list-item>'
                                '<text:p>eggs</text:p>'
                              '</text:list-item>'
                            '</text:list>'
                          '</text:list-item>'
                        '</text:list>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(spam.serialize(), expected)


    def test_append_sub_item(self):
        spam = odf_create_list([u'spam'])
        ham = odf_create_list([u'ham'])
        eggs = odf_create_list([u'eggs'])

        spam.append_item(ham)
        ham.append_item(eggs)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:list>'
                          '<text:list-item>'
                            '<text:p>ham</text:p>'
                          '</text:list-item>'
                          '<text:list-item>'
                            '<text:list>'
                              '<text:list-item>'
                                '<text:p>eggs</text:p>'
                              '</text:list-item>'
                            '</text:list>'
                          '</text:list-item>'
                        '</text:list>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(spam.serialize(), expected)


    def test_nested_list(self):
        breakfast = odf_create_list()
        spam = odf_create_list_item(u'spam')
        ham = odf_create_list_item(u'ham')
        eggs = odf_create_list_item(u'eggs')
        # First way: a list in an item, right next to a paragraph
        spam.append_element(odf_create_list([u'thé', u'café', u'chocolat']))
        breakfast.append_item(spam)
        breakfast.append_item(ham)
        breakfast.append_item(eggs)
        # Second way: a list as an item
        breakfast.append_item(breakfast.clone())

        expected = ('<text:list>\n'
                    '  <text:list-item>\n'
                    '    <text:p>spam</text:p>\n'
                    '    <text:list>\n'
                    '      <text:list-item>\n'
                    '        <text:p>th&#233;</text:p>\n'
                    '      </text:list-item>\n'
                    '      <text:list-item>\n'
                    '        <text:p>caf&#233;</text:p>\n'
                    '      </text:list-item>\n'
                    '      <text:list-item>\n'
                    '        <text:p>chocolat</text:p>\n'
                    '      </text:list-item>\n'
                    '    </text:list>\n'
                    '  </text:list-item>\n'
                    '  <text:list-item>\n'
                    '    <text:p>ham</text:p>\n'
                    '  </text:list-item>\n'
                    '  <text:list-item>\n'
                    '    <text:p>eggs</text:p>\n'
                    '  </text:list-item>\n'
                    '  <text:list-item>\n'
                    '    <text:list>\n'
                    '      <text:list-item>\n'
                    '        <text:p>spam</text:p>\n'
                    '        <text:list>\n'
                    '          <text:list-item>\n'
                    '            <text:p>th&#233;</text:p>\n'
                    '          </text:list-item>\n'
                    '          <text:list-item>\n'
                    '            <text:p>caf&#233;</text:p>\n'
                    '          </text:list-item>\n'
                    '          <text:list-item>\n'
                    '            <text:p>chocolat</text:p>\n'
                    '          </text:list-item>\n'
                    '        </text:list>\n'
                    '      </text:list-item>\n'
                    '      <text:list-item>\n'
                    '        <text:p>ham</text:p>\n'
                    '      </text:list-item>\n'
                    '      <text:list-item>\n'
                    '        <text:p>eggs</text:p>\n'
                    '      </text:list-item>\n'
                    '    </text:list>\n'
                    '  </text:list-item>\n'
                    '</text:list>\n')
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(pretty=True), expected)


    def test_insert_before(self):
        breakfast = odf_create_list()
        breakfast.append_item(u'spam')
        eggs = odf_create_list_item(u'eggs')
        breakfast.append_item(eggs)
        ham = odf_create_list_item(u'ham')
        breakfast.insert_item(ham, before=eggs)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>ham</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>eggs</text:p>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)


    def test_insert_after(self):
        breakfast = odf_create_list()
        breakfast.append_item(u'spam')
        ham = odf_create_list_item(u'ham')
        breakfast.append_item(ham)
        eggs = odf_create_list_item(u'eggs')
        breakfast.insert_item(eggs, after=ham)

        expected = ('<text:list>'
                      '<text:list-item>'
                        '<text:p>spam</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>ham</text:p>'
                      '</text:list-item>'
                      '<text:list-item>'
                        '<text:p>eggs</text:p>'
                      '</text:list-item>'
                    '</text:list>')
        # TODO use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)


    def test_get_item_by_content(self):
        # Create the items
        spam = odf_create_list_item(u'spam')
        ham = odf_create_list_item(u'ham')
        eggs = odf_create_list_item(u'eggs')
        # Create the corresponding lists
        spam_list = odf_create_list()
        ham_list = odf_create_list()
        eggs_list = odf_create_list()
        # Fill the lists
        spam_list.append_item(spam)
        ham_list.append_item(ham)
        eggs_list.append_item(eggs)
        # Create the final nested list (spam_list)
        spam.append_element(ham_list)
        ham.append_element(eggs_list)

        item = spam_list.get_item_by_content(ur'spam')
        expected = ('<text:list-item>\n'
                    '  <text:p>spam</text:p>\n'
                    '  <text:list>\n'
                    '    <text:list-item>\n'
                    '      <text:p>ham</text:p>\n'
                    '      <text:list>\n'
                    '        <text:list-item>\n'
                    '          <text:p>eggs</text:p>\n'
                    '        </text:list-item>\n'
                    '      </text:list>\n'
                    '    </text:list-item>\n'
                    '  </text:list>\n'
                    '</text:list-item>\n')
        self.assertEqual(item.serialize(pretty=True), expected)
        item = spam_list.get_item_by_content(ur'ham')
        expected = ('<text:list-item>\n'
                    '  <text:p>ham</text:p>\n'
                    '  <text:list>\n'
                    '    <text:list-item>\n'
                    '      <text:p>eggs</text:p>\n'
                    '    </text:list-item>\n'
                    '  </text:list>\n'
                    '</text:list-item>\n')
        self.assertEqual(item.serialize(pretty=True), expected)
        item = spam_list.get_item_by_content(ur'eggs')
        expected = ('<text:list-item>\n'
                    '  <text:p>eggs</text:p>\n'
                    '</text:list-item>\n')
        self.assertEqual(item.serialize(pretty=True), expected)


    def test_get_formated_text(self):
        # Create the items
        spam = odf_create_list_item(u'In this picture, there are 47 people;\n'
                                    u'none of them can be seen.')
        ham = odf_create_list_item(u'In this film, we hope to show you the\n'
                                   u'value of not being seen.\n')
        eggs = odf_create_list_item(u'Here is Mr. Bagthorpe of London, '
                                    u'SE14.\n')
        foo = odf_create_list_item(u'He cannot be seen.')
        bar = odf_create_list_item(u'Now I am going to ask him to stand up.')
        baz = odf_create_list_item(u'Mr. Bagthorpe, will you stand up please?')
        # Create the lists
        how_not_to_be_seen1 = odf_create_list()
        how_not_to_be_seen2 = odf_create_list()
        how_not_to_be_seen3 = odf_create_list()
        # Fill the lists
        # First list
        how_not_to_be_seen1.append_item(spam)
        # Second list
        how_not_to_be_seen2.append_item(ham)
        how_not_to_be_seen2.append_item(eggs)
        how_not_to_be_seen2.append_item(foo)
        # Third list
        how_not_to_be_seen3.append_item(bar)
        how_not_to_be_seen3.append_item(baz)
        # Create the final nested list (how_not_to_be_seen1)
        spam.append_element(how_not_to_be_seen2)
        foo.append_element(how_not_to_be_seen3)

        # Initialize an empty context
        context = {'notes_counter': 0,
                   'footnotes': [],
                   'endnotes': []}
        expected = (u'- In this picture, there are 47 people;\n'
                    u'  none of them can be seen.\n'
                    u'  - In this film, we hope to show you the\n'
                    u'    value of not being seen.\n'
                    u'  - Here is Mr. Bagthorpe of London, SE14.\n'
                    u'  - He cannot be seen.\n'
                    u'    - Now I am going to ask him to stand up.\n'
                    u'    - Mr. Bagthorpe, will you stand up please?\n')
        self.assertEqual(how_not_to_be_seen1.get_formated_text(context),
                         expected)



if __name__ == '__main__':
    main()
