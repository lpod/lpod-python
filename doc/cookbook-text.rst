.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Luis Belmar-Letelier <luis@itaapy.com>
            David Versmisse <david.versmisse@itaapy.com>

   This file is part of Lpod (see: http://lpod-project.org).
   Lpod is free software; you can redistribute it and/or modify it under
   the terms of either:

   a) the GNU General Public License as published by the Free Software
      Foundation, either version 3 of the License, or (at your option)
      any later version.
      Lpod is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.
      You should have received a copy of the GNU General Public License
      along with Lpod.  If not, see <http://www.gnu.org/licenses/>.

   b) the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0

#############
Text Cookbook
#############

.. contents::
   :local:

We will demonstrate how to generate OpenDocument Text (ODT) documents from
scratch.

Creating Text Document
======================

Use the `odf_new_document_from_type` function with 'text' as the type::

    >>> from lpod.document import odf_new_document_from_type
    >>> document = odf_new_document_from_type('text')

Now `document` is an empty text document issued from a template. It's a bit
like creating a new text document in your office application, except lpOD
templates don't create a default paragraph.

Adding Content
==============

Contents go into the body::

    >>> body = document.get_body()

Now we have a context to attach new elements to. In a text document, we
generally want to write paragraphs, lists, headings, and a table of content
to show the document hierarchy at first.

Adding Table of Content (TOC)
=============================

The TOC element comes from the `toc` module::

    >>> from lpod.toc import odf_create_toc
    >>> toc = odf_create_toc()
    >>> body.append_element(toc)

Adding Paragraph
================

For a smoother start, let's add a simple element::

    >>> from lpod.paragraph import odf_create_paragraph
    >>> paragraph = odf_create_paragraph(u"lpOD generated Document")
    >>> body.append_element(paragraph)

Adding Title
============

Titles are organised by level, starting from 1.

So let's add the main title of our document::

    >>> from lpod.heading import odf_create_heading
    >>> title1 = odf_create_heading(1, u"Lists")
    >>> body.append_element(title1)

Adding List
===========

Lists are a dedicated object::

    >>> from lpod.list import odf_create_list
    >>> my_list = odf_create_list([u'chocolat', u'café'])

The list factory accepts a Python list of unicode strings and list items.

The list can be written even though we will modify it afterwards::

    >>> body.append_element(my_list)

Adding List Item
================

List items also have their factory::

    >>> from lpod.list import odf_create_list_item
    >>> item = odf_create_list_item(u"thé")
    >>> my_list.append_item(item)

Adding Sublist
==============

A sublist is simply a list as an item of another list::

    >>> item.append_element(odf_create_list([u"thé vert", u"thé rouge"]))

Inserting List Item
===================

In case your forgot to insert an important item::

    >>> my_list.insert_item(u"Chicorée", position=1)

Or you can insert it before another item::

    >>> cafe = my_list.get_item_by_content(u"café")
    >>> my_list.insert_item(u'Chicorée', before=cafe)

Or after::

    >>> my_list.insert_item(u"Chicorée", after=cafe)

Adding Footnote
===============

Let's first start a new section in the document::

    >>> body.append_element(odf_create_heading(1, u"Footnotes"))
    >>> paragraph = odf_create_paragraph(u"A paragraph with a footnote "
            u"about references in it.")
    >>> body.append_element(paragraph)

Notes are quite complex so they deserve a dedicated API on paragraphs::

    >>> paragraph.insert_note(after=u"graph", note_id='note1', citation=u"1",
            body=(u'Author, A. (2007). "How to cite references", '
                  u'New York: McGraw-Hill.'))

That looks complex so we detail the arguments:

======== ==================================================
after    The word after what the "¹" citation is inserted.
note_id  The unique identifier of the note in the document.
citation The symbol the user sees to follow the footnote.
body     The footnote itself, at the end of the page.
======== ==================================================

LpOD creates footnotes by default. To create endnotes -- notes that appear
at the end of the document --, give the `note_class='endnote'` parameter.

Adding Annotation
=================

Annotations are notes that don't appear in the document but typically on a
side bar in a desktop application. So they are not printed.

Another section to make our document clear::

    >>> body.append_element(odf_create_heading(1, u"Annotations"))
    >>> paragraph = odf_create_paragraph(u"A paragraph with an annotation "
            u"in the middle.")
    >>> body.append_element(paragraph)

Annotations are inserted like notes but they are simpler::

    >>> paragraph.insert_annotation(after=u"annotation",
            body=u"It's so easy!", creator=u"Luis")

Annotation arguments are quite different:

======= ==================================================
after   The word after what the annotation is inserted.
body    The annotation itself, at the end of the page.
creator The author of the annotation.
date    A `datetime` value, by default `datetime.now()`.
======= ==================================================

Adding Table
============

Another section to make our document clear::

    >>> body.append_element(odf_create_heading(1, u"Tables"))
    >>> body.append_element(odf_create_paragraph(u"A 3x3 table:"))

Creating a table is not complicated::

    >>> from lpod.table import odf_create_table
    >>> table = odf_create_table(u"Table 1", width=3, height=3)
    >>> body.append_element(table)

But manipulating the table itself is another matter detailed in the
:doc:`Spreadsheet Cookbook <cookbook-spreadsheet>` (applicable to text tables
for the most part).

Applying Styles
===============

Styles probably are the most complex subject, detailed in the :doc:`Styles
Cookbook <cookbook-styles>` but the following information may suit your
immediate needs.

Another section to make our document clear::

    >>> body.append_element(odf_create_heading(1, u"Applying Styles"))

We add the paragraph we'll play with::

    >>> body.append_element(odf_create_paragraph(u'Highlighting the word '
            u'"highlight".')

Copying Style from Another Document
-----------------------------------

We know the `lpod_styles.odt` document contains an interesting style.

So let's first fetch the style::

    >>> lpod_styles = odf_get_document('lpod_styles.odt')
    >>> highlight = lpod_styles.get_style('text', u"Yellow Highlight",
            display_name=True)

We made some assumptions here:

=================== ========================================================
'text'              The family of the style, text styles apply on individual
                    characters.
u"Yellow Highlight" The name of the style as we see it in a desktop
                    application.
display_name        Styles have an internal name ("Yellow_20_Highlight" in
                    this example) but we gave the display_name instead.
=================== ========================================================

We hopefully have a style object that we add to our own collection::

    >>> document.insert_style(highlight)

Apply Style to a Pattern
========================

Styling individual characters requires wrapping them into a span element, and
applying the style to it.

LpOD does it in a single convenient method::

    >>> paragraph.set_span(highlight, u"highlight")

Now each occurence of the "highlight" pattern will appear in a yellow
background.

Updating Table of Content (TOC)
===============================

We added a TOC at first but it's empty. Now the titles are known, we can
generate its structure::

    >>> toc.auto_fill(document)

As the document is passed to find the titles, the TOC doesn't need to be
attached to the document to be generated. It could even be attached to another
document (think of generating a document compiling TOCs from a pool of
documents).

Saving the Document
===================

Last but not least, don't lose our hard work::

    >>> document.save('text.odt', pretty=True)

The `pretty` parameter asks for writing an indented serialized XML. The cost
in space in negligible and greatly helps debugging, so don't hesitate to use
it.
