# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element



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
    return u''.join(result)



class odf_paragraph(odf_element):
    """Specialised element for paragraphs.
    """
    def insert_note(self, note_element,  note_class='footnote', note_id=None,
                    citation=None, body=None, *args, **kw):
        # TODO complain if the note has no note_id or citation
        # TODO note_id may be a function called with note_id(*args, **kw)
        raise NotImplementedError


    def insert_annotation(self, annotation_element, text_or_element=None,
                          creator=None, date=None):
        raise NotImplementedError


    def get_formated_text(self, context):
        result = [_get_formated_text(self, context, with_text=True)]
        result.append(u'\n')
        return u''.join(result)



register_element_class('text:p', odf_paragraph)
