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


Text marks and indices
======================

.. contents::
   :local:

Text Bookmarks
--------------

A text bookmark is either a mark associated to a position in a text, or a pair
of location marks that defines a delimited range of text. It's represented
in the lpOD API by an ``odf_bookmark`` object.

Position bookmarks
~~~~~~~~~~~~~~~~~~
A position bookmark is a location mark somewhere in a text container, which is
identified by a unique name, but without any content.

A bookmark is created "in place", in a given element at a given position, using
the ``set_bookmark()`` context based method.  The bookmark name is a mandatory
argument. By default, the bookmark is put before the first character of the
content in the calling element (which may be a paragraph, a heading, or a text
span).

The position can be explicitly provided by the user. Alternatively, the user can provide a regular expression, so the bookmark is set before the first substring that matches the expression::

  paragraph.set_bookmark("BM1", text="xyz")
  paragraph.set_bookmark("BM2", position=4)

There is no need to specify the creation of a position bookmark;
``set_bookmark()`` creates a position bookmark by default; an additional
``role`` parameter is required for range bookmarks only, as introduced later.

The first instruction above sets a bookmark before the first substring matching
the given expression (here ``xyz``), which is processed as a regular expression. The second instruction sets a bookmark in the same paragraph at a given (zero-based), so before the 5th character.

In order to put a bookmark according to a regexp that could be matched more than
once in the same paragraph, it's possible to combine the position and text
options, so the search area begins at the given position.

A bookmark can be retrieved by its unique name. The ODF element then can be
obtained as the parent of the bookmark element. However, if the bookmark is
located inside a span, its parent is the span element instead of a regular
paragraph. So another method is provided, that returns the main text container
of the bookmark. In the following example, the first line returns the parent of
a given bookmark (whatever the kind of element), while the second one returns
the paragraph (or heading) where the bookmark is located::

  context.get_bookmark("BM1").parent
  context.get_paragraph_by_bookmark("BM1")

The ``get_bookmark_offset()`` context method allows the user to get the offset of a given bookmark in the host ODF element. Beware: this offset is related to the text of the parent element (which could be a text span).

The ``remove_bookmark()`` method may be used from any context above the
container or the target bookmark, including the whole document, in order to
delete a bookmark whatever its container. The only required argument is the
bookmark name. Alternatively, a ``remove()`` method (without argument) may be
called from the ``odf_bookmark`` object.

Range bookmarks
~~~~~~~~~~~~~~~~
A range bookmark is an identified text range which can spread across paragraph
frontiers. It's a named content area, not dependant of the document tree
structure. It starts somewhere in a paragraph and stops somewhere in the same
paragraph or in a following one. Technically, it's a pair of special position
bookmarks, so called bookmark start and bookmark end, owning the same name.

The API allows the user to create a range bookmark and name it through an
existing content, as well as to retrieve and extract it according to its name.

A range bookmark is inserted using the ``set_bookmark()`` like a position
bookmark, but this method must be called twice (knowing that the start and end
points aren't always in the same context) and an additional ``role`` parameter
is required. The value of ``role`` is either ``start`` or ``end``. The
application must issue two explicit calls with the same bookmark name but with
the two different values of ``role``. Example::

  paragraph1.set_bookmark("MyRange", position=12, role="start")
  paragraph2.set_bookmark("MyRange", position=3, role="end")

The sequence above creates a range bookmark starting at a given position in a
paragraph and ending at another position in another paragraph.

The balance of ``start`` and ``end`` marks for a given range bookmark is not
automatically checked. However, any ``set_bookmark()`` call with the same name
and the same ``role`` value fails with an error message, so the user can't
incidentally create redundant ``start`` or ``end`` marks. In addition,
``get_bookmark()`` will trigger a warning if the target is a non-balanced range
bookmark.

The consistency of an ``odf_bookmark`` object may be verified using its
``check()`` method, that returns ``true`` if and only if the range bookmark has
defined start and end points AND if the end point is located after the start
point, or ``false`` otherwise.

The ``start_parent()`` and ``end_parent()`` methods, provided by the
``odf_bookmark`` object, allow the user to get the elements containing the start
point and the end point of the calling bookmark, respectively. The generic
``parent()`` method, when called from a range bookmark, just behave like
``start_parent()``. If ``start-parent()`` is called from a position bookmark,
it behaves like ``parent()``. On the other hand, ``end_parent()`` returns a
null value when called from either a position bookmark or a non-balanced
range bookmark. Note that is ``check()`` returns ``false`` while both
``start_parent()`` and ``end_parent()`` return something, we know that the end
point is located somewhere before the start point.

A ``get_text()`` method returns the text content of the bookmark as a flat
string, without the structure; this string is just a concatenation of all the
pieces of text occurring in the range, whatever the style and the type of their
respective containers; however, the paragraph boundaries are replaced by blank
spaces. Note that, when called from a position bookmark or an inconsistent range
bookmark, ``get_text()`` just returns an null value, while it always returns a
string (possibly empty) when called from a range bookmark.

A range bookmark (consistent or not) may be safely removed through the
``remove_bookmark()`` method (which deletes the start point and the end point).

A range bookmark can be safely processed only if it's entirely contained in the
calling context. A context that is not the whole document can contain a bookmark
start or a bookmark end but not both.  In addition, a bookmark spreading across
several elements gets corrupt if the element containing its start point or its
end point is later removed.

The ``remove_bookmark()`` method (which can be uses at any level, including the
whole document) allows the applications to safely remove balanced and
non-balanced range bookmarks. In addition, a ``clean_marks()`` automatically
removes non-balanced range bookmarks (as well as non-balanced index marks).
The same apply to the ``odf_bookmark`` based ``remove()`` method.

However, the present version of lpOD doesn't check the relative positions of
the start and end points of a range bookmark. As a consequence, due to some
moves in the document structure or any other reason, the applications are
responsible for preventing any bookmark end point to be located before the
corresponding start point.

Index marks [tbc]
-----------------

Index marks are bookmarks with particular roles. There are three kind of index
marks, namely:

- ``lexical`` marks, whose role is to designate text positions or ranges in
  order to use them as entries for a lexical (or alphabetical) index;
- ``toc`` marks, created to become the source for tables of contents (as soon
  as these tables of contents are generated from TOC marks instead of headings);
- ``user`` marks, which allow the user to associate sets text positions or
  ranges with arbitrary categories.

Bibliography marks [todo]
--------------------------


