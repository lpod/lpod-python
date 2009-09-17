# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from re import compile, escape

# XXX Import from lxml
from lxml.etree import Element

# Import from lpod
from element import register_element_class, odf_element, odf_create_element
from element import FIRST_CHILD, ODF_NAMESPACES
from note import odf_create_note, odf_create_annotation


def _get_formated_text(element, context, with_text=True):
    result = []
    if with_text:
        objects = element.xpath('*|text()')
    else:
        objects = element.get_children()
    for obj in objects:
        if type(obj) is unicode:
            result.append(obj)
        else:
            tag = obj.get_name()
            # Good tags with text
            if tag in ('text:span', 'text:a', 'text:p'):
                result.append(_get_formated_text(obj, context,
                                                 with_text=True))
            # Footnote or endnote
            elif tag == 'text:note':
                note_class = obj.get_attribute('text:note-class')
                citation = obj.get_element('text:note-citation').get_text()
                body = obj.get_element('text:note-body').get_text().strip()
                for expected, container, marker in [
                    ('footnote', context['footnotes'], u"[%s]"),
                    ('endnote', context['endnotes'], u"(%s)")]:
                    if note_class == expected:
                        if not citation:
                            # Would only happen with hand-made documents
                            citation = len(container)
                        container.append((citation, body))
                        result.append(marker % citation)
            # Tabulation
            elif tag == 'text:tab':
                result.append(u'\t')
            else:
                result.append(obj.get_formated_text(context))
    return u''.join(result)



def odf_create_paragraph(text=None, style=None):
    """Create a paragraph element of the given style containing the optional
    given text.

    Arguments:

        style -- unicode

        text -- unicode

    Return: odf_element
    """
    element = odf_create_element('<text:p/>')
    if text:
        element.set_text(text)
    if style:
        element.set_attribute('text:style-name', style)
    return element



class odf_paragraph(odf_element):
    """Specialised element for paragraphs.
    """
    def get_formated_text(self, context):
        result = [_get_formated_text(self, context, with_text=True)]
        result.append(u'\n')
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
                note_element.set_note_class(note_class)
            if note_id:
                note_element.set_note_id(note_id, *args, **kw)
            if citation:
                note_element.set_note_citation(citation)
            if body:
                note_element.set_note_body(body)
        note_element.check_validity()
        if type(after) is unicode:
            self._insert_after(note_element, after)
        elif isinstance(after, odf_element):
            after.insert_element(note_element, FIRST_CHILD)
        else:
            self.insert_element(note_element, FIRST_CHILD)


    def insert_annotation(self, annotation_element=None, after=None,
                          body=None, creator=None, date=None):
        if annotation_element is None:
            annotation_element = odf_create_annotation(body,
                                                       creator=creator,
                                                       date=date)
        else:
            # XXX clone or modify the argument?
            if body:
                annotation_element.set_annotation_body(body)
            if creator:
                annotation_element.set_dc_creator(creator)
            if date:
                annotation_element.set_dc_date(date)
        annotation_element.check_validity()
        if type(after) is unicode:
            self._insert_after(annotation_element, after)
        elif isinstance(after, odf_element):
            after.insert_element(annotation_element, FIRST_CHILD)
        else:
            self.insert_element(annotation_element, FIRST_CHILD)


    def set_span(self, style, regex=None, offset=None, length=0):
        """Apply the given style to text content matching the regex OR the
        positional arguments offset and length.
        """
        # XXX bad: we expose lxml
        span_name = '{%s}span' % ODF_NAMESPACES['text']
        span_attrib = {'{%s}name' % ODF_NAMESPACES['style']: style}
        if offset:
            # XXX quickly hacking the offset
            text = self.get_text()
            if length:
                regex = text[offset:offset + length]
            else:
                regex = text[offset:]
            regex = escape(regex)
        if regex:
            pattern = compile(unicode(regex))
            element = self._odf_element__element
            for text in element.xpath('descendant-or-self::text()'):
                # Static information about the text node
                container = text.getparent()
                wrapper = container.getparent()
                is_text = text.is_text
                is_tail = text.is_tail
                # Group positions are calculated and static, so apply in
                # reverse order to preserve positions
                for group in reversed(list(pattern.finditer(text))):
                    start, end = group.span()
                    # Do not use the text node as it changes at each loop
                    if is_text:
                        text = container.text
                    else:
                        text = container.tail
                    before = text[:start]
                    match = text[start:end]
                    after = text[end:]
                    span = Element(span_name, attrib=span_attrib,
                                   nsmap=ODF_NAMESPACES)
                    span.text = match
                    span.tail = after
                    if is_text:
                        container.text = before
                        # Insert as first child
                        span.tail = after
                        container.insert(0, span)
                    else:
                        container.tail = before
                        # Insert as next sibling
                        index = wrapper.index(container)
                        wrapper.insert(index + 1, span)


    def set_link(self, url, regex=None, offset=None, length=0):
        """Make a link from text content matching the regex OR the positional
        arguments.
        """
        raise NotImplementedError



register_element_class('text:p', odf_paragraph)
