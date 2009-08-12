# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime

# Import from lpod
from xmlpart import odf_create_element, odf_element


def odf_create_note(note_class='footnote', note_id=None, citation=None,
                    body=None):
    """Create either a footnote or a endnote element with the given text,
    optionally referencing it using the given note_id.

    Arguments:

        note_class -- 'footnote' or 'endnote'

        note_id -- str

        citation -- unicode

        body -- an odf_element or an unicode object

    Return: odf_element
    """
    data = ('<text:note text:note-class="%s">'
              '<text:note-citation/>'
              '<text:note-body/>'
            '</text:note>')
    element = odf_create_element(data % note_class)
    if note_id is not None:
        element.set_attribute('text:id', note_id)
    if citation is not None:
        note_citation = element.get_element('text:note-citation')
        note_citation.set_text(citation)
    if body is not None:
        note_body = element.get_element('text:note-body')
        # Autocreate a paragraph if body = unicode
        if isinstance(body, unicode):
            note_body.set_text_content(body)
        elif isinstance(body, odf_element):
            note_body.append_element(body)
        else:
            raise ValueError, 'unexpected type for body: "%s"' % type(body)
    return element



def odf_create_annotation(text_or_element=None, creator=None, date=None):
    """Create an annotation element credited to the given creator with the
    given text, optionally dated (current date by default).

    Arguments:

        text -- unicode or odf_element

        creator -- unicode

        date -- datetime

    Return: odf_element
    """
    # TODO allow paragraph and text styles
    element = odf_create_element('<office:annotation/>')
    if text_or_element:
        if type(text_or_element) is unicode:
            element.set_text_content(text_or_element)
        elif isinstance(text_or_element, odf_element):
            element.append(text_or_element)
        else:
            raise TypeError, 'expected unicode or odf_element'
    #if creator is None:
        # TODO get the login name
    if creator:
        element.set_creator(creator)
    if date is None:
        date = datetime.now()
    element.set_date(date)
    return element
