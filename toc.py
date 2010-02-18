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


def odf_create_toc(title=u"Table of Contents", name=None, protected=True,
        outline_level=None, style=None, title_style=u"Contents_20_Heading"):
    """Create a table of contents. Default parameters are what most people
    use: Protected from manual modifications and not limited in title levels.

    The name is mandatory and derived automatically from the title if not
    given. Provide one in case of a conflict with other TOCs in the same
    document.

    Arguments:

        title -- unicode

        name -- unicode

        protected -- bool

        outline_level -- int

        style -- str

    Return: odf_toc
    """
    element = odf_create_element('<text:table-of-content/>')
    # XXX
    if name is None:
        name = u"%s1" % title
    element.set_toc_name(name)
    element.set_toc_protected(protected)
    if outline_level:
        element.set_toc_outline_level(outline_level)
    if style:
        element.set_toc_style(style)
    # Create the source template
    source = odf_create_toc_source(title=title, title_style=title_style)
    element.append_element(source)
    # Create the index body automatically with the index title
    if title:
        # This style is in the template document
        element.set_toc_title(title, text_style=title_style)
    return element



def odf_create_toc_source(title=None, outline_level=10,
        title_style=u"Contents_20_Heading", entry_style=u"Contents_20_%d"):
    element = odf_create_element('<text:table-of-content-source/>')
    element.set_outline_level(outline_level)
    if title:
        title_template = odf_create_element('<text:index-title-template/>')
        if title_style:
            # This style is in the template document
            title_template.set_text_style(title_style)
        title_template.set_text(title)
        element.append_element(title_template)
    for level in range(1, 11):
        template = odf_create_element('''<text:table-of-content-entry-template
          text:outline-level="%d">
          <text:index-entry-chapter/>
          <text:index-entry-text/>
          <text:index-entry-tab-stop style:type="right"
            style:leader-char="."/>
          <text:index-entry-page-number/>
         </text:table-of-content-entry-template>''' % level)
        if entry_style:
            template.set_text_style(entry_style % level)
        element.append_element(template)
    return element



def odf_create_index_body():
    return odf_create_element('<text:index-body/>')



def odf_create_index_title(title=None, name=None, style=None,
        text_style=None):
    """Create an index title

    Arguments:

        title -- unicode

    Return: odf_element
    """
    element = odf_create_element('<text:index-title/>')
    if title or text_style:
        title = odf_create_paragraph(text=title, style=text_style)
        element.append_element(title)
    if name:
        element.set_attribute('text:name', name)
    if style:
        element.set_text_style(style)
    return element



class odf_toc(odf_element):

    def get_formatted_text(self, context):
        index_body = self.get_element('text:index-body')

        if index_body is None:
            return u''

        if context["rst_mode"]:
            return u"\n.. contents::\n"

        result = []
        for element in index_body.get_children():
            if element.get_tagname() == 'text:index-title':
                for element in element.get_children():
                    result.append(element.get_formatted_text(context))
                result.append(u'\n')
            else:
                result.append(element.get_formatted_text(context))
        result.append('\n')
        return u''.join(result)


    def get_toc_name(self):
        return self.get_attribute('text:name')


    def set_toc_name(self, name):
        self.set_attribute('text:name', name)


    def get_toc_outline_level(self):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            return None
        return source.get_outline_level()


    def set_toc_outline_level(self, level):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            source = odf_create_element('<text:table-of-content-source/>')
            self.insert_element(source, FIRST_CHILD)
        source.set_outline_level(level)


    def is_toc_protected(self):
        return Boolean.decode(self.get_attribute('text:protected'))


    def set_toc_protected(self, protected):
        self.set_attribute('text:protected', Boolean.encode(protected))


    def get_toc_style(self):
        return self.get_text_style()


    def set_toc_style(self, style):
        self.set_text_style(style)


    def get_toc_body(self):
        return self.get_element('text:index-body')


    def set_toc_body(self, body=None):
        old_body = self.get_toc_body()
        if old_body is not None:
            self.delete_element(old_body)
        if body is None:
            body = odf_create_index_body()
        self.append_element(body)
        return body


    def get_toc_title(self):
        body = self.get_toc_body()
        if body is None:
            return None
        index_title = body.get_element('text:index-title')
        if index_title is None:
            return None
        return index_title.get_text_content()


    def set_toc_title(self, title, style=None, text_style=None):
        index_body = self.get_toc_body()
        if index_body is None:
            index_body = self.set_toc_body()
        index_title = index_body.get_element('text:index-title')
        if index_title is None:
            name = u"%s_Head" % self.get_toc_name()
            index_title = odf_create_index_title(title, name=name,
                    style=style, text_style=text_style)
            index_body.append_element(index_title)
        else:
            if style:
                index_title.set_text_style(style)
            paragraph = index_title.get_paragraph_by_position(0)
            if paragraph is None:
                paragraph = odf_create_paragraph()
                index_title.append_element(paragraph)
            if text_style:
                paragraph.set_text_style(text_style)
            paragraph.set_text(title)


    def toc_fill(self, document=None):
        """Fill the TOC with the titles found in the document. A TOC is not
        contextual so it will catch all titles before and after its insertion.
        If the TOC is not attached to a document, attach it beforehand or
        provide one as argument.

        Arguments:
        document -- odf_document
        """
        # Find the body
        if document is not None:
            body = document.get_body()
        else:
            body = self.get_body()
        if body is None:
            raise ValueError, "the TOC must be related to a document somehow"

        # Save the title
        index_body = self.get_toc_body()
        title = index_body.get_element('text:index-title')

        # Clean the old index-body
        index_body = self.set_toc_body()

        # Restore the title
        index_body.insert_element(title, position=0)

        # Auto-fill the index
        level_indexes = {}
        for heading in body.get_heading_list():
            level = heading.get_outline_level()
            number = []
            # 1. l < level
            for l in range(1, level):
                index = level_indexes.setdefault(l, 1)
                number.append(unicode(index))
            # 2. l == level
            index = level_indexes.setdefault(level, 0) + 1
            level_indexes[level] = index
            number.append(unicode(index))
            # 3. l > level
            for l in range(level + 1, 11):
                if level_indexes.has_key(l):
                    del level_indexes[l]
            number = u'.'.join(number)
            number += u'.'
            # Make the title with "1.2.3 Title" format
            title = u"%s %s" % (number, heading.get_text())
            paragraph = odf_create_paragraph(title)
            index_body.append_element(paragraph)



register_element_class('text:table-of-content', odf_toc)
