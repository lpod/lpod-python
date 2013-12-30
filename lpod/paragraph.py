# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
import re
from functools import wraps  # for keeping trace of docstring with decorators

# Import from lpod
from bookmark import odf_create_bookmark, odf_create_bookmark_start
from bookmark import odf_create_bookmark_end
from element import FIRST_CHILD, NEXT_SIBLING
from element import register_element_class, odf_element, odf_create_element
from paragraph_base import paragraph_base
from paragraph_base import odf_create_spaces
from paragraph_base import odf_create_tabulation
from paragraph_base import odf_create_line_break

from note import odf_create_note
from note import odf_create_annotation, odf_create_annotation_end
from reference import odf_create_reference_mark, odf_create_reference_mark_start
from reference import odf_create_reference_mark_end, odf_create_reference
from style import odf_style
from link import odf_create_link




def _odf_create_span(text=None, style=None):
    """Create a span element of the given style containing the optional
    given text.

    Arguments:

        style -- unicode

        text -- unicode

    Return: odf_element
    """
    element = odf_create_element('text:span')
    if text:
        element.set_text(text)
    if style:
        element.set_style(style)
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



def _by_regex_offset(method):
    @wraps(method)
    def wrapper(element, *args, **kwargs):
        """Insert the result of method(element, ...) at the place matching the
        regex OR the positional arguments offset and length.

        Arguments:

            method -- wrapped method

            element -- self

            regex -- unicode regular expression

            offset -- int

            length -- int
        """
        offset = kwargs.get('offset', None)
        regex = kwargs.get('regex', None)
        if offset:
            length = kwargs.get('length', 0)
            counted = 0
            for text in element.xpath("//text()"):
                if len(text) + counted <= offset:
                    counted += len(text)
                    continue
                if length > 0:
                    length = min(length, len(text))
                else:
                    length = len(text)
                # Static information about the text node
                container = text.get_parent()
                upper = container.get_parent()
                is_text = text.is_text()
                start = offset - counted
                end = start + length
                # Do not use the text node as it changes at each loop
                if is_text:
                    text = container.get_text()
                else:
                    text = container.get_tail()
                before = text[:start]
                match = text[start:end]
                tail = text[end:]
                result = method(element, match, tail, *args, **kwargs)
                if is_text:
                    container.set_text(before)
                    # Insert as first child
                    container.insert(result, position=0)
                else:
                    container.set_tail(before)
                    # Insert as next sibling
                    index = upper.index(container)
                    upper.insert(result, position=index + 1)
                return
        if regex:
            pattern = re.compile(unicode(regex), re.UNICODE)
            for text in element.xpath('descendant::text()'):
                # Static information about the text node
                container = text.get_parent()
                upper = container.get_parent()
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
                    tail = text[end:]
                    result = method(element, match, tail, *args, **kwargs)
                    if is_text:
                        container.set_text(before)
                        # Insert as first child
                        container.insert(result, position=0)
                    else:
                        container.set_tail(before)
                        # Insert as next sibling
                        index = upper.index(container)
                        upper.insert(result, position=index + 1)
    return wrapper



class odf_paragraph(paragraph_base):
    """Specialised element for paragraphs <text:p>. The <text:p> element
    represents a paragraph, which is the basic unit of text in an OpenDocument
    file.
    """

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
            self._insert(note_element, after=after, main_text=True)
        elif isinstance(after, odf_element):
            after.insert(note_element, FIRST_CHILD)
        else:
            self.insert(note_element, FIRST_CHILD)


    def insert_annotation(self, annotation_element=None, before=None,
                          after=None, position=0, content=None,
                          body=None, creator=None, date=None):
        """Insert an annotation, at the position defined by the regex (before,
        after, content) or by positionnal argument (position). If content is
        provided, the annotation covers the full content regex. Else, the
        annotation is positionned either 'before' or 'after' provided regex.

        If content is an odf element (ie: paragraph, span, ...), the full inner
        content is covered by the annotation (of the position just after if
        content is a single empty tag).

        If content/before or after exists (regex) and return a group of matching
        positions, the position value is the index of matching place to use.

        annotation_element can contain a previously created annotation, else
        the annotation is created from the body, creator and optional date
        (current date by default).

        Arguments:

            annotation_element -- annotation element or name

            before -- unicode regular expression or None

            after -- unicode regular expression or None

            content -- unicode regular expression or None, or odf_element

            position -- int or tuple of int

            body -- unicode or odf_element

            creator -- unicode

            date -- datetime
        """

        if annotation_element is None:
            annotation_element = odf_create_annotation(body, creator=creator,
                                                       date=date, parent=self)
        else:
            # XXX clone or modify the argument?
            if body:
                annotation_element.set_body(body)
            if creator:
                annotation_element.set_dc_creator(creator)
            if date:
                annotation_element.set_dc_date(date)
        annotation_element.check_validity()

        # special case: content is an odf element (ie: a paragraph)
        if isinstance(content, odf_element):
            if content.is_empty():
                content.insert(annotation_element, xmlposition=NEXT_SIBLING)
                return annotation_element
            content.insert(annotation_element, start=True)
            annotation_end = odf_create_annotation_end(annotation_element)
            content.append(annotation_end)
            return annotation_element

        # special case
        if isinstance(after, odf_element):
            after.insert(annotation_element, FIRST_CHILD)
            return annotation_element

        # With "content" => automatically insert a "start" and an "end"
        # bookmark
        if (before is None and after is None and content is not None
                and type(position) is int):
            # Start tag
            self._insert(annotation_element, before=content, position=position,
                         main_text=True)
            # End tag
            annotation_end = odf_create_annotation_end(annotation_element)
            self._insert(annotation_end, after=content, position=position,
                         main_text=True)
            return annotation_element

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        # bookmark
        if (before is None and after is None and content is None
                and type(position) is tuple):
            # Start
            self._insert(annotation_element, position=position[0],
                         main_text=True)
            # End
            annotation_end = odf_create_annotation_end(annotation_element)
            self._insert(annotation_end, position=position[1], main_text=True)
            return annotation_element

        # Without "content" nor "position"
        if content is not None or type(position) is not int:
            raise ValueError("bad arguments")

        # Insert
        self._insert(annotation_element, before=before, after=after,
                     position=position, main_text=True)
        return annotation_element


    def insert_annotation_end(self, annotation_element, before=None,
                          after=None, position=0):
        """Insert an annotation end tag for an existing annotation. If some end
        tag already exists, replace it. Annotation end tag is set at the
        position defined by the regex (before or after).

        If content/before or after (regex) returns a group of matching
        positions, the position value is the index of matching place to use.

        Arguments:

            annotation_element -- annotation element (mandatory)

            before -- unicode regular expression or None

            after -- unicode regular expression or None

            position -- int
        """

        if annotation_element is None:
            raise ValueError
        if annotation_element.get_tag() != u'office:annotation':
            raise ValueError("Not a 'office:annotation' element")

        # remove existing end tag
        name = annotation_element.get_name()
        existing_end_tag = self.get_annotation_end(name=name)
        if existing_end_tag:
            existing_end_tag.delete()

        # create the end tag
        end_tag = odf_create_annotation_end(annotation_element)

        # Insert
        self._insert(end_tag, before=before, after=after,
                     position=position, main_text=True)
        return end_tag


    def set_reference_mark(self, name, before=None, after=None, position=0,
                           content=None):
        """Insert a reference mark, at the position defined by the regex
        (before, after, content) or by positionnal argument (position). If
        content is provided, the annotation covers the full range content regex
        (instances of odf_reference_mark_start and odf_reference_mark_end are
        created). Else, an instance of odf_reference_mark is positionned either
        'before' or 'after' provided regex.

        If content is an odf element (ie: paragraph, span, ...), the full inner
        content is referenced (of the position just after if content is a single
        empty tag).

        If content/before or after exists (regex) and return a group of matching
        positions, the position value is the index of matching place to use.

        Name is mandatory and shall be unique in the document for the preference
        mark range.

        Arguments:

            name -- unicode

            before -- unicode regular expression or None

            after -- unicode regular expression or None, or odf_element

            content -- unicode regular expression or None, or odf_element

            position -- int or tuple of int

        Return: the created reference or reference start
        """
        # special case: content is an odf element (ie: a paragraph)
        if isinstance(content, odf_element):
            if content.is_empty():
                reference = odf_create_reference_mark(name)
                content.insert(reference, xmlposition=NEXT_SIBLING)
                return reference
            reference_start = odf_create_reference_mark_start(name)
            content.insert(reference_start, start=True)
            reference_end = odf_create_reference_mark_end(name)
            content.append(reference_end)
            return reference_start
        # With "content" => automatically insert a "start" and an "end"
        # reference
        if (before is None and after is None and content is not None
                and type(position) is int):
            # Start tag
            reference_start = odf_create_reference_mark_start(name)
            self._insert(reference_start, before=content, position=position,
                         main_text=True)
            # End tag
            reference_end = odf_create_reference_mark_end(name)
            self._insert(reference_end, after=content, position=position,
                         main_text=True)
            return reference_start

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        if (before is None and after is None and content is None
                and type(position) is tuple):
            # Start
            reference_start = odf_create_reference_mark_start(name)
            self._insert(reference_start, position=position[0],
                         main_text=True)
            # End
            reference_end = odf_create_reference_mark_end(name)
            self._insert(reference_end, position=position[1], main_text=True)
            return reference_start

        # Without "content" nor "position"
        if content is not None or type(position) is not int:
            raise ValueError("bad arguments")

        # Insert a positional reference mark
        reference = odf_create_reference_mark(name)
        self._insert(reference, before=before, after=after,
                     position=position, main_text=True)
        return reference


    def set_reference_mark_end(self, reference_mark, before=None,
                          after=None, position=0):
        """Insert/move a reference_mark_end for an existing reference mark. If
        some end tag already exists, replace it. Reference tag is set at the
        position defined by the regex (before or after).

        If content/before or after (regex) returns a group of matching
        positions, the position value is the index of matching place to use.

        Arguments:

            reference_mark -- reference element (mandatory)

            before -- unicode regular expression or None

            after -- unicode regular expression or None

            position -- int
        """
        if reference_mark.get_tag() not in (u'text:reference-mark',
                                            u'text:reference-mark-start'):
            raise ValueError(
            "Not a 'text:reference-mark or text:reference-mark-start' element")
        name = reference_mark.get_name()
        if reference_mark.get_tag() == u'text:reference-mark':
            # change it to a range reference:
            reference_mark._set_tag_raw('text:reference-mark-start')

        existing_end_tag = self.get_reference_mark_end(name=name)
        if existing_end_tag:
            existing_end_tag.delete()

        # create the end tag
        end_tag = odf_create_reference_mark_end(name)

        # Insert
        self._insert(end_tag, before=before, after=after,
                     position=position, main_text=True)
        return end_tag


    def insert_variable(self, variable_element,  after):
        self._insert(variable_element, after=after, main_text=True)


    @_by_regex_offset
    def set_span(self, match, tail, style, regex=None, offset=None, length=0):
        """
        set_span(style, regex=None, offset=None, length=0)
        Apply the given style to text content matching the regex OR the
        positional arguments offset and length.

        (match, tail: provided by decorator)

        Arguments:

            style -- style element or name

            regex -- unicode regular expression

            offset -- int

            length -- int
        """
        if isinstance(style, odf_style):
            style = style.get_name()
        span = _odf_create_span(match, style=style)
        span.set_tail(tail)
        return span


    def remove_spans(self, keep_heading=True):
        """Send back a copy of the element, without span styles.
        If keep_heading is True (default), the first level heading style is left
        unchanged.
        """
        strip = ('text:span',)
        if keep_heading:
            protect = ('text:h',)
        else:
            protect = None
        return self.strip_tags(strip=strip, protect=protect)


    def remove_span(self, spans):
        """Send back a copy of the element, the spans (not a clone) removed.

        Arguments:

            spans -- odf_element or list of odf_element
        """
        return self.strip_elements(spans)


    @_by_regex_offset
    def set_link(self, match, tail, url, regex=None, offset=None, length=0):
        """
        set_link(url, regex=None, offset=None, length=0)
        Make a link to the provided url from text content matching the regex
        OR the positional arguments offset and length.

        (match, tail: provided by decorator)

        Arguments:


            url -- unicode

            regex -- unicode regular expression

            offset -- int

            length -- int
        """
        link = odf_create_link(url, text=match)
        link.set_tail(tail)
        return link


    def remove_links(self):
        """Send back a copy of the element, without links tags.
        """
        strip = ('text:a',)
        return self.strip_tags(strip=strip)


    def remove_link(self, links):
        """Send back a copy of the element, the sub_links (not a clone) removed.

        Arguments:

            links -- odf_link or list of odf_link
        """
        return self.strip_elements(links)


    def insert_reference(self, name, ref_format='', before=None, after=None,
                         position=0, display=None):
        """Create and Insert a reference to a content marked by a reference
        mark. The odf_reference element (<text:reference-ref>) represents a
        field that references a <text:reference-mark-start> or
        <text:reference-mark> element. Its text:reference-format attribute
        specifies what is displayed from the referenced element. Default is
        'page' Actual content is not automatically updated except for the 'text'
        format.

        Name is mandatory and should represent an existing reference mark of the
        document.
        The ref_format is the type of formt reference : default is 'page'. The
        reference is inserted the position defined by the regex (before/after),
        or by positionnal argument (position). If 'display' is provided, it will
        be used as the text value for the reference.
        If after is an odf element, the reference is inserted as first child of
        this element.

        Arguments:

            name -- unicode

            ref_format -- one of : 'chapter', 'direction', 'page', 'text',
                                    'caption', 'category-and-value', 'value',
                                    'number', 'number-all-superior',
                                    'number-no-superior'

            before -- unicode regular expression or None

            after -- unicode regular expression or odf element or None

            position -- int

            display -- unicode or None
        """
        reference = odf_create_reference(name, ref_format)
        if display is None and ref_format == 'text':
            # get reference content
            body = self.get_document_body()
            if not body:
                body = self.get_root()
            mark = body.get_reference_mark(name=name)
            if mark:
                display = mark.get_referenced_text()
        if not display:
            display = u' '
        reference.set_text(display)
        if isinstance(after, odf_element):
            after.insert(reference, FIRST_CHILD)
        else:
            self._insert(reference, before=before, after=after,
                         position=position, main_text=True)


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
            self._insert(start, before=content, position=position,
                         main_text=True)
            # End
            end = odf_create_bookmark_end(name)
            self._insert(end, after=content, position=position,
                         main_text=True)
            return start, end

        # With "(int, int)" =>  automatically insert a "start" and an "end"
        # bookmark
        if (before is None and after is None and role is None
                and content is None and type(position) is tuple):
            # Start
            start = odf_create_bookmark_start(name)
            self._insert(start, position=position[0], main_text=True)
            # End
            end = odf_create_bookmark_end(name)
            self._insert(end, position=position[1], main_text=True)
            return start, end

        # Without "content" nor "position"
        if content is not None or type(position) is not int:
            raise ValueError("bad arguments")

        # Role
        if role is None:
            bookmark = odf_create_bookmark(name)
        elif role == "start":
            bookmark = odf_create_bookmark_start(name)
        elif role == "end":
            bookmark = odf_create_bookmark_end(name)
        else:
            raise ValueError("bad arguments")

        # Insert
        self._insert(bookmark, before=before, after=after, position=position,
                     main_text=True)

        return bookmark



class odf_span(odf_paragraph):
    pass



register_element_class('text:p', odf_paragraph)
register_element_class('text:span', odf_span)
