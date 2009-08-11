# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element


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
        result = []
        for obj in self.xpath('*|text()'):
            if type(obj) is unicode:
                result.append(obj)
            else:
                tag = obj.get_name()
                if tag in ('text:a', 'text:span'):
                    # XXX
                    obj.get_formated_text(context)

        # Insert the footnotes
        result.append(u'\n')
        for note in context['footnotes']:
            result.append(u'[%d] %s\n' % note)
        context['footnotes'] = []

        return u''.join(result)



register_element_class('text:p', odf_paragraph)
