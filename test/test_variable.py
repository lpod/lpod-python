# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
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
from datetime import datetime, time
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.variable import odf_create_variable_decl, odf_create_variable_set
from lpod.variable import odf_create_variable_get
from lpod.variable import odf_create_user_field_decl
from lpod.variable import odf_create_user_field_get
from lpod.variable import odf_create_page_number_variable
from lpod.variable import odf_create_page_count_variable
from lpod.variable import odf_create_date_variable, odf_create_time_variable
from lpod.variable import odf_create_chapter_variable
from lpod.variable import odf_create_filename_variable
from lpod.variable import odf_create_initial_creator_variable
from lpod.variable import odf_create_creation_date_variable
from lpod.variable import odf_create_creation_time_variable
from lpod.variable import odf_create_description_variable
from lpod.variable import odf_create_title_variable
from lpod.variable import odf_create_keywords_variable
from lpod.variable import odf_create_subject_variable
from lpod.utils import convert_unicode
from lpod.variable import odf_create_user_defined
from lpod.const import ODF_META


class TestVariables(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/variable.odt')


    def test_create_variable_decl(self):
        variable_decl = odf_create_variable_decl(u'你好 Zoé', 'float')
        expected = ('<text:variable-decl office:value-type="float" '
                      'text:name="%s"/>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_decl.serialize(), expected)


    def test_create_variable_set_float(self):
        variable_set = odf_create_variable_set(u'你好 Zoé', value=42)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="float" office:value="42" '
                      'text:display="none"/>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_set.serialize(), expected)


    def test_create_variable_set_datetime(self):
        date = datetime(2009, 5, 17, 23, 23, 00)
        variable_set = odf_create_variable_set(u'你好 Zoé', value=date,
                                               display=True)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="date" '
                      'office:date-value="2009-05-17T23:23:00">'
                      '2009-05-17T23:23:00'
                    '</text:variable-set>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_set.serialize(), expected)


    def test_create_variable_get(self):
        variable_get = odf_create_variable_get(u'你好 Zoé', value=42)
        expected = ('<text:variable-get text:name="%s" '
                      'office:value-type="float" office:value="42">'
                      '42'
                    '</text:variable-get>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(variable_get.serialize(), expected)


    def test_get_variable_decl(self):
        clone = self.document.clone()
        body = clone.get_body()
        variable_decl = body.get_variable_decl(u"Variabilité")
        expected = ('<text:variable-decl office:value-type="float" '
                      'text:name="%s"/>' % convert_unicode(u"Variabilité"))
        self.assertEqual(variable_decl.serialize(), expected)


    def test_get_variable_set(self):
        clone = self.document.clone()
        body = clone.get_body()
        variable_sets = body.get_variable_sets(u"Variabilité")
        self.assertEqual(len(variable_sets), 1)
        expected = ('<text:variable-set text:name="%s" '
                      'office:value-type="float" office:value="123" '
                      'style:data-style-name="N1">123</text:variable-set>' %
                        convert_unicode(u"Variabilité"))
        self.assertEqual(variable_sets[0].serialize(), expected)


    def test_get_variable_get(self):
        document = self.document.clone()
        body = document.get_body()
        value = body.get_variable_set_value(u"Variabilité")
        self.assertEqual(value, 123)



class TestUserFields(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/variable.odt')


    def test_create_user_field_decl(self):
        user_field_decl = odf_create_user_field_decl(u'你好 Zoé', 42)
        expected = (('<text:user-field-decl text:name="%s" '
                       'office:value-type="float" office:value="42"/>') %
                      convert_unicode(u'你好 Zoé'))
        self.assertEqual(user_field_decl.serialize(), expected)


    def test_create_user_field_get(self):
        user_field_get = odf_create_user_field_get(u'你好 Zoé', value=42)
        expected = ('<text:user-field-get text:name="%s" '
                      'office:value-type="float" office:value="42">'
                      '42'
                    '</text:user-field-get>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(user_field_get.serialize(), expected)


    def test_create_user_field_input(self):
        user_field_input = odf_create_user_field_input(u'你好 Zoé', value=42)
        expected = ('<text:user-field-input text:name="%s" '
                      'office:value-type="float" office:value="42">'
                      '42'
                    '</text:user-field-input>') % convert_unicode(u'你好 Zoé')
        self.assertEqual(user_field_input.serialize(), expected)


    def test_get_user_field_decl(self):
        clone = self.document.clone()
        body = clone.get_body()
        user_field_decl = body.get_user_field_decl(u"Champêtre")
        expected = ('<text:user-field-decl office:value-type="float" '
                      'office:value="1" text:name="%s"/>' %
                      convert_unicode(u"Champêtre"))
        self.assertEqual(user_field_decl.serialize(), expected)


    def test_get_user_field_get(self):
        clone = self.document.clone()
        body = clone.get_body()
        value = body.get_user_field_value(u"Champêtre")
        self.assertEqual(value, True)



class TestUserDefined(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/meta.odt')
        self.meta = self.document.get_part(ODF_META)


    def test_create_user_defined_1(self):
        element = odf_create_user_defined(u'unknown_in_meta',
                                value=42,
                                value_type=u'float',
                                text=None,
                                style=None,
                                from_document=self.document)
        expected = ('<text:user-defined text:name="unknown_in_meta" '
                    'office:value-type="float" '
                    'office:value="42">42</text:user-defined>')
        self.assertEqual(element.serialize(), expected)


    def test_create_user_defined_2(self):
        element = odf_create_user_defined(u'unknown_in_meta2',
                                value=datetime(2013, 12, 30),
                                value_type=u'date',
                                text=u'2013-12-30',
                                style=None,
                                from_document=self.document)
        expected = ('<text:user-defined text:name="unknown_in_meta2" '
                    'office:value-type="date" '
                    'office:date-value="2013-12-30T00:00:00">2013-12-30'
                    '</text:user-defined>')
        self.assertEqual(element.serialize(), expected)


    def test_create_user_defined_2_no_doc(self):
        element = odf_create_user_defined(u'unknown_in_meta2',
                                value=datetime(2013, 12, 30),
                                value_type=u'date',
                                text=u'2013-12-30',
                                style=None,
                                from_document=None)
        expected = ('<text:user-defined text:name="unknown_in_meta2" '
                    'office:value-type="date" '
                    'office:date-value="2013-12-30T00:00:00">2013-12-30'
                    '</text:user-defined>')
        self.assertEqual(element.serialize(), expected)


    def test_create_user_defined_3_existing(self):
        element = odf_create_user_defined(u'Référence',
                                from_document=self.document)
        expected = (
                    '<text:user-defined text:name="%s" '
                    'office:value-type="boolean" '
                    'office:boolean-value="true">'
                    'true</text:user-defined>') % convert_unicode(u'Référence')
        self.assertEqual(element.serialize(), expected)


    def test_create_user_defined_4_existing(self):
        element = odf_create_user_defined(u'Référence',
                                value=False, # default value if not existing
                                value_type=u'boolean',
                                from_document=self.document)
        expected = (
                    '<text:user-defined text:name="%s" '
                    'office:value-type="boolean" '
                    'office:boolean-value="true">'
                    'true</text:user-defined>') % convert_unicode(u'Référence')
        self.assertEqual(element.serialize(), expected)


    def test_create_user_defined_5_nodoc(self):
        element = odf_create_user_defined(u'Référence',
                                value=False, # default value if not existing
                                value_type=u'boolean',
                                from_document=None)
        expected = (
                    '<text:user-defined text:name="%s" '
                    'office:value-type="boolean" '
                    'office:boolean-value="false">'
                    'false</text:user-defined>') % convert_unicode(u'Référence')
        self.assertEqual(element.serialize(), expected)


    def test_get_user_defined(self):
        element = odf_create_user_defined(u'Référence',
                                value=False, # default value if not existing
                                value_type=u'boolean',
                                from_document=self.document)
        body = self.document.get_body()
        para = body.get_paragraph()
        para.append(element)
        user_defined = body.get_user_defined(u'Référence')
        expected = (
                    '<text:user-defined text:name="%s" '
                    'office:value-type="boolean" '
                    'office:boolean-value="true">'
                    'true</text:user-defined>') % convert_unicode(u'Référence')
        self.assertEqual(user_defined.serialize(), expected)


    def test_get_user_defined_list(self):
        element = odf_create_user_defined(u'Référence',
                                value=False, # default value if not existing
                                value_type=u'boolean',
                                from_document=self.document)
        body = self.document.get_body()
        para = body.get_paragraph()
        para.append(element)
        element2 = odf_create_user_defined(u'unknown_in_meta2',
                                value=datetime(2013, 12, 30),
                                value_type=u'date',
                                text=u'2013-12-30',
                                style=None,
                                from_document=None)
        para.append(element2)
        user_defined_list = body.get_user_defined_list()
        self.assertEqual(len(user_defined_list), 2)


    def test_get_user_defined_value(self):
        element = odf_create_user_defined(u'Référence',
                                value=False, # default value if not existing
                                value_type=u'boolean',
                                from_document=self.document)
        body = self.document.get_body()
        para = body.get_paragraph()
        para.append(element)
        element2 = odf_create_user_defined(u'unknown_in_meta2',
                                value=datetime(2013, 12, 30),
                                value_type=u'date',
                                text=u'2013-12-30',
                                style=None,
                                from_document=None)
        para.append(element2)
        value = body.get_user_defined_value(u'Référence')
        self.assertEqual(value, True)
        value = body.get_user_defined_value(u'unknown_in_meta2')
        self.assertEqual(value, datetime(2013, 12, 30))


# TODO On all the following variable tests, interact with the document

class TestPageNumber(TestCase):

    def test_create_page_number(self):
        page_number = odf_create_page_number_variable()
        expected = '<text:page-number text:select-page="current"/>'
        self.assertEqual(page_number.serialize(), expected)


    def test_create_page_number_complex(self):
        page_number = odf_create_page_number_variable(select_page='next',
                                                      page_adjust=1)
        expected = ('<text:page-number text:select-page="next" '
                    'text:page-adjust="1"/>')
        self.assertEqual(page_number.serialize(), expected)



class TestPageCount(TestCase):

    def test_create_page_count(self):
        page_count = odf_create_page_count_variable()
        expected = '<text:page-count/>'
        self.assertEqual(page_count.serialize(), expected)



class TestDate(TestCase):

    def test_create_date(self):
        date_elt = odf_create_date_variable(datetime(2009, 7, 20))
        expected = ('<text:date text:date-value="2009-07-20T00:00:00">'
                      '2009-07-20'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)


    def test_create_date_fixed(self):
        date_elt = odf_create_date_variable(datetime(2009, 7, 20),
                                            fixed=True)
        expected = ('<text:date text:date-value="2009-07-20T00:00:00" '
                      'text:fixed="true">'
                      '2009-07-20'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)


    def test_create_date_text(self):
        date_elt =  odf_create_date_variable(datetime(2009, 7, 20),
                text=u'20 juil. 09')
        expected = ('<text:date text:date-value="2009-07-20T00:00:00">'
                      '20 juil. 09'
                    '</text:date>')
        self.assertEqual(date_elt.serialize(), expected)



class TestTime(TestCase):

    def test_create_time(self):
        time_elt = odf_create_time_variable(time(19,30))
        expected = ('<text:time text:time-value="1900-01-01T19:30:00">'
                      '19:30:00'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)


    def test_create_time_fixed(self):
        time_elt = odf_create_time_variable(time(19, 30), fixed=True)
        expected = ('<text:time text:time-value="1900-01-01T19:30:00" '
                      'text:fixed="true">'
                      '19:30:00'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)


    def test_create_time_text(self):
        time_elt =  odf_create_time_variable(time(19, 30), text=u'19h30')
        expected = ('<text:time text:time-value="1900-01-01T19:30:00">'
                      '19h30'
                    '</text:time>')
        self.assertEqual(time_elt.serialize(), expected)



class TestChapter(TestCase):

    def test_create_chapter(self):
        chapter = odf_create_chapter_variable()
        expected = '<text:chapter text:display="name"/>'
        self.assertEqual(chapter.serialize(), expected)


    def test_create_chapter_complex(self):
        chapter = odf_create_chapter_variable(display='number-and-name',
                                              outline_level=1)
        expected = ('<text:chapter text:display="number-and-name" '
                      'text:outline-level="1"/>')
        self.assertEqual(chapter.serialize(), expected)



class TestFilename(TestCase):

    def test_create_filename(self):
        filename = odf_create_filename_variable()
        expected = '<text:file-name text:display="full"/>'
        self.assertEqual(filename.serialize(), expected)


    def test_create_filename_fixed(self):
        filename = odf_create_filename_variable(fixed=True)
        expected = '<text:file-name text:display="full" text:fixed="true"/>'
        self.assertEqual(filename.serialize(), expected)



class TestInitialCreator(TestCase):

    def test_create_initial_creator(self):
        elt = odf_create_initial_creator_variable()
        expected = '<text:initial-creator/>'
        self.assertEqual(elt.serialize(), expected)



class TestCreationDate(TestCase):

    def test_create_creation_date(self):
        elt = odf_create_creation_date_variable()
        expected = '<text:creation-date/>'
        self.assertEqual(elt.serialize(), expected)



class TestCreationTime(TestCase):

    def test_create_creation_time(self):
        elt = odf_create_creation_time_variable()
        expected = '<text:creation-time/>'
        self.assertEqual(elt.serialize(), expected)



class TestDescription(TestCase):

    def test_create_description(self):
        elt = odf_create_description_variable()
        expected = '<text:description/>'
        self.assertEqual(elt.serialize(), expected)



class TestTitle(TestCase):

    def test_create_title(self):
        elt = odf_create_title_variable()
        expected = '<text:title/>'
        self.assertEqual(elt.serialize(), expected)



class TestSubject(TestCase):

    def test_create_subject(self):
        elt = odf_create_subject_variable()
        expected = '<text:subject/>'
        self.assertEqual(elt.serialize(), expected)



class TestKeywords(TestCase):

    def test_create_keywords(self):
        elt = odf_create_keywords_variable()
        expected = '<text:keywords/>'
        self.assertEqual(elt.serialize(), expected)



if __name__ == '__main__':
    main()
