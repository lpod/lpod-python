# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.datatype import DateTime, Duration


class TestMetadata(TestCase):

    def setUp(self):
        document = odf_get_document('samples/meta.odt')
        self.meta = document.get_part('meta')


    def tearDown(self):
        del self.meta


    def test_get_title(self):
        meta = self.meta
        title = meta.get_title()
        expected = u"Intitulé"
        self.assertEqual(title, expected)


    def test_set_title(self):
        meta = self.meta
        clone = meta.clone()
        title = u"Nouvel intitulé"
        clone.set_title(title)
        self.assertEqual(clone.get_title(), title)


    def test_get_description(self):
        meta = self.meta
        description = meta.get_description()
        expected = u"Comments\nCommentaires\n评论"
        self.assertEqual(description, expected)


    def test_set_description(self):
        meta = self.meta
        clone = meta.clone()
        description = u"评论\nnCommentaires\nComments"
        clone.set_description(description)
        self.assertEqual(clone.get_description(), description)


    def test_get_subject(self):
        meta = self.meta
        subject = meta.get_subject()
        expected = u"Sujet de sa majesté"
        self.assertEqual(subject, expected)


    def test_set_subject(self):
        meta = self.meta
        clone = meta.clone()
        subject = u"Θέμα"
        clone.set_subject(subject)
        self.assertEqual(clone.get_subject(), subject)


    def test_get_language(self):
        meta = self.meta
        language = meta.get_language()
        expected = None
        self.assertEqual(language, expected)


    def test_set_language(self):
        meta = self.meta
        clone = meta.clone()
        language = 'en-US'
        clone.set_language(language)
        self.assertEqual(clone.get_language(), language)


    def test_set_bad_language(self):
        meta = self.meta
        clone = meta.clone()
        language = u"English"
        self.assertRaises(TypeError, clone.set_language, language)


    def test_get_modification_date(self):
        meta = self.meta
        date = meta.get_modification_date()
        expected = DateTime.decode('2009-07-31T15:59:13')
        self.assertEqual(date, expected)


    def test_set_modification_date(self):
        meta = self.meta
        clone = meta.clone()
        now = datetime.now().replace(microsecond=0)
        clone.set_modification_date(now)
        self.assertEqual(clone.get_modification_date(), now)


    def test_set_bad_modication_date(self):
        meta = self.meta
        clone = meta.clone()
        date = '2009-06-29T14:15:45'
        self.assertRaises(AttributeError, clone.set_modification_date, date)


    def test_get_creation_date(self):
        meta = self.meta
        date = meta.get_creation_date()
        expected = datetime(2009, 7, 31, 15, 57, 37)
        self.assertEqual(date, expected)


    def test_set_creation_date(self):
        meta = self.meta
        clone = meta.clone()
        now = datetime.now().replace(microsecond=0)
        clone.set_creation_date(now)
        self.assertEqual(clone.get_creation_date(), now)


    def test_set_bad_creation_date(self):
        meta = self.meta
        clone = meta.clone()
        date = '2009-06-29T14:15:45'
        self.assertRaises(AttributeError, clone.set_creation_date, date)


    def test_get_initial_creator(self):
        meta = self.meta
        creator = meta.get_initial_creator()
        expected = None
        self.assertEqual(creator, expected)


    def test_set_initial_creator(self):
        meta = self.meta
        clone = meta.clone()
        creator = u"Hervé"
        clone.set_initial_creator(creator)
        self.assertEqual(clone.get_initial_creator(), creator)


    def test_get_keywords(self):
        meta = self.meta
        keywords = meta.get_keywords()
        expected = u"Mots-clés"
        self.assertEqual(keywords, expected)


    def test_set_keywords(self):
        meta = self.meta
        clone = meta.clone()
        keywords = u"Nouveaux mots-clés"
        clone.set_keywords(keywords)
        self.assertEqual(clone.get_keywords(), keywords)


    def test_get_editing_duration(self):
        meta = self.meta
        duration = meta.get_editing_duration()
        expected = Duration.decode('PT00H05M30S')
        self.assertEqual(duration, expected)


    def test_set_editing_duration(self):
        meta = self.meta
        clone = meta.clone()
        duration = timedelta(1, 2, 0, 0, 5, 6, 7)
        clone.set_editing_duration(duration)
        self.assertEqual(clone.get_editing_duration(), duration)


    def test_set_bad_editing_duration(self):
        meta = self.meta
        clone = meta.clone()
        duration = 'PT00H01M27S'
        self.assertRaises(TypeError, clone.set_editing_duration, duration)


    def test_get_editing_cycles(self):
        meta = self.meta
        cycles = meta.get_editing_cycles()
        expected = 2
        self.assertEqual(cycles, expected)


    def test_set_editing_cycles(self):
        meta = self.meta
        clone = meta.clone()
        cycles = 1 # I swear it was a first shot!
        clone.set_editing_cycles(cycles)
        self.assertEqual(clone.get_editing_cycles(), cycles)


    def test_set_bad_editing_cycles(self):
        meta = self.meta
        clone = meta.clone()
        cycles = '3'
        self.assertRaises(TypeError, clone.set_editing_duration, cycles)


    def test_get_generator(self):
        meta = self.meta
        generator = meta.get_generator()
        expected = (u"OpenOffice.org/3.1$Unix "
                    u"OpenOffice.org_project/310m11$Build-9399")
        self.assertEqual(generator, expected)


    def test_set_generator(self):
        meta = self.meta
        clone = meta.clone()
        generator = u"lpOD Project"
        clone.set_generator(generator)
        self.assertEqual(clone.get_generator(), generator)


    def test_get_statistic(self):
        meta = self.meta
        statistic = meta.get_statistic()
        expected = {'meta:table-count': 0,
                    'meta:image-count': 0,
                    'meta:object-count': 0,
                    'meta:page-count': 1,
                    'meta:paragraph-count': 1,
                    'meta:word-count': 4,
                    'meta:character-count': 27}
        self.assertEqual(statistic, expected)


    def test_set_statistic(self):
        meta = self.meta
        clone = meta.clone()
        statistic = {'meta:table-count': 1,
                     'meta:image-count': 2,
                     'meta:object-count': 3,
                     'meta:page-count': 4,
                     'meta:paragraph-count': 5,
                     'meta:word-count': 6,
                     'meta:character-count': 7}
        clone.set_statistic(statistic)
        self.assertEqual(clone.get_statistic(), statistic)


    def test_get_user_defined_metadata(self):
        meta = self.meta
        metadata = meta.get_user_defined_metadata()
        expected = {u"Achevé à la date": datetime(2009, 7, 31),
                    u"Numéro du document": Decimal("3"),
                    u"Référence": True,
                    u"Vérifié par": u"Moi-même"}
        self.assertEqual(metadata, expected)


    def test_set_user_defined_metadata(self):
        meta = self.meta
        clone = meta.clone()
        # A new value
        meta.set_user_defined_metadata('Prop5', 1)
        # Change a value
        meta.set_user_defined_metadata(u"Référence", False)
        expected = {u"Achevé à la date": datetime(2009, 7, 31),
                    u"Numéro du document": Decimal("3"),
                    u"Référence": False,
                    u"Vérifié par": u"Moi-même",
                    u'Prop5': Decimal('1')}
        metadata = meta.get_user_defined_metadata()
        self.assertEqual(metadata, expected)



if __name__ == '__main__':
    main()
