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


Other Structured Containers
============================

.. contents::
   :local:

Item lists
----------

A list is a structured object that contains an optional list header followed by
any number of list items. The list header, if defined, contains one or more
paragraphs that are displayed before the list. A list item can contain
paragraphs, headings, or lists. Its properties are ``style``, that is an
appropriate list style, and ``continue numbering``, a boolean value that, if
true, means that *if the numbering style of the preceding list is the same as the current list, the number of the first list item in the current list is the number of the last item in the preceding list incremented by one* (default=false).

  .. figure:: figures/lpod_list.*
     :align: center

A list is created using ``odf_create_list()``, then inserted using
``insert_element()`` as usual.

A list header is created "in place" with ``set_header()``, called from a list
element; this method returns an ODF element that can be used later as a context
to append paragraphs in the header. Alternatively, it's possible to call the
list-based ``set_header()`` with one or more existing paragraphs as arguments,
so these paragraphs are immediately incorporated in the new list header. Note
that every use of ``set_header()`` replaces any existing header by a new one.

Regular list items are created in place (like the optional list header) using
``add_item()`` wich creates one or more new items and inserts them at a
position which depends on optional parameters, according to the same kind
of logic than the tabble-based ``add_row()`` method. Without any argument, a
single item is appended at end of the list. An optional ``before`` named
parameter may be provided; if defined, the value of this parameter must be a
row number (in numeric, zero-based form) in the range of the list; the new
items are inserted *before* the original item that existed at the given
position. Alternatively, a ``after`` parameter may be provided instead of
``before``; it produces a similar result, but the new items are inserted
*after* the given position. If a additional ``number`` parameter is provided
with a integer value, the corresponding number of identical items are
inserted in place.

By default, a new item is created empty. However, as a shortcut for the most
common case, it's possible to directly create it with a text content. To do
so, the text content must be provided through a ``text`` parameter; an
optional ``style`` parameter, whose value is a regular paragraph style, may
provided too. The new item is then created with a single paragraph as content
(that is the most typical situation).

Another optional ``start value`` parameter may be set in order to restart the
numbering of the current list at the given value. Of course, this start value
apply to the first inserted item if ``add_item()`` is used to create many items
in a single call.

``add_item()`` returns the newly created list of item elements. In addition,
an existing item may be selected in the list context using ``get_item()`` with
its numeric position. A list item is an ODF element, so any content element
may be attached to it using ``insert_element()``.

Note that, unlike headings, list items don't have an explicit level property.
All the items in an ODF list have the same level. Knowing that a list may be
inside an item belonging to another list, the hierarchy is represented by the
structural list imbrication, not by item attributes.


Sections
--------

A section is a named region in a text document. It's a high level container that
can include one or more content elements of any kind (including sections, that
may be nested).

The purpose of a section is either to assign certain formatting properties to a
document region, or to include an external content.

A section is created using ``odf_create_section()`` with a mandatory name
as the first argument and the following optional parameters:

- ``style``: the name of a section style, already existing or to be defined;
- ``url`` : the URL of an external resource that will provide the content of the
  section;
- ``protected``: a boolean that, if true, means that the section should
  be write-protected when the document is edited through a user-oriented,
  interactive application (of course, such a protection doesn't prevent
  an lpOD-based tool from modifying the table)(default is false);
- ``protection key``: a (supposedly encrypted) string that represents
  a password; if this parameter is set and if ``protected`` is true,
  a end-user interactive application should ask for a password that matches
  this string before removing the write-protection (beware, such a protection
  is *not* a security feature);
- ``display``: boolean, tells that the section should be visible (default is 
  true).

Draw pages
----------

Draw pages are structured containers belonging to presentation or drawing
documents. They shouldn't appear in text or spreadsheet documents.

A draw page can contain forms, drawings, frames, presentation animations, and/or
presentation notes (§9.1.4 in the ODF specification).

  .. figure:: figures/lpod_drawpage.*
     :align: center

*[Unfinished diagram]*

A draw page is created using ``odf_create_draw_page()`` and integrated through
``insert_element()``. Note that a draw page should be inserted at the document
body level, knowing that it's a top level content element.

A draw page must have an identifier (unique for the document) and may have the
following parameters, to be set at creation time or later:

- ``name``: an optional, but unique if provided, name (which may be made visible
   for the end-users);

- ``style``: the name of a drawing page style (existing or to be defined);

- ``master``: the name of a master page whose structure is appropriate for
   draw pages (beware, a master page defined for a text document don't always
   fit for draw pages);

- ``layout``: the name of a *presentation page layout* as defined
   in §14.15 of the ODF specification (if such a layout is used); beware, such
   objects are neither similar nor related to general *page layouts* as defined
   in §14.3 (a general page layout may be used through a *master page* only,
   and should never be directly connected to a draw page) (sorry, this confusing
   vocabulary is not a choice of the lpOD team;-)

The following example creates a draw page with these usual parameters and
integrates it as the last page of a presentation document::

   dp = odf_create_draw_page('xyz1234',
                           name='Introduction',
                           style='DrawPageOneStyle',
                           master='DrawPageOneMaster',
                           layout='DrawPageOneLayout
                           )
   document.append_element(dp)

All these parameters may retrieved or changed later using ``get_properties()``
and ``set_properties()`` with draw page objects.

An existing draw page may be retrieved in the document through
``get_draw_page()`` with the identifier as argument.

Populating a draw page doesn't require element-specific methods, knowing that:

- all the fixed parts, the layout and the background are defined by the
   associated ``style``, ``master`` and ``layout``;
- all the content objects are created separately and attached to the draw page
   using the regular ``insert_element()`` or ``append_element()`` method from
   the draw page object.

