# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the Standard Library

# Import from lpod
from element import register_element_class, odf_element, odf_create_element
from element import FIRST_CHILD, PREV_SIBLING, NEXT_SIBLING
from paragraph import odf_create_paragraph
from utils import _get_element, _get_elements, obsolete, isiterable


def odf_create_list_item(text_or_element=None):
    """Create a list item element.

    Sending a unicode text is just a shortcut for the most common case. To
    create a list item with several paragraphs or anything else (except
    tables), first create an empty list item, and fill it using the other
    "odf_create_*" functions.

    Arguments:

        text -- unicode or odf_element

    Return: odf_element
    """
    element = odf_create_element('text:list-item')
    if type(text_or_element) is unicode:
        element.set_text_content(text_or_element)
    elif isinstance(text_or_element, odf_element):
        element.append(text_or_element)
    elif text_or_element is not None:
        raise TypeError, "expected unicode or odf_element"
    return element



def odf_create_list(text=[], style=None):
    """Create a list element.

    Arguments:

        text -- a list of unicode

        style -- unicode

    The "text" argument is just a shortcut for the most common case. To create
    complex lists, first create an empty list, and fill it using built list
    items.

    Return: odf_element
    """
    element = odf_create_element('text:list')
    for value in text:
        element.append(odf_create_list_item(text_or_element=value))
    if style is not None:
        element.set_style(style)
    return element



class odf_list(odf_element):
    """Specialised element for lists.
    """
    def get_style(self):
        return self.get_attribute('text:style-name')


    def set_style(self, name):
        return self.set_style_attribute('text:style-name', name)


    def get_items(self, content=None):
        """Return all the list items that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_paragraph
        """
        return _get_elements(self, 'text:list-item', content=content)

    get_item_list = obsolete('get_item_list', get_items)


    def get_item(self, position=0, content=None):
        """Return the list item that matches the criteria. In nested lists,
        return the list item that really contains that content.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_element or None if not found
        """
        # Custom implementation because of nested lists
        if content:
            # Don't search recursively but on the very own paragraph(s) of
            # each list item
            for paragraph in self.get_elements('descendant::text:p'):
                if paragraph.match(content):
                    return paragraph.get_element('parent::text:list-item')
            return None
        return _get_element(self, 'text:list-item', position)


    def set_header(self, text_or_element):
        if not isiterable(text_or_element):
            text_or_element = [text_or_element]
        # Remove existing header
        for element in self.get_elements('text:p'):
            self.delete(element)
        for paragraph in reversed(text_or_element):
            if type(paragraph) is unicode:
                paragraph = odf_create_paragraph(paragraph)
            self.insert(paragraph, FIRST_CHILD)


    def insert_item(self, item, position=None, before=None, after=None):
        # Check if the item is already a list-item
        tag_name = item.get_tag() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)

        if before is not None:
            before.insert(item, xmlposition=PREV_SIBLING)
        elif after is not None:
            after.insert(item, xmlposition=NEXT_SIBLING)
        elif position is not None:
            self.insert(item, position=position)
        else:
            raise ValueError, "position must be defined"


    def append_item(self, item):
        # Check if the item is already a list-item
        tag_name = item.get_tag() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)
        self.append(item)


    def get_formatted_text(self, context):
        rst_mode = context["rst_mode"]

        result = []
        if rst_mode:
            result.append('\n')
        for list_item in self.get_elements('text:list-item'):
            textbuf = []
            for child in list_item.get_children():
                text = child.get_formatted_text(context)
                tag = child.get_tag()
                if tag == 'text:h':
                    # A title in a list is a bug
                    return text
                elif tag == 'text:list':
                    if not text.lstrip().startswith(u'-'):
                        # If the list didn't indent, don't either
                        # (inner title)
                        return text
                textbuf.append(text)
            textbuf = u''.join(textbuf)
            textbuf = textbuf.strip('\n')
            # Indent the text
            textbuf = u'- %s\n' % textbuf.replace(u'\n', u'\n  ')
            result.append(textbuf)
        if rst_mode:
            result.append('\n')
        return u''.join(result)



register_element_class('text:list', odf_list)
