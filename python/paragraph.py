# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from table import odf_table
from xmlpart import register_element_class, odf_element



def _get_formated_text(element, context, with_text):
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
                result.append(_get_formated_text(obj, context, True))
            # Note
            elif tag == 'text:note':
                context['notes_counter'] += 1
                notes_counter = context['notes_counter']
                note_body = obj.get_element('text:note-body')
                text = _get_formated_text(note_body, context, False)
                text = text.strip()

                if obj.get_attribute('text:note-class') == 'footnote':
                    context['footnotes'].append((notes_counter, text))
                    result.append('[%d]' % notes_counter)
                else:
                    context['endnotes'].append((notes_counter, text))
                    result.append('(%d)' % notes_counter)
            # Table
            elif tag == 'table:table':
                table = odf_table(odf_element=obj)
                result.append(table.get_formated_text(context))

    # Paragraph => insert the notes
    if element.get_name() == 'text:p':
        result.append(u'\n')
        footnotes = context['footnotes']
        # XXX Sort the footnotes
        for note in footnotes:
            result.append(u'[%d] %s\n' % note)
        # Append a \n after the notes
        if footnotes:
            context['footnotes'] = []
            result.append(u'\n')

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
        return _get_formated_text(self, context, True)



register_element_class('text:p', odf_paragraph)
