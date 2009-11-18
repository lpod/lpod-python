# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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

# Import from lpod
from element import FIRST_CHILD
from element import register_element_class, odf_create_element, odf_element
from paragraph import odf_create_paragraph
from utils import Boolean



def odf_create_toc(name=u"Table of content", protected=True, style=None,
                   outline_level=10):
    data = '<text:table-of-content/>'
    element = odf_create_element(data)
    if name:
        element.set_attribute('text:name', name)
    element.set_attribute('text:protected', Boolean.encode(protected))
    if style:
        element.set_attribute('text:style-name', style)
    # A TOC is quite a complex hierarchy
    element.set_toc_outline_level(outline_level)
    return element



def odf_create_index_body():
    return odf_create_element('<text:index-body/>')



def odf_create_index_title(title=None):
    """Create an index title

    Arguments:

        title -- unicode

    Return: odf_element
    """
    element = odf_create_element('<text:index-title/>')
    if title:
        title = odf_create_paragraph(text=title)
        element.append_element(title)
    return element



class odf_toc(odf_element):

    def get_formated_text(self, context):
        index_body = self.get_element('text:index-body')

        if index_body is None:
            return u''

        result = []
        for element in index_body.get_children():
            if element.get_tagname() == 'text:index-title':
                for element in element.get_children():
                    result.append(element.get_formated_text(context))
                result.append(u'\n')
            else:
                result.append(element.get_formated_text(context))
        result.append('\n')
        return u''.join(result)


    def get_toc_outline_level(self):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            return None
        return source.get_attribute('text:outline-level')


    def set_toc_outline_level(self, level):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            source = odf_create_element('<text:table-of-content-source/>')
            self.insert_element(source, FIRST_CHILD)
        source.set_attribute('text:outline-level', str(int(level)))


    def auto_fill(self, document):
        """This function makes an update of the current TOC.

        Arguments:

        document -- odf_document
        """

        # Clean the old index-body
        index_body = self.get_element('text:index-body')
        if index_body:
            self.delete(index_body)
        index_body = odf_create_index_body()
        self.append_element(index_body)

        # Auto fill the index
        # 1. The title
        meta = document.get_xmlpart("meta")
        title = meta.get_title()
        if not title:
            title = u"(no title)"
        title = odf_create_index_title(title)
        index_body.append_element(title)
        #2. The section
        content = document.get_xmlpart("content")
        body = content.get_body()
        for number, heading in enumerate(body.get_heading_list(level=1)):
            title = u"%d. %s" % (number + 1, heading.get_text())
            paragraph = odf_create_paragraph(text=title)
            index_body.append_element(paragraph)



register_element_class('text:table-of-content', odf_toc)
