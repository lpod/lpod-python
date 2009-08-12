# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.document import odf_create_note, odf_create_annotation
from lpod.document import odf_create_list, odf_create_paragraph
from lpod.xmlpart import LAST_CHILD


class TestNote(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/note.odt')
        self.content = document.get_xmlpart('content')
        expected = ('<text:note text:note-class="footnote" text:id="note1">'
                      '<text:note-citation>1</text:note-citation>'
                      '<text:note-body>'
                        '<text:p>'
                          'a footnote'
                        '</text:p>'
                      '</text:note-body>'
                    '</text:note>')
        self.expected = expected


    def test_create_note(self):

        # With an odf_element
        note_body = odf_create_paragraph(u'a footnote', style='Standard')
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=note_body)
        expected = self.expected.replace('<text:p>',
                                         '<text:p text:style-name="Standard">')
        self.assertEqual(note.serialize(), expected)

        # With an unicode object
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=u'a footnote')
        self.assertEqual(note.serialize(), self.expected)


    def test_get_note(self):
        content = self.content
        note = content.get_note_by_id('ftn0')
        self.assertEqual(note.get_name(), 'text:note')


    def test_get_note_list(self):
        content = self.content
        notes = content.get_note_list()
        self.assertEqual(len(notes), 2)



    def test_get_note_list_footnote(self):
        content = self.content
        notes = content.get_note_list(note_class='footnote')
        self.assertEqual(len(notes), 1)


    def test_get_note_list_endnote(self):
        content = self.content
        notes = content.get_note_list(note_class='endnote')
        self.assertEqual(len(notes), 1)


    def test_insert_note(self):
        clone = self.content.clone()
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=u'a footnote')
        paragraph = clone.get_paragraph_by_position(1)
        paragraph.insert_element(note, LAST_CHILD)


    def test_get_formated_text(self):
        document = self.document
        content = self.content
        paragraph = content.get_element('//text:p')
        list_whith_note = odf_create_list()
        list_whith_note.append_item(paragraph)
        body = content.get_body()
        body.append_element(list_whith_note)
        expected = (u"- Un paragraphe[1] d'apparence(i) banale.\n"
                    u"---\n"
                    u"[1] C'est-à-dire l'élément « text:p ».\n\n"
                    u"\n------\n"
                    u"(i) Les apparences sont trompeuses !\n")
        self.assertEqual(document.get_formated_text(), expected)



class TestAnnotation(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/note.odt')
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_annotation(self):
        # Create
        annotation = odf_create_annotation(u"Lost Dialogs", creator=u"Plato",
                date=datetime(2009, 6, 22, 17, 18, 42))
        expected = ('<office:annotation>'
                      '<text:p>'
                        'Lost Dialogs'
                      '</text:p>'
                      '<dc:creator>Plato</dc:creator>'
                      '<dc:date>2009-06-22T17:18:42</dc:date>'
                    '</office:annotation>')
        self.assertEqual(annotation.serialize(), expected)


    def test_get_annotation_list(self):
        content = self.content
        annotations = content.get_annotation_list()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_date()
        self.assertEqual(date, datetime(2009, 8, 3, 12, 9, 45))
        text = annotation.get_text_content()
        self.assertEqual(text, u"Sauf qu'il est commenté !")


    def test_get_annotation_list_author(self):
        content = self.content
        creator = u"Auteur inconnu"
        annotations = content.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author(self):
        content = self.content
        creator = u"Plato"
        annotations = content.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date(self):
        content = self.content
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        content = self.content
        start_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        content = self.content
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        content = self.content
        end_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = content.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        content = self.content
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date_end_date(self):
        content = self.content
        start_date = datetime(2009, 5, 1, 0, 0, 0)
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = content.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_start_date_end_date(self):
        content = self.content
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author_start_date_end_date(self):
        content = self.content
        creator = u"Plato"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_bad_start_date_end_date(self):
        content = self.content
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 23, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = content.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_insert_annotation(self):
        content = self.content
        clone = content.clone()
        creator = u"Plato"
        text = u"It's like you're in a cave."
        annotation = odf_create_annotation(text, creator=creator)
        context = clone.get_paragraph_by_position(1)
        context.wrap_text(annotation, offset=27)
        annotations = clone.get_annotation_list()
        self.assertEqual(len(annotations), 2)
        first_annotation = annotations[0]
        self.assertEqual(first_annotation.get_text_content(), text)
        del clone



if __name__ == '__main__':
    main()
