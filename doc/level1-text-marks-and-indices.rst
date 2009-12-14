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

A text bookmark can either mark a text position or a text range. It's either a
mark associated to a position in a text, or a pair of location marks that
defines a delimited range of text. Both are created "in place" using a
``set_bookmark()`` context-based method, whose first argument is the unique name
of the bookmark, and which takes named parameters that depend on the type of
bookmark. The calling element should be a paragraph, a heading or a text span.

Position bookmarks
~~~~~~~~~~~~~~~~~~

A position bookmark is a location mark somewhere in a text container, which is
identified by a unique name, but without any content. Its just a named location
somewhere in a text container.

By default, the bookmark is created and inserted using ``set_bookmark()``
before the first character of the content in the calling element (which may be a 
paragraph, a heading, or a text span). As an example, this instruction creates
a position bookmark before the first character of a paragraph::

  paragraph.set_bookmark("MyFirstBookmark")

This very simple instruction is appropriate as long as the purpose in only to
associate a significant and persistent name to a text container in order to
retrieve it later (with an interactive text processor or by program with lpOD or
another ODF toolkit). It's probably the most frequent use of bookmarks. However,
the API offers more sophisticated functionality.

The position can be explicitly provided by the user with a ``position``
parameter. Alternatively, the user can provide a regular expression using a
``before`` or ``after`` parameter, so the bookmark is set immediately before or
after the first substring that matches the expression. The code below
illustrates these possibilities::

  paragraph.set_bookmark("BM2", position=4)
  paragraph.set_bookmark("BM1", before="xyz")

This method returns something in case of success (the returned value is just
the ``odf_element`` corresponding to the new bookmark), or a null value
otherwise.

For performance reasons, the uniqueness of the given name is not checked. If
needed, this check should be done by the applications, by calling
``get_bookmark()`` (with the same name and from the document context) just
before ``set_bookmark()``; as long as ``get_bookmark()`` returns a null value,
the given bookmark name is not in use.

There is no need to specify the creation of a position bookmark;
``set_bookmark()`` creates a position bookmark by default; an additional
``role`` parameter is required for range bookmarks only, as introduced later.

The first instruction above sets a bookmark before the first substring matching
the given expression (here ``xyz``), which is processed as a regular expression. The second instruction sets a bookmark in the same paragraph at a given (zero-based), so before the 5th character.

In order to put a bookmark according to a regexp that could be matched more than
once in the same paragraph, it's possible to combine the position and text
options, so the search area begins at the given position. The following example
puts a bookmark at the end of the first substring that matches a given
expression after a given position::

  paragraph.set_bookmark("BM3", position=4, after="xyz")

In order to retrieve the position of a bookmark relatively to the containing
text, use the ``get_bookmark_position()`` method from the host element.

A bookmark can be retrieved by its unique name using ``get_bookmark()``.
The ODF element that contains the bookmark then can be obtained as the parent of
the bookmark element. However, if the bookmark is located inside a span, its
parent is the span element instead of a regular paragraph. So another method is
provided, that returns the main text container of the bookmark. In the following 
example, the two lines return the text container (whatever its type, paragraph,
heading or text span) where the bookmark is located::

  element = context.get_bookmark("BM1").parent
  element = context.get_element_by_bookmark("BM1")

The ``remove_bookmark()`` method may be used from any context above the
container or the target bookmark, including the whole document, in order to
delete a bookmark whatever its container. The only required parameter is the
bookmark name.

Range bookmarks
~~~~~~~~~~~~~~~~

A range bookmark is an identified text range which can spread across paragraph
frontiers. It's a named content area, not dependant of the document tree
structure. It starts somewhere in a paragraph and stops somewhere in the same
paragraph or in a following one. Technically, it's a pair of special position
bookmarks, so called bookmark start and bookmark end, owning the same name.

The API allows the user to create a range bookmark within an existing content,
as well as to retrieve and extract it according to its name. Range bookmarks
share some common functionality with position bookmarks

A range bookmark is inserted using the ``set_bookmark()`` like a position
bookmark. However, this method must be sometimes called twice knowing that the
start and end points aren't always in the same context). In such a situation,
an additional ``role`` parameter is required. The value of ``role`` is either
``start`` or ``end``, and the application must issue two explicit calls with the
same bookmark name but with the two different values of ``role``. Example::

  paragraph1.set_bookmark("MyRange", position=12, role="start")
  paragraph2.set_bookmark("MyRange", position=3, role="end")

The sequence above creates a range bookmark starting at a given position in a
paragraph and ending at another position in another paragraph.

Knowing that the default position is 0, and the last position in a string is -1,
the following example creates a range bookmark that just covers the full content
of a single paragraph::

  paragraph.set_bookmark("AnotherBookmark", role="start")
  paragraph.set_bookmark("AnotherBookmark", role="end", position=-1)

The balance of ``start`` and ``end`` marks for a given range bookmark is not
automatically checked. However, any ``set_bookmark()`` call with the same name
and the same ``role`` value as a previous one fails, so the user can't
incidentally create redundant ``start`` or ``end`` marks.

If the created object is a range bookmark, ``set_bookmark()`` returns an ODF
elements, representing the start point or the end point, according to the
``role`` parameter. In case of failure it returns a null value.

A range bookmark may be entirely contained in the same paragraph. As a
consequence, it's possible to create with a single call of ``set_bookmark()``,
with parameters that make sense for such a situation. If a ``content``
parameter, whose value is a regexp, is provided instead of the ``before`` or
``after`` options, the given expression is regarded as covering the whole text
content of to be enclosed by the bookmark, and this content is supposed to be
entirely included in the calling paragraph. So the range bookmark is immediately
created and automatically balanced. As soon as ``content`` is present, ``role``
is not needed (and is ignored). Like ``before`` and ``after``, ``content`` may
be combined with ``position``. In addition, the range bookmark is automatically
complete and consistent.

Note that the following instruction::

  paragraph.set_bookmark("MyRange", content="xyz")

does exactly the same job as the sequence below (provided that the calling
paragraph remains the same between the two instructions)::

  paragraph.set_bookmark("MyRange", before="xyz", role="start")
  paragraph.set_bookmark("MyRange", after="xyz", role="end")

Another way to create a range bookmark in a single instruction is the use of
a ``range`` parameter instead of ``content``. The value of ``range`` must be
a pair of non-negative integer values specifying the start and end offsets
of the bookmark relatively to the text content of the calling element. Knowing
that 0 is the first position and -1 the last, a (0,-1) range value means that
the whole text of the element will become the content of the bookmark. The code
hereafter creates a bookmark running between two given positions in a single
paragraph::

  paragraph.set_bookmark("MyRange", range=(3,15))

When ``range`` is provided, the second position can't before the first one and
the method fails if one of the given positions is off limits, so the consistency
of the bookmark is secured as soon as ``set_bookmark()`` returns an non-null
value with this parameter.

The ``range`` and ``content`` parameters may be combined in order to create a
range bookmark whose content matches a given filter string AND is located
in a delimited substring in the calling element. The next example creates a
range bookmark whose content is the first substring that matches a "xyz"
expression in search space that excludes the 5 first and the 5 last characters::

  paragraph.set_bookmark("MyRange", content="xyz", range=(5, -6))

...provided that the calling paragraph contains at least 13 characters and that
a "xyz" string appear in the delimited area.

When ``set_bookmark()`` creates a range bookmark in a single instruction, it
returns a pair of elements according to the same logic as ``get_bookmark()``
(see below).

The consistency of a range bookmark may be verified using the
``check_bookmark()`` context- or document-based method, whose mandatory argument
is the name of the bookmark, and that returns ``true`` if and only if the
corresponding range bookmark exists, has defined start and end points AND if the
end point is located after the start point. This method returns ``false``
if anyone of these conditions is not met (as a consequence, ``get_bookmark()``
may succeed while ``check_bookmark()`` fails for the same bookmark name). Of
course, ``check_bookmark()`` always succeed with a regular position bookmark,
so, with a position bookmark, this method is just en existence check.

A range bookmark is not a single object; it's a pair of distinct ODF elements
whose parent elements may differ. With a range bookmark, ``get_bookmark()``
returns the pair instead of a single element like with a position bookmark.
Of course, the first element of the pair is the start point while the second
one is the end point. So it's possible, with the generic element-based
``parent()`` method, to select the ODF elements that contain respectively the
start and the end points (in most situations, it's the same container).

The context-based ``get_element_by_bookmark()``, when the given name designates
a range bookmark, returns the parent element of the start point by default.
However, it's possible to use the same ``role`` as with ``set_bookmark()``; if
the ``role`` value is ``end``, then ``get_element_by_bookmark()`` will return
the container of the end point (or null if the given name designates a position
bookmark or an non-consistent range bookmark whose end point doesn't exist).

A ``get_bookmark_text()`` context- or document-based method whose argument is
the name of a range bookmark returns the text content of the bookmark as a flat
string, without the structure; this string is just a concatenation of all the
pieces of text occurring in the range, whatever the style and the type of their
respective containers; however, the paragraph boundaries are replaced by blank
spaces. Note that, when called with a position bookmark or an inconsistent
range bookmark, ``get_bookmark_text()`` just returns an null value, while it
always returns a string (possibly empty) when called from a regular range
bookmark.

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

However, the present version of lpOD doesn't check the relative positions of
the start and end points of a range bookmark when it's spread across two or
more ODF elements. As a consequence, due to some moves in the document structure
or any other reason including logic errors, the applications are responsible for
preventing any bookmark end point to be located before the corresponding start
point.

Index marks
-----------

Index marks are bookmarks with particular roles. There are three kind of index
marks, namely:

- ``lexical`` marks, whose role is to designate text positions or ranges in
  order to use them as entries for a lexical (or alphabetical) index;
- ``toc`` marks, created to become the source for tables of contents (as soon
  as these tables of contents are generated from TOC marks instead of headings);
- ``user`` marks, which allow the user to create custom indices (which could be
  ignored by the typical TOC or lexical index generation features of the
  office applications).

An index mark, just like a text bookmark, is either a mark associated to a
position in a text, or a pair of location marks that defines a delimited range
of text.

An index mark is created in place using the ``set_index_mark()`` context-based
method, according to the same basic logic ``set_bookmark()``, with some
important differences:

- because an index mark is not a named object, the first argument of
  ``set_index_mark()`` is not really a name, like a bookmark name; this
  argument (which remains mandatory) is either a technical identifier, or
  a significant text, according to the kind of index mark;

- for a position index mark (which, by definition, has no text content), the
  first argument is a text string that is displayed in the associated index
  (when this index is generated);
  
- for a range index mark (which, by definition, has a text content), the first
  argument is only a meaningless but unique key that is internally used in order
  to associate the two ODF elements that represent the start point and the end
  point of the range; this key should not be displayed by a typical interactive
  text processor, and is not reliable as a persistent identifier knowing that
  an ODF-compliant application could silently change it as soon as the document
  is edited;

- an additional ``type`` option whose possible values are ``lexical``, ``toc``,
  and ``user`` specifies the functional type; the default is ``lexical``;

- when the ``user`` type is selected, an additional ``index name`` parameter is
  required; its value is the name of the user-defined index that will (or could)
  be associated to the current index entry; this name could be regarded as the
  arbitrary name of an arbitrary collection of text marks;

- if the ``index name`` argument is provided, the mandatory value of ``type``
  is ``user``; as a consequence, if ``index name`` is set, the default ``type``
  becomes ``user`` and the ``type`` parameter is not required;

- according to the ODF 1.1 specification, the range of an index mark can't
  spread across paragraph boundaries, i.e. the start en end points must be
  contained in the same paragraph; as a consequence, a range index mark may
  (and should) be always created using a single ``set_index_mark()``;

- like ``set_bookmark()``, ``set_index_mark()`` returns a pair of ODF elements
  when it creates a range index mark; if the application needs to set particular
  properties (using the ``set_attribute()`` generic method or otherwise) to the
  index mark, the first element of the pair (i.e. the start point element) must
  be used.

The example hereafter successively creates, in the same paragraph, a range TOC
mark, two range index marks associated to the same user-defined index, and a
lexical position index mark at the default position (i.e. before the first
character of the paragraph)::

  paragraph.set_index_mark("id1", type="toc", range=(3,5))
  paragraph.set_index_mark("id2", index_name="OpenStandards", content="XML")
  paragraph.set_index_mark("id3", index_name="OpenStandards", content="ODF")
  paragraph.set_index_mark("Go There" type="lexical")

Not that the last instruction (unlike the preceding ones) uses a possibly
meaningful text as the first argument instead of an arbitrary technical
identifier. Because this instruction creates a lexical index entry, the given
text will appear in the document as a reference to the paragraph as soon as a
standard lexical index is generated (by the current program or later by an
end-user office software).

According to the ODF 1.1 specification, the start and end points of an index
entry must belong to the same paragraph. This additional constraint is not
automatically checked by ``set_index_mark()``; however it may be explicitly
checked (as other constraints) with the ``check_index_mark()`` method, called in
the same way as ``check_bookmark()``, with the identifier used to create the
mark.

In addition, there is a ``get_index_marks()`` context-based method that allows
the applications to retrieve a list of index entries present in a document or in
a more restricted context. This method needs a ``type`` parameter, whose
possible values are the same as with ``set_index_mark()``, in order to select
the kind of index entries; the ``lexical`` type is the default. If the ``user``
type is selected, the name of the user-defined index must be provided too,
through a ``index name`` parameter. However, if ``index name`` is provided,
the ``user`` type is automatically selected and the ``type`` parameter is not
required.

The following example successively produces three lists of index marks, the
first one containing the entries for a table of contents, the second one the
entries of a standard lexical index, and the third one the entries dedicated
to an arbitrary user-defined index:: 

  toc = document.get_index_marks(type="toc")
  alphabetical_index = document.get_index_marks()
  foo_index = document.get_index_marks(index_name="foo")

The API provides a document- or context-based ``remove_index_marks()`` method
that, in a single instruction, removes all the index marks of a given kind,
that is the ``lexical`` category by default. It's possible to selectively remove
the entries associated to a given custom index, with a ``index name`` parameter,
or all the entries corresponding to a given type, using the ``type`` argument.
On the other hand, due to the lack of persistent and reliable unique names,
there is no level 1 method to selectively remove an individual index entry
according to its identifier (of course, a lot of workarounds are available for
ODF-aware progammers with the XPath-based level 0 methods).

Bibliography marks
------------------

A bibliography mark is a particular index mark. It may be used in order to
store anywhere in a text a data structure which contains multiple attributes but
whose only one particular attribute, so-called the "identifier" is visible at
the place of the mark. All the other attributes, or some of them, may appear in
a bibliography index, when such an index is generated (according to index
format).

A bibliography mark is created using the ``set_bibliography_mark()`` method from
a paragraph, a heading or a text span element. Its placement is controlled with
the same arguments as a position bookmark, i.e. ``position``, ``before`` or
``after`` (look at the Text Bookmarks section for details). Without explicit
placement parameters, the bibliography mark is inserted at the beginning of the
calling container.

Unlike ``set_bookmark()``, ``set_bibliography_mark()`` doesn't require a name as
its first argument, but it requires a named ``type`` parameter whose value
is one of the publication types listed in the §7.1.4 of the ODF 1.1
specification (examples: ``article``, ``book``, ``conference``, ``techreport``,
``masterthesis``, ``email``, ``manual``, ``www``, etc). This predefined set of
types is questionable, knowing that, for example, the standard doesn't tell us
if the right type is ``www`` or ``manual`` for, say, a manual that is published
through the web, but the user is responsible for the choice.

Beside the ``type`` parameter, a ``identifier`` parameter (that is not a real
identifier in spite of its name) is supported. This so-called ``identifier``,
unlike a real identifier, is a label that will be displayed in the document at
the position of the bibliography entry by a typical ODF compliant viewer or
editor and that will provide the end-user with a visible link between the
bibliography mark in the document body and a bibliography index later generated
elsewhere. Nothing in the ODF 1.1 specification prevents the applications from
creating the same bibliography mark repeatedly, and from inserting different
bibliography marks with the same ``identifier``.

The full set of supported parameters correspond to the list of possible
attributes of the bibliography mark element, defined in the §7.1.4 of the
ODF 1.1 specification. All them are ``text:`` attributes, but
``set_bibliography_mark()`` allows the use of named parameters without the
``text:`` prefix (examples: ``author``, ``title``, ``editor``, ``year``,
``isbn``, ``url``, etc). The instruction below inserts in a paragraph,
immediately after the first occurrence of the "lpOD documentation" substring, a
bibliography entry that represents the lpOD documentation, and whose visible
label at the insertion point could be something like "[lpOD2009]" in a typical
document viewer::

  paragraph.set_bibliography_mark(
    identifier="lpOD2009",
    type="manual",
    after="lpOD",
    year="2009",
    month="december",
    url="http://docs.lpod-project.org",
    editor="The lpOD Team"
    )	
 
``set_bibliography_mark()`` returns an ODF element whose any property may be
set or changed later through the element-based ``set_attribute()`` method.

Knowing that there is no persistent unique name for this class of objects, there
is a context-based ``get_bibliography_marks()`` method that returns the list of
all the the bibliography marks. If this method is called with a string argument
(which may be a regexp), the search is restricted to the entries whose so-called
``identifier`` property is defined and matches this argument. Each element of
the returned list (if any) may be then checked or updated using the generic
``get_attribute()``, ``get_attributes()``, ``set_attribute()`` and
``set_attributes()`` methods.

