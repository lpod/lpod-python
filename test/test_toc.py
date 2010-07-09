# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.toc import odf_create_toc


def get_toc_lines(toc):
    return [paragraph.get_text()
            for paragraph in toc.get_paragraphs()]



class TOCTest(TestCase):

    def setUp(self):
        self.document = odf_get_document("samples/toc.odt")
        self.expected = [
                u"Table des matières",
                u"1. Level 1 title 1",
                u"1.1. Level 2 title 1",
                u"2. Level 1 title 2",
                u"2.1.1. Level 3 title 1",
                u"2.2. Level 2 title 2",
                u"3. Level 1 title 3",
                u"3.1. Level 2 title 1",
                u"3.1.1. Level 3 title 1",
                u"3.1.2. Level 3 title 2",
                u"3.2. Level 2 title 2",
                u"3.2.1. Level 3 title 1",
                u"3.2.2. Level 3 title 2"]


    def test_toc_fill_unattached(self):
        toc = odf_create_toc(u"Table des matières")
        self.assertRaises(ValueError, toc.fill)


    def test_toc_fill_unattached_document(self):
        toc = odf_create_toc(u"Table des matières")
        toc.fill(self.document)
        toc_lines = get_toc_lines(toc)
        self.assertEqual(toc_lines, self.expected)


    def test_toc_fill_attached(self):
        document = self.document.clone()
        toc = odf_create_toc(u"Table des matières")
        document.get_body().append(toc)
        toc.fill()
        toc_lines = get_toc_lines(toc)
        self.assertEqual(toc_lines, self.expected)



if __name__ == '__main__':
    main()

