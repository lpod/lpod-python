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


.. contents::

Text marks and indices
======================

Position bookmarks
------------------
A position bookmark is a location mark somewhere in a text container, which is
identified by a unique name, but without any content.

A bookmark is created "in place", in a given element at a given position.  The
name and the target element are mandatory arguments. By default, the bookmark is put before the first character of the content.

The position can be explicitly provided by the user. Alternatively, the user can provide a regular expression, so the bookmark is set before the first substring that matches the expression::

  document.create_bookmark("BM1", paragraph, text="xyz")
  document.create_bookmark("BM2", paragraph, position=4)

The first instruction above sets a bookmark before the first substring matching
the given expression (here ``xyz``), which is processed as a regular expression. The second instruction sets a bookmark in the same paragraph at a given (zero-based), so before the 5th character.

In order to put a bookmark according to a regex that could be matched more than
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

Another method allows the user to get the offset of a given bookmark in the host ODF element. Beware: this offset is related to the text of the parent element (which could be a text span).

Range bookmarks
----------------
A range bookmark is an identified text range which can spread across paragraph
frontiers. It's a named content area, not dependant of the document tree
structure. It starts somewhere in a paragraph and stops somewhere in the same
paragraph or in a following one. Technically, it's a pair of special position
bookmarks, so called bookmark start and bookmark end, owning the same name.

The API allows the user to create a range bookmark and name it through an
existing content, as well as to retrieve and extract it according to its name.

Provided methods allow the user to get

- the pair of elements containing the bookmark start and the bookmark end
  (possibly the same);
- the text content of the bookmark (without the structure).

A retrieved range bookmark can be safely removed through a single method.

A range bookmark can be safely processed only if it's entirely contained in the
calling context. A context that is not the whole document can contain a bookmark
start or a bookmark end but not both.  In addition, a bookmark spreading across
several elements gets corrupt if the element containing its start point or its
end point is later removed.

