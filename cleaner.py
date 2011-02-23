#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
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
from lpod.element import PREV_SIBLING



def _test_text_h(document):
    body = document.get_body()

    for heading in body.get_headings():
        parent = heading.get_parent()
        # Ok ?
        if parent.get_tag() != 'office:text':
            return 'nested "text:h" detected'

    return True


def _fix_text_h(document):
    body = document.get_body()
    error_nb = 0

    error_detected = True
    while error_detected:
        error_detected = False
        for heading in body.get_headings():
            parent = heading.get_parent()
            # Ok ?
            if parent.get_tag() == 'office:text':
                continue

            # Else, ...
            error_detected = True
            error_nb += 1

            # XXX The texts are not children ??
            # We move all elements outside this "bad" container
            for element in parent.get_children():
                parent.insert(element, xmlposition=PREV_SIBLING)
            # And we remove it
            parent.delete()

    return error_nb



def test_document(document):
    """Test if the document is valid.

       Returns: True if the document is valid
                or a <str> otherwise. This str describes the problem.
    """

    # Test, ...
    return _test_text_h(document)



def clean_document(document):
    """This method returns a cloned, cleaned document and the number of fixed
       errors"""
    outdoc = document.clone()

    # Fix, ...
    error_nb = _fix_text_h(outdoc)

    return outdoc, error_nb




