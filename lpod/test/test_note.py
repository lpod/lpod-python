# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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
from datetime import datetime
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.element import odf_create_element
from lpod.list import odf_create_list
from lpod.note import odf_create_note, odf_create_annotation
from lpod.paragraph import odf_create_paragraph


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
        note = body.get_note(note_id='ftn1')
        self.assertEqual(note.get_tag(), 'text:note')


    def test_get_note_list(self):
        body = self.body
        notes = body.get_notes()
        self.assertEqual(len(notes), 2)


    def test_get_note_list_footnote(self):
        body = self.body
        notes = body.get_notes(note_class='footnote')
        self.assertEqual(len(notes), 1)


    def test_get_note_list_endnote(self):
        body = self.body
        notes = body.get_notes(note_class='endnote')
        self.assertEqual(len(notes), 1)


    def test_get_note_by_id(self):
        body = self.body
        note = body.get_note(note_id='ftn1')
        expected = ('<text:note text:id="ftn1" text:note-class="footnote">\n'
                    '  <text:note-citation>1</text:note-citation>\n'
                    '  <text:note-body>\n'
                    '      <text:p text:style-name="Footnote">'
                    'C\'est-&#224;-dire l\'&#233;l&#233;ment '
                    '&#171;&#160;text:p&#160;&#187;.</text:p>'
                    '</text:note-body>\n'
                    '</text:note>\n')
        self.assertEqual(note.serialize(pretty=True), expected)


    def test_get_note_by_class_footnote(self):
        body = self.body
        footnotes = body.get_notes(note_class='footnote')
        footnote = footnotes[0]
        expected = ('<text:note text:id="ftn1" text:note-class="footnote">\n'
                    '  <text:note-citation>1</text:note-citation>\n'
                    '  <text:note-body>\n'
                    '      <text:p text:style-name="Footnote">'
                    'C\'est-&#224;-dire l\'&#233;l&#233;ment '
                    '&#171;&#160;text:p&#160;&#187;.</text:p>'
                    '</text:note-body>\n'
                    '</text:note>\n')
        self.assertEqual(footnote.serialize(pretty=True), expected)


    def test_get_note_by_class_endnote(self):
        body = self.body
        endnotes = body.get_notes(note_class='endnote')
        endnote = endnotes[0]
        expected = ('<text:note text:id="ftn2" text:note-class="endnote">\n'
                    '  <text:note-citation>i</text:note-citation>\n'
                    '  <text:note-body>\n'
                    '      <text:p text:style-name="Endnote">Les apparences '
                    'sont trompeuses !</text:p></text:note-body>\n'
                    '</text:note>\n')
        self.assertEqual(endnote.serialize(pretty=True), expected)


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
        self.assertEqual(paragraph.serialize(), expected)


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
        self.assertEqual(paragraph.serialize(), expected)


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
        self.assertEqual(paragraph.serialize(), expected)


    def test_get_formatted_text(self):
        document = self.document
        body = self.body
        paragraph = body.get_element('//text:p')
        list_with_note = odf_create_list()
        list_with_note.append_item(paragraph)
        body.append(list_with_note)
        expected = (u"- Un paragraphe[1] d'apparence(i) banale[*].\n"
                    u"----\n"
                    u"[1] C'est-à-dire l'élément « text:p ».\n"
                    u"\n"
                    u"----\n"
                    u"[*] Sauf qu'il est commenté !\n"
                    u"\n"
                    u"========\n"
                    u"(i) Les apparences sont trompeuses !\n")
        self.assertEqual(document.get_formatted_text(), expected)



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
        annotations = body.get_annotations()
        self.assertEqual(len(annotations), 1)
        annotation = annotations[0]
        creator = annotation.get_dc_creator()
        self.assertEqual(creator, u"Auteur inconnu")
        date = annotation.get_dc_date()
        self.assertEqual(date, datetime(2009, 8, 3, 12, 9, 45))
        text = annotation.get_text_content()
        self.assertEqual(text, u"Sauf qu'il est commenté !")


    def test_get_annotation_list_author(self):
        body = self.body
        creator = u"Auteur inconnu"
        annotations = body.get_annotations(creator=creator)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author(self):
        body = self.body
        creator = u"Plato"
        annotations = body.get_annotations(creator=creator)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date(self):
        body = self.body
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = body.get_annotations(start_date=start_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date(self):
        body = self.body
        start_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotations(start_date=start_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_end_date(self):
        body = self.body
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotations(end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_end_date(self):
        body = self.body
        end_date = datetime(2009, 8, 1, 0, 0, 0)
        annotations = body.get_annotations(end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_start_date_end_date(self):
        body = self.body
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotations(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_start_date_end_date(self):
        body = self.body
        start_date = datetime(2009, 5, 1, 0, 0, 0)
        end_date = datetime(2009, 6, 1, 0, 0, 0)
        annotations = body.get_annotations(start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_start_date_end_date(self):
        body = self.body
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 8, 1, 0, 0, 0)
        end_date = datetime(2009, 9, 1, 0, 0, 0)
        annotations = body.get_annotations(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 1)


    def test_get_annotation_list_bad_author_start_date_end_date(self):
        body = self.body
        creator = u"Plato"
        start_date = datetime(2009, 6, 1, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = body.get_annotations(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_get_annotation_list_author_bad_start_date_end_date(self):
        body = self.body
        creator = u"Auteur inconnu"
        start_date = datetime(2009, 6, 23, 0, 0, 0)
        end_date = datetime(2009, 7, 1, 0, 0, 0)
        annotations = body.get_annotations(creator=creator,
                                                   start_date=start_date,
                                                   end_date=end_date)
        self.assertEqual(len(annotations), 0)


    def test_insert_annotation(self):
        text = u"It's like you're in a cave."
        creator = u"Plato"
        date = datetime(2009, 8, 19)
        annotation = odf_create_annotation(text, creator=creator, date=date)
        paragraph = odf_create_paragraph(u"Un paragraphe")
        paragraph.insert_annotation(annotation, after=u"para")
        expected = ('<text:p>Un para'
                      '<office:annotation>'
                        '<text:p>It\'s like you\'re in a cave.</text:p>'
                        '<dc:creator>Plato</dc:creator>'
                        '<dc:date>2009-08-19T00:00:00</dc:date>'
                      '</office:annotation>'
                    'graphe</text:p>')
        self.assertEqual(paragraph.serialize(), expected)



if __name__ == '__main__':
    main()
