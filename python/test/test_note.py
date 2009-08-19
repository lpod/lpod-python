# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.element import odf_create_element
from lpod.list import odf_create_list
from lpod.note import odf_create_note, odf_create_annotation
from lpod.paragraph import odf_create_paragraph
from lpod.utils import convert_unicode


class TestNote(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/note.odt')
        self.body = document.get_body()
        expected = ('<text:note text:note-class="footnote" text:id="note1">'
                      '<text:note-citation>1</text:note-citation>'
                      '<text:note-body>'
                        '<text:p>'
                          'a footnote'
                        '</text:p>'
                      '</text:note-body>'
                    '</text:note>')
        self.expected = expected


    def test_create_note1(self):
        # With an odf_element
        note_body = odf_create_paragraph(u'a footnote', style='Standard')
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=note_body)
        expected = self.expected.replace('<text:p>',
                                         '<text:p text:style-name="Standard">')
        self.assertEqual(note.serialize(), expected)


    def test_create_note2(self):
        # With an unicode object
        note = odf_create_note(note_id='note1', citation=u'1',
                               body=u'a footnote')
        self.assertEqual(note.serialize(), self.expected)


    def test_get_note(self):
        body = self.body
        note = body.get_note_by_id('ftn0')
        self.assertEqual(note.get_name(), 'text:note')


    def test_get_note_list(self):
        body = self.body
        notes = body.get_note_list()
        self.assertEqual(len(notes), 2)



    def test_get_note_list_footnote(self):
        body = self.body
        notes = body.get_note_list(note_class='footnote')
        self.assertEqual(len(notes), 1)


    def test_get_note_list_endnote(self):
        body = self.body
        notes = body.get_note_list(note_class='endnote')
        self.assertEqual(len(notes), 1)


    def test_insert_note(self):
        note = odf_create_note(note_id='note1', citation=u"1",
                               body=u"élément pertubateur")
        paragraph = odf_create_paragraph(u"Un paragraphe")
        paragraph.insert_note(note, after=u"para")
        expected = ('<text:p>Un para'
                      '<text:note text:note-class="footnote" '
                        'text:id="note1">'
                        '<text:note-citation>1</text:note-citation>'
                        '<text:note-body>'
                          '<text:p>&#233;l&#233;ment pertubateur</text:p>'
                        '</text:note-body>'
                      '</text:note>'
                    'graphe</text:p>')
        self.assertEqual(paragraph.serialize(), convert_unicode(expected))


    def test_insert_note_inside_span(self):
        note = odf_create_note(note_id='note1', citation=u"1",
                               body=u"élément pertubateur")
        data = "<text:p>Un <text:span>para</text:span>graphe</text:p>"
        paragraph = odf_create_element(data)
        paragraph.insert_note(note, after=u"para")
        expected = ('<text:p>Un <text:span>para'
                      '<text:note text:note-class="footnote" '
                        'text:id="note1">'
                        '<text:note-citation>1</text:note-citation>'
                        '<text:note-body>'
                          '<text:p>&#233;l&#233;ment pertubateur</text:p>'
                        '</text:note-body>'
                      '</text:note>'
                    '</text:span>graphe</text:p>')
        self.assertEqual(paragraph.serialize(), convert_unicode(expected))


    def test_insert_note_after_span(self):
        note = odf_create_note(note_id='note1', citation=u"1",
                               body=u"élément pertubateur")
        data = "<text:p>Un <text:span>para</text:span>graphe.</text:p>"
        paragraph = odf_create_element(data)
        paragraph.insert_note(note, after=u"graphe")
        expected = ('<text:p>Un <text:span>para</text:span>graphe'
                      '<text:note text:note-class="footnote" '
                        'text:id="note1">'
                        '<text:note-citation>1</text:note-citation>'
                        '<text:note-body>'
                          '<text:p>&#233;l&#233;ment pertubateur</text:p>'
                        '</text:note-body>'
                      '</text:note>'
                    '.</text:p>')
        self.assertEqual(paragraph.serialize(), convert_unicode(expected))


    def test_get_formated_text(self):
        document = self.document
        body = self.body
        paragraph = body.get_element('//text:p')
        list_whith_note = odf_create_list()
        list_whith_note.append_item(paragraph)
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
        self.body = document.get_body()


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
        body = self.body
        annotations = body.get_annotation_list()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_annotation_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_annotation_date()
        self.assertEqual(date, datetime(2009, 8, 3, 12, 9, 45))
        text = annotation.get_text_content()
        self.assertEqual(text, u"Sauf qu'il est commenté !")


    def test_get_annotation_list_author(self):
        body = self.body
        creator = u"Auteur inconnu"
        annotations = body.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author(self):
        body = self.body
        creator = u"Plato"
        annotations = body.get_annotation_list(creator=creator)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date(self):
        body = self.body
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = body.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        body = self.body
        start_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotation_list(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        body = self.body
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        body = self.body
        end_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = body.get_annotation_list(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        body = self.body
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date_end_date(self):
        body = self.body
        start_date = datetime(2009, 5, 1, 0, 0, 0)
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = body.get_annotation_list(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_start_date_end_date(self):
        body = self.body
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author_start_date_end_date(self):
        body = self.body
        creator = u"Plato"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = body.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_bad_start_date_end_date(self):
        body = self.body
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 23, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = body.get_annotation_list(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_insert_annotation(self):
        body = self.body.clone()
        creator = u"Plato"
        text = u"It's like you're in a cave."
        annotation = odf_create_annotation(text, creator=creator)
        paragraph = body.get_paragraph_by_position(1)
        paragraph.insert_annotation(annotation, after=u"Un")
        annotations = body.get_annotation_list()
        self.assertEqual(len(annotations), 2)
        first_annotation = annotations[0]
        print "annotation", paragraph.serialize()
        raise NotImplementedError
        self.assertEqual(first_annotation.get_text_content(), text)



if __name__ == '__main__':
    main()
