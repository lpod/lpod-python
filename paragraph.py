# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from re import compile, escape, UNICODE

# Import from lpod
from bookmark import odf_create_bookmark, odf_create_bookmark_start
from bookmark import odf_create_bookmark_end
from element import FIRST_CHILD, odf_text
from element import register_element_class, odf_element, odf_create_element
from note import odf_create_note, odf_create_annotation
from style import odf_style


def _get_formatted_text(element, context, with_text=True):
    document = context['document']
    rst_mode = context['rst_mode']

    result = []
    if with_text:
        objects = element.xpath('*|text()')
    else:
        objects = element.get_children()
    for obj in objects:
        if type(obj) is odf_text:
            result.append(obj)
        else:
            tag = obj.get_tag()
            # Good tags with text
            if tag in ('text:a', 'text:p'):
                result.append(_get_formatted_text(obj, context,
                                                 with_text=True))
            # Try to convert some styles in rst_mode
            elif tag == 'text:span':
                # XXX Move this part in span.py ??
                text = _get_formatted_text(obj, context, with_text=True)
                if not rst_mode:
                    result.append(text)
                    continue
                if not text.strip():
                    result.append(text)
                    continue
                style = obj.get_style()
                if style is None:
                    result.append(text)
                    continue
                style = document.get_style("text", style)
                properties = style.get_properties()
                if properties is None:
                    result.append(text)
                    continue
                # Compute before, text and after
                before = ''
                for c in text:
                    if c.isspace():
                        before += c
                    else:
                        break
                after = ''
                for c in reversed(text):
                    if c.isspace():
                        after = c + after
                    else:
                        break
                text = text.strip()
                # Bold ?
                if properties.get('fo:font-weight') == 'bold':
                    result.append(before)
                    result.append('**')
                    result.append(text)
                    result.append('**')
                    result.append(after)
                    continue
                # Italic ?
                if properties.get('fo:font-style') == 'italic':
                    result.append(before)
                    result.append('*')
                    result.append(text)
                    result.append('*')
                    result.append(after)
                    continue
                # Unknown style, ...
                result.append(before)
                result.append(text)
                result.append(after)
            # Footnote or endnote
            elif tag == 'text:note':
                note_class = obj.get_class()
                container = {'footnote': context['footnotes'],
                             'endnote': context['endnotes']}[note_class]
                citation = obj.get_citation()
                if not citation:
                    # Would only happen with hand-made documents
                    citation = len(container)
                body = obj.get_body()
                container.append((citation, body))
                if rst_mode:
                    marker = {'footnote': u" [#]_ ",
                              'endnote': u" [*]_ "}[note_class]
                else:
                    marker = {'footnote': u"[{citation}]",
                              'endnote': u"({citation})"}[note_class]
                result.append(marker.format(citation=citation))
            # Annotations
            elif tag == 'office:annotation':
                context['annotations'].append(obj.get_body())
                if rst_mode:
                    result.append(' [#]_ ')
                else:
                    result.append('[*]')
            # Tabulation
            elif tag == 'text:tab':
                result.append(u'\t')
            # Line break
            elif tag == 'text:line-break':
                if rst_mode:
                    result.append(u"\n|")
                else:
                    result.append(u"\n")
            else:
                result.append(obj.get_formatted_text(context))
    return u''.join(result)



def odf_create_line_break():
    return odf_create_element('text:line-break')



def odf_create_undividable_space(number=1):
    """
    Arguments:

        number -- int

    Return odf_element
    """
    # FIXME what is number?
    element = odf_create_element('text:s')
    element.set_attribute('text:c', str(number))
    return element



def odf_create_paragraph(text_or_element=None, style=None):
    """Create a paragraph element of the given style containing the optional
    given text.

    Arguments:

        text -- unicode or odf_element

        style -- unicode

    Return: odf_element
    """
    paragraph = odf_create_element('text:p')
    if isinstance(text_or_element, odf_element):
        paragraph.append(text_or_element)
    else:
        paragraph.set_text(text_or_element)
    if style is not None:
        paragraph.set_style(style)
    return paragraph



class odf_paragraph(odf_element):
    """Specialised element for paragraphs.
    """
    def get_style(self):
        return self.get_attribute('text:style-name')


    def set_style(self, name):
        return self.set_style_attribute('text:style-name', name)


    def get_text_style(self):
        return self.get_attribute('text:style-name')


    def set_text_style(self, name):
        return self.set_style_attribute('text:style-name', name)


    def get_formatted_text(self, context):
        result = [_get_formatted_text(self, context, with_text=True)]
        result.append(u'\n\n')
        return u''.join(result)


    def insert_note(self, note_element=None, after=None,
                    note_class='footnote', note_id=None, citation=None,
                    body=None, *args, **kw):
        if note_element is None:
            note_element = odf_create_note(note_class=note_class,
                                           note_id=note_id,
                                           citation=citation, body=body)
        else:
            # XXX clone or modify the argument?
            if note_class:
                note_element.set_class(note_class)
            if note_id:
                note_element.set_id(note_id, *args, **kw)
            if citation:
                note_element.set_citation(citation)
            if body:
                note_element.set_body(body)
        note_element.check_validity()
        if type(after) is unicode:
            self._insert(note_element, after=after)
        elif isinstance(after, odf_element):
            after.insert(note_element, FIRST_CHILD)
        else:
            self.insert(note_element, FIRST_CHILD)


    def insert_annotation(self, annotation_element=None, after=None,
                          body=None, creator=None, date=None):
        if annotation_element is None:
            annotation_element = odf_create_annotation(body,
                                                       creator=creator,
                                                       date=date)
        else:
            # XXX clone or modify the argument?
            if body:
                annotation_element.set_body(body)
            if creator:
                annotation_element.set_dc_creator(creator)
            if date:
                annotation_element.set_dc_date(date)
        annotation_element.check_validity()
        if type(after) is unicode:
            self._insert(annotation_element, after=after)
        elif isinstance(after, odf_element):
            after.insert(annotation_element, FIRST_CHILD)
        else:
            self.insert(annotation_element, FIRST_CHILD)


    def insert_variable(self, variable_element,  after):
        self._insert(variable_element, after=after)


    def set_span(self, style, regex=None, offset=None, length=0):
        """Apply the given style to text content matching the regex OR the
        positional arguments offset and length.

        Arguments:

            style -- style element or name

            regex -- unicode regular expression

            offset -- int

            length -- int
        """
        # XXX FIX ME cyclic import
        from span import odf_create_span

        if isinstance(style, odf_style):
            style = style.get_name()
        if offset:
            # XXX quickly hacking the offset
            text = self.get_text()
            if length:
                regex = text[offset:offset + length]
            else:
                regex = text[offset:]
            regex = escape(regex)
        if regex:
            pattern = compile(unicode(regex), UNICODE)
            for text in self.xpath('descendant::text()'):
                # Static information about the text node
                container = text.get_parent()
                wrapper = container.get_parent()
                is_text = text.is_text()
                # Group positions are calculated and static, so apply in
                # reverse order to preserve positions
                for group in reversed(list(pattern.finditer(text))):
                    start, end = group.span()
                    # Do not use the text node as it changes at each loop
                    if is_text:
                        text = container.get_text()
                    else:
                        text = container.get_tail()
                    before = text[:start]
                    match = text[start:end]
                    after = text[end:]
                    span = odf_create_span(match, style=style)
                    span.set_tail(after)
                    if is_text:
                        container.set_text(before)
                        # Insert as first child
                        container.insert(span, position=0)
                    else:
                        container.set_tail(before)
                        # Insert as next sibling
                        index = wrapper.index(container)
                        wrapper.insert(span, position=index + 1)


    def set_link(self, url, regex=None, offset=None, length=0):
        """Make a link from text content matching the regex OR the positional
        arguments.
        """
        raise NotImplementedError


    def set_bookmark(self, name, before=None, after=None, position=0,
                     role=None, content=None):
        """Insert a bookmark before or after the characters in the text which
        match the regex before/after. When the regex matches more of one part
        of the text, position can be set to choose which part must be used.
        If before and after are None, we use only position that is the number
        of characters. So, by default, this function inserts a bookmark
        before the first character of the content. Role can be None, "start"
        or "end", we insert respectively a position bookmark a bookmark-start
        or a bookmark-end. If content is not None these 2 calls are
        equivalent::

          paragraph.set_bookmark("bookmark", content="xyz")

        and::

          paragraph.set_bookmark("bookmark", before="xyz", role="start")
          paragraph.set_bookmark("bookmark", after="xyz", role="end")

        If position is a 2-tuple, these 2 calls are equivalent::

          paragraph.set_bookmark("bookmark", position=(10, 20))

        and::

          paragraph.set_bookmark("bookmark", position=10, role="start")
          paragraph.set_bookmark("bookmark", position=20, role="end")

        Arguments:

            name -- str

            before -- unicode regex

            after -- unicode regex

            position -- int or (int, int)

            role -- None, "start" or "end"

            content -- unicode regex
        """
        # With "content" => automatically insert a "start" and an "end"
        # bookmark
        if (before is None and after is None and role is None
                and content is not None and type(position) is int):
            # Start
            start = odf_create_bookmark_start(name)
            self._insert(start, before=content, position=position)
            # End
            end = odf_create_bookmark_end(name)
            self._insert(end, after=content, position=position)
            return start, end

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        # bookmark
        if (before is None and after is None and role is None
                and content is None and type(position) is tuple):
            # Start
            start = odf_create_bookmark_start(name)
            self._insert(start, position=position[0])
            # End
            end = odf_create_bookmark_end(name)
            self._insert(end, position=position[1])
            return start, end

        # Without "content" nor "position"
        if content is not None or type(position) is not int:
            raise ValueError, "bad arguments"

        # Role
        if role is None:
            bookmark = odf_create_bookmark(name)
        elif role == "start":
            bookmark = odf_create_bookmark_start(name)
        elif role == "end":
            bookmark = odf_create_bookmark_end(name)
        else:
            raise ValueError, "bad arguments"

        # Insert
        self._insert(bookmark, before=before, after=after, position=position)

        return bookmark



register_element_class('text:p', odf_paragraph)
