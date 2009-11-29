.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Jean-Marie Gouarné <jean-marie.gouarne@arsaperta.com>
            Luis Belmar-Letelier <luis@itaapy.com>

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


Notes
=========

.. contents::

Generally speaking, a note is an object whose main function is to allow the user
to set some text content out of the main document body but to structurally
associate this content to a specific location in the document body. The content
of a note is stored in a sequence of one or more paragraphs and/or item lists.

The lpOD API supports three kinds of notes, so-called footnotes, endnotes and
annotations. Footnotes and endnotes have the same structure and differ only by
their display location in the document body, while annotations are specific
objects.

Footnote and endnote creation
-----------------------------

Footnotes and endnotes are created through the same method. The user must
provide a note identifier, i.e. an arbitrary code name (not visible in the
document), unique in the scope of the document, and a class option, knowing that
a note class is either 'footnote' or 'endnote'.

These notes are created as free elements, so they can be inserted later in place
(and replicated for reuse in several locations one or more documents). As a
consequence, creation and insertion are done through two distinct functions,
i.e. ``odf_create_note()`` and ``insert_note()``, the second one being a
context-related method.

While the identifier and the class are mandatory as soon as a note is inserted
in a document, these parameters are not required at the creation time. They can
be provided (or changed) through the insert_note() method.

The ``insert_note()`` method allows the user to insert the note in the same way
as a position bookmark (see above). As a consequence, its first arguments are
the same as those of the create bookmark method.  However, ``insert_note()``
requires additional arguments providing the identifier and the citation mark
(if not previously set), and the citation mark, i.e. the symbol which will be
displayed in the document body as a reference to the note. Remember that the
note citation is not an identifier; it's a designed to be displayed according
to a context-related logic, while the identifier is unique for the whole
document.

Regarding the identifier, the user can provide either an explicit value, or an
function that is supposed to return an automatically generated unique value. If
the class option is missing, the API automatically selects 'footnote'.

Footnote and endnote content
-----------------------------

A note is a container whose body can be filled with one or more paragraphs or
item lists at any time, before or after the insertion in the document. As a
consequence, a note can be used as a regular context for paragraph or list
appending or retrieval operations.

Note that neither the OpenDocument schema nor the lpOD level 1 API prevents the
user from including notes into a note body; however the lpOD team doesn't
recommend such a practice.

Annotation creation [tbc]
-------------------------

Annotations don't have identifiers and are directly linked to a given offset in
a given text container.

Change tracking [todo]
----------------------


