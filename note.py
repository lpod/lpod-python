# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
from datetime import datetime
from types import FunctionType

# Import from lpod
from element import odf_create_element, odf_element, register_element_class


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
    element.set_class(note_class)
    if note_id is not None:
        element.set_id(note_id)
    if citation is not None:
        element.set_citation(citation)
    if body is not None:
        element.set_body(body)
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
    element = odf_create_element('office:annotation')
    element.set_body(text_or_element)
    if creator:
        element.set_dc_creator(creator)
    if date is None:
        date = datetime.now()
    element.set_dc_date(date)
    return element



class odf_note(odf_element):

    def get_class(self):
        return self.get_attribute('text:note-class')


    def set_class(self, note_class):
        return self.set_attribute('text:note-class', note_class)


    def get_id(self):
        return self.get_attribute('text:id')


    def set_id(self, note_id, *args, **kw):
        if type(note_id) is FunctionType:
            note_id = note_id(*args, **kw)
        return self.set_attribute('text:id', note_id)


    def get_citation(self):
        note_citation = self.get_element('text:note-citation')
        return note_citation.get_text()


    def set_citation(self, text):
        note_citation = self.get_element('text:note-citation')
        note_citation.set_text(text)


    def get_body(self):
        # XXX conflict with element.get_body
        note_body = self.get_element('text:note-body')
        return note_body.get_text_content()


    def set_body(self, text_or_element):
        note_body = self.get_element('text:note-body')
        if type(text_or_element) is unicode:
            note_body.set_text_content(text_or_element)
        elif isinstance(text_or_element, odf_element):
            note_body.clear()
            note_body.append(text_or_element)
        else:
            raise ValueError, 'unexpected type for body: "%s"' % type(
                    text_or_element)


    def check_validity(self):
        if not self.get_class():
            raise ValueError, 'note class must be "footnote" or "endnote"'
        if not self.get_id():
            raise ValueError, "notes must have an id"
        if not self.get_citation():
            raise ValueError, "notes must have a citation"
        if not self.get_body():
            # XXX error?
            pass



class odf_annotation(odf_element):

    def get_body(self):
        return self.get_text_content()


    def set_body(self, text_or_element):
        if type(text_or_element) is unicode:
            self.set_text_content(text_or_element)
        elif isinstance(text_or_element, odf_element):
            self.clear()
            self.append(text_or_element)
        else:
            raise TypeError, 'expected unicode or odf_element'


    #
    # Shortcuts expected to be reusable over several elements
    #

    def check_validity(self):
        if not self.get_body():
            raise ValueError, "annotation must have a body"
        if not self.get_dc_creator():
            raise ValueError, "annotation must have a creator"
        if not self.get_dc_date():
            self.set_dc_date(datetime.now())



register_element_class('text:note', odf_note)
register_element_class('office:annotation', odf_annotation)
