# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime, timedelta
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.utils import DateTime, Duration


class TestMetadata(TestCase):

    def setUp(self):
        document = odf_get_document('samples/example.odt')
        self.meta = document.get_xmlpart('meta')


    def tearDown(self):
        del self.meta


    def test_get_title(self):
        meta = self.meta
        title = meta.get_title()
        expected = u"This is the title"
        self.assertEqual(title, expected)


    def test_set_title(self):
        meta = self.meta
        clone = meta.clone()
        title = u"A new title"
        clone.set_title(title)
        self.assertEqual(clone.get_title(), title)


    def test_set_bad_title(self):
        meta = self.meta
        clone = meta.clone()
        title = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_title, title)


    def test_get_description(self):
        meta = self.meta
        description = meta.get_description()
        expected = u"This is the description"
        self.assertEqual(description, expected)


    def test_set_description(self):
        meta = self.meta
        clone = meta.clone()
        description = u"A new description"
        clone.set_description(description)
        self.assertEqual(clone.get_description(), description)


    def test_set_bad_description(self):
        meta = self.meta
        clone = meta.clone()
        description = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_description, description)


    def test_get_subject(self):
        meta = self.meta
        subject = meta.get_subject()
        expected = u"This is the subject"
        self.assertEqual(subject, expected)


    def test_set_subject(self):
        meta = self.meta
        clone = meta.clone()
        subject = u"A new subject"
        clone.set_subject(subject)
        self.assertEqual(clone.get_subject(), subject)


    def test_set_bad_subject(self):
        meta = self.meta
        clone = meta.clone()
        subject = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_subject, subject)


    def test_get_language(self):
        meta = self.meta
        language = meta.get_language()
        expected = 'fr-FR'
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
        expected = DateTime.decode('2009-07-20T18:24:54')
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
        self.assertRaises(TypeError, clone.set_modification_date, date)


    def test_get_creation_date(self):
        meta = self.meta
        date = meta.get_creation_date()
        expected = datetime(2009, 2, 18, 20, 5, 10)
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
        self.assertRaises(TypeError, clone.set_creation_date, date)


    def test_get_initial_creator(self):
        meta = self.meta
        creator = meta.get_initial_creator()
        expected = None
        self.assertEqual(creator, expected)


    def test_set_initial_creator(self):
        meta = self.meta
        clone = meta.clone()
        creator = u"Socrates"
        clone.set_initial_creator(creator)
        self.assertEqual(clone.get_initial_creator(), creator)


    def test_set_bad_initial_creator(self):
        meta = self.meta
        clone = meta.clone()
        creator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_initial_creator, creator)


    def test_get_keyword(self):
        meta = self.meta
        keyword = meta.get_keyword()
        expected = u"These are the keywords"
        self.assertEqual(keyword, expected)


    def test_set_keyword(self):
        meta = self.meta
        clone = meta.clone()
        keyword = u"New keywords"
        clone.set_keyword(keyword)
        self.assertEqual(clone.get_keyword(), keyword)


    def test_set_bad_keyword(self):
        meta = self.meta
        clone = meta.clone()
        keyword = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_keyword, keyword)


    def test_get_editing_duration(self):
        meta = self.meta
        duration = meta.get_editing_duration()
        expected = Duration.decode('PT00H08M40S')
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
        expected = 10
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
        expected = (u"OpenOffice.org/3.1$Linux "
                    u"OpenOffice.org_project/310m11$Build-9399")
        self.assertEqual(generator, expected)


    def test_set_generator(self):
        meta = self.meta
        clone = meta.clone()
        generator = u"lpOD Project"
        clone.set_generator(generator)
        self.assertEqual(clone.get_generator(), generator)


    def test_set_bad_generator(self):
        meta = self.meta
        clone = meta.clone()
        generator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_generator, generator)


    def test_get_statistic(self):
        meta = self.meta
        statistic = meta.get_statistic()
        expected = {'meta:table-count': 0,
                    'meta:image-count': 0,
                    'meta:object-count': 0,
                    'meta:page-count': 1,
                    'meta:paragraph-count': 9,
                    'meta:word-count': 51,
                    'meta:character-count': 279}
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


    def test_set_bad_statistic(self):
        meta = self.meta
        clone = meta.clone()
        generator = "This ain't unicode"
        self.assertRaises(TypeError, clone.set_generator, generator)


    def test_get_user_defined_metadata(self):
        meta = self.meta

        metadata = meta.get_user_defined_metadata()
        expected = {'Prop1': u'a text',
                    'Prop2': datetime(2009, 7, 20, 0, 0),
                    'Prop3': 42.0,
                    'Prop4': True}

        self.assertEqual(metadata, expected)


    def test_set_user_defined_metadata(self):
        meta = self.meta
        clone = meta.clone()

        # A new value
        meta.set_user_defined_metadata('Prop5', 1)

        # Change a value
        meta.set_user_defined_metadata('Prop2', False)

        expected = {'Prop1': u'a text',
                    'Prop2': False,
                    'Prop3': 42.0,
                    'Prop4': True,
                    'Prop5': 1.0}

        metadata = meta.get_user_defined_metadata()
        self.assertEqual(metadata, expected)



if __name__ == '__main__':
    main()
