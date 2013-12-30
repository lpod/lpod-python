# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
        document2 = odf_get_document('samples/base_text.odt').clone()
        self.body2 = document2.get_body()


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


    def test_get_reference_mark_single(self):
        body = self.body
        para = body.get_paragraph()
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        para.append(reference_mark)
        get = body.get_reference_mark_single(name=u'你好 Zoé')
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_single_list(self):
        body = self.body
        para = body.get_paragraph()
        reference_mark = odf_create_reference_mark(u'你好 Zoé')
        para.append(reference_mark)
        get = body.get_reference_marks_single()[0]
        expected = ('<text:reference-mark text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start(self):
        body = self.body
        para = body.get_paragraph()
        reference_mark_start = odf_create_reference_mark_start(u'你好 Zoé')
        para.append(reference_mark_start)
        get = body.get_reference_mark_start(name=u'你好 Zoé')
        expected = ('<text:reference-mark-start text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_start_list(self):
        body = self.body
        result = body.get_reference_mark_starts()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-start '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_reference_mark_end(self):
        body = self.body
        para = body.get_paragraph()
        reference_mark_end = odf_create_reference_mark_end(u'你好 Zoé')
        para.append(reference_mark_end)
        get = body.get_reference_mark_end(name=u'你好 Zoé')
        expected = ('<text:reference-mark-end text:name="%s"/>' %
                    convert_unicode(u'你好 Zoé'))
        self.assertEqual(get.serialize(), expected)


    def test_get_reference_mark_end_list(self):
        body = self.body
        result = body.get_reference_mark_ends()
        self.assertEqual(len(result), 1)
        element = result[0]
        expected = ('<text:reference-mark-end '
                      'text:name="Nouvelle r&#233;f&#233;rence"/>')
        self.assertEqual(element.serialize(), expected)


    def test_get_referenced_1_odf(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=u'paragraph of the second title')
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced()
        expected = (u'<office:text><text:p text:style-name="Text_20_body">'
                    u'paragraph of the second title</text:p></office:text>')
        self.assertEqual(referenced.serialize(), expected)


    def test_get_referenced_1_xml(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=u'paragraph of the second title')
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_xml=True)
        expected = (u'<office:text><text:p text:style-name="Text_20_body">'
                    u'paragraph of the second title</text:p></office:text>')
        self.assertEqual(referenced, expected)


    def test_get_referenced_1_list(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=u'paragraph of the second title')
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_list=True)
        self.assertEqual(isinstance(referenced, list), True)
        self.assertEqual(len(referenced), 1)
        expected = (u'<text:p text:style-name="Text_20_body">'
                    u'paragraph of the second title</text:p>')
        self.assertEqual(referenced[0].serialize(), expected)


    def test_get_referenced_multi_odf(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=para)
        para.set_reference_mark(u'two',
                                position=(0, 7))
        ref = body.get_reference_mark(name=u'two')
        referenced = ref.get_referenced()
        expected = (u'<office:text>'
                    u'<text:p text:style-name="Text_20_body">'
                    u'This is'
                    u'</text:p></office:text>')
        self.assertEqual(referenced.serialize(), expected)


    def test_get_referenced_multi_xml_dirty(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=para)
        para.set_reference_mark(u'two',
                                position=(0, 7))
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_xml=True, clean=False)
        expected = (u'<office:text>'
                    u'<text:p text:style-name="Text_20_body">'
                    u'<text:reference-mark-start text:name="two"/>'
                    u'This is<text:reference-mark-end text:name="two"/>'
                    u' the first paragraph of the second title.'
                    u'</text:p>'
                    u'</office:text>')
        self.assertEqual(referenced, expected)


    def test_get_referenced_multi_xml_clean(self):
        body = self.body2
        para = body.get_paragraph(content=u'of the second title')
        para.set_reference_mark(u'one',
                                content=para)
        para.set_reference_mark(u'two',
                                position=(0, 7))
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_xml=True, clean=True)
        expected = (u'<office:text>'
                    u'<text:p text:style-name="Text_20_body">'
                    u'This is'
                    u' the first paragraph of the second title.'
                    u'</text:p>'
                    u'</office:text>')
        self.assertEqual(referenced, expected)


    def test_get_referenced_mix_xml(self):
        body = self.body2
        para = body.get_paragraph()
        para.set_reference_mark(u'one',
                                content=u'first paragraph.')
        para.set_reference_mark(u'two',
                                position=(0, 17))
        ref = body.get_reference_mark(name=u'two')
        referenced = ref.get_referenced(as_xml=True)
        expected = (u'<office:text>'
                    u'<text:p text:style-name="Text_20_body">'
                    u'This is the first'
                    u'</text:p>'
                    u'</office:text>')
        self.assertEqual(referenced, expected)


    def test_get_referenced_header(self):
        body = self.body2
        head = body.get_heading()
        head.set_reference_mark(u'one',
                                content=head)
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_xml=True)
        expected = (u'<office:text>'
                    u'<text:h text:style-name="Heading_20_1" '
                    u'text:outline-level="1">'
                    u'LpOD Test Case Document'
                    '</text:h>'
                    u'</office:text>')
        self.assertEqual(referenced, expected)


    def test_get_referenced_no_header(self):
        body = self.body2
        head = body.get_heading()
        head.set_reference_mark(u'one',
                                content=head)
        ref = body.get_reference_mark(name=u'one')
        referenced = ref.get_referenced(as_xml=True, no_header=True)
        expected = (u'<office:text>'
                    u'<text:p>'
                    u'LpOD Test Case Document'
                    '</text:p>'
                    u'</office:text>')
        self.assertEqual(referenced, expected)


if __name__ == '__main__':
    main()
