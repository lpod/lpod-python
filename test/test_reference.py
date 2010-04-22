# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
from lpod.reference import odf_create_reference_mark
from lpod.reference import odf_create_reference_mark_start
from lpod.reference import odf_create_reference_mark_end
from lpod.utils import convert_unicode


class reference_markTest(TestCase):

    def setUp(self):
        document = odf_get_document('samples/bookmark.odt').clone()
        self.body = document.get_body()


    def test_create_reference_mark(self):
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark.serialize(), expected)


    def test_create_reference_mark_start(self):
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_start.serialize(), expected)


    def test_create_reference_mark_end(self):
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(reference_mark_end.serialize(), expected)


    def test_get_reference_mark(self):
        body = self.body
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        body.append(reference_mark)
        get = body.get_reference_mark_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_list(self):
        body = self.body
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        body.append(reference_mark)
        get = body.get_reference_mark_list()[0]
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start(self):
        body = self.body
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        body.append(reference_mark_start)
        get = body.get_reference_mark_start_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start_list(self):
        body = self.body
        result = body.get_reference_mark_start_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-start '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_reference_mark_end(self):
        body = self.body
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        body.append(reference_mark_end)
        get = body.get_reference_mark_end_by_name(u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_end_list(self):
        body = self.body
        result = body.get_reference_mark_end_list()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-end '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)



if __name__ == '__main__':
    main()
