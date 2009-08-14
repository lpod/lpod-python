# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from types import FunctionType

# Import from lpod
from utils import DateTime
from xmlpart import odf_create_element, odf_element, register_element_class


def odf_create_note(note_class='footnote', note_id=None, citation=None,
                    body=None):
    """Create either a footnote or a endnote element with the given text,
    optionally referencing it using the given note_id.

    Arguments:

        note_class -- 'footnote' or 'endnote'

        note_id -- str

        citation -- unicode

        body -- unicode or odf_element

    Return: odf_element
    """
    data = ('<text:note>'
              '<text:note-citation/>'
              '<text:note-body/>'
            '</text:note>')
    element = odf_create_element(data)
    element.set_note_class(note_class)
    if note_id is not None:
        element.set_note_id(note_id)
    if citation is not None:
        element.set_note_citation(citation)
    if body is not None:
        element.set_note_body(body)
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
    element.set_annotation_body(text_or_element)
    if creator:
        element.set_annotation_creator(creator)
    if date is None:
        date = datetime.now()
    element.set_annotation_date(date)
    return element



class odf_note(odf_element):

    def get_note_class(self):
        return self.get_attribute('text:note-class')


    def set_note_class(self, note_class):
        return self.set_attribute('text:note-class', note_class)


    def get_note_id(self):
        # XXX maybe generic -> "get_text_id"?
        return self.get_attribute('text:id')


    def set_note_id(self, note_id, *args, **kw):
        # XXX maybe generic -> "set_text_id"?
        if type(note_id) is FunctionType:
            note_id = note_id(*args, **kw)
        return self.set_attribute('text:id', note_id)


    def get_note_citation(self):
        note_citation = self.get_element('text:note-citation')
        return note_citation.get_text()


    def set_note_citation(self, text):
        note_citation = self.get_element('text:note-citation')
        note_citation.set_text(text)


    def get_note_body(self):
        note_body = self.get_element('text:note-body')
        children = note_body.get_children()
        if children:
            return children[0]
        return None


    def set_note_body(self, text_or_element):
        note_body = self.get_element('text:note-body')
        if type(text_or_element) is unicode:
            note_body.set_text_content(text_or_element)
        elif isinstance(text_or_element, odf_element):
            note_body.append_element(text_or_element)
        else:
            raise ValueError, 'unexpected type for body: "%s"' % type(
                    text_or_element)


    def check_validity(self):
        if not self.get_note_class():
            raise ValueError, 'note class must be "footnote" or "endnote"'
        if not self.get_note_id():
            raise ValueError, "notes must have an id"
        if not self.get_note_citation():
            raise ValueError, "notes must have a citation"
        if not self.get_note_body():
            # XXX error?
            pass



class odf_annotation(odf_element):

    def get_annotation_body(self):
        # FIXME improvizing here
        return self.get_element('text:p')


    def set_annotation_body(self, text_or_element):
        if type(text_or_element) is unicode:
            self.set_text_content(text_or_element)
        elif isinstance(text_or_element, odf_element):
            self.append(text_or_element)
        else:
            raise TypeError, 'expected unicode or odf_element'


    #
    # Shortcuts expected to be reusable over several elements
    #

    def get_annotation_creator(self):
        dc_creator = self.get_element('dc:creator')
        if dc_creator is None:
            return None
        return dc_creator.get_text()


    def set_annotation_creator(self, creator):
        dc_creator = self.get_element('dc:creator')
        if dc_creator is None:
            dc_creator = odf_create_element('<dc:creator/>')
            self.append_element(dc_creator)
        dc_creator.set_text(creator)


    def get_annotation_date(self):
        dc_date = self.get_element('dc:date')
        if dc_date is None:
            return None
        date = dc_date.get_text()
        return DateTime.decode(date)


    def set_annotation_date(self, date):
        dc_date = self.get_element('dc:date')
        if dc_date is None:
            dc_date = odf_create_element('<dc:date/>')
            self.append_element(dc_date)
        dc_date.set_text(DateTime.encode(date))


    def check_validity(self):
        if not self.get_annotation_body():
            raise ValueError, "annotation must have a body"
        if not self.get_annotation_creator():
            raise ValueError, "annotation must have a creator"
        if not self.get_annotation_date():
            self.set_annotation_date(datetime.now())



register_element_class('text:note', odf_note)
register_element_class('office:annotation', odf_annotation)
