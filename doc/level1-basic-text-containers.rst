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

Basic text containers
=====================

.. contents::

Paragraphs
-----------

A paragraph element inherits all the basic element features introduced above,
and owns the following ones.

All the visible text content of a document is hold in paragraphs (and in
*headings*, which are special paragraphs, cf. later in this documentation).
A paragraph is basically a text container associated with a layout style.

The text content may be directly hold as the text of the paragraph element;
however, a paragraph can contain sub-paragraph elements so-called *spans*
(introduced later in this documentation).

As soon as a piece of text is displayed somewhere in a document,
whatever the context, this text belongs to a paragraph.

In a text document, paragraphs may appear as top level elements, i.e.
directly in the document body, as well as inside complex containers, such as
lists, tables, text boxes. Paragraphs may be used as components of page headers
or footers. In other documents, a paragraph can't appear as a top level element,
knowing that any visible text is embedded in a structured container (table cell,
text box, etc).

Creation and attachment
~~~~~~~~~~~~~~~~~~~~~~~
A paragraph can be created with a given style and a given text content. The
default content is an empty string. There is not default style; a paragraph can
be created without explicit style, as long as the default paragraph style of the
document is convenient for the application. The style and the text content can
be set or changed later.

A paragraph is created (as a free element) using the ``odf_create_paragraph()``
function, with a ``text`` and a ``style`` optional parameters. It may be
attached later through the standard ``append_element()`` or
``insert_element()`` method::

   p = odf_create_paragraph(text='My first paragraph', style='TextBody')
   document.append_element(p)

Retrieval
~~~~~~~~~
Like any element, a paragraph can be retrieved in a given context using
``get_paragraph_by_position()`` or ``get_paragraph_by_content()``, and
``get_paragraph_list()`` returns all the paragraphs in the context.

The ``get_paragraph_list()`` with a ``style`` named parameter restricts the
search in order to get the paragraphs which use a given style.

Text processing
~~~~~~~~~~~~~~~
The traditional string editing methods (i.e. regex-based search & replace
functions) are available against the text content of a paragraph.

``search()`` in a element-based method which takes a search string (or a
regular expression) as argument a,d returns the position of the first substring
matching the argument in the text content of the element. A null return value
means no match. This method works with the direct text content of the calling
element, not with the children, so it makes sense with paragraphs, headings and
text spans only.

``replace()`` is a context-based method. It takes two arguments, the first one
being a search string like with ``search()``, the second one a text which will
replace any substring matching the search string. The return value of the
method is the total number of matches. If the second argument is an empty
string, every matching substring is just deleted without replacement. If the
second argument is missing, then nothing is changed, and the method just counts
the number of matches. This method is context-based, so it recursively works on
all the paragraphs, headers and spans below the calling element; the calling
element may be any ODF element, including the elements that can't directly own a
text content. It may be called at the document level.

Multiple spaces and intra-paragraph breaks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
According to the ODF specification, a sequence of multiple spaces is regarded
as a single space, so multiple spaces must be represented by an appropriate
ODF element. In the same way, tabulation marks and line breaks can't be
directly included in the text content, and must be replaced by appropriate
ODF elements. This API transparently does the job: it allows the user to put
in a paragraph a text strings containing multiple spaces, tab stops ("\t")
and/or line breaks ("\n").

Headings
---------
All the features that apply to paragraphs, as described above, apply to headings
as well. As a consequence, a heading may be regarded as a subclass of the
paragraph class.

However, a heading is a special paragraph which owns additional properties
related to its hierarchical level and its numbering. As an consequence, some
heading-specific methods are provided, and the constructor function is
``odf_create_heading()``. The ``text`` and ``style`` parameters are allowed
like with ``odf_create_paragraph()``. In addition, this constructor gets more
optional parameters:

- ``level`` which indicates the hierarchical level of the heading (default 1,
  i.e. the top level);

- ``restart numbering``, a boolean which, if true, indicates that the numbering
  should be restarted at the current heading (default false);

- ``start value`` to restart the heading numbering of the current level at a
  given value;

- ``suppress numbering``, a boolean which, if true, indicates that the heading
  must not be numbered (default false).

See below for explanations about level and numbering.

In addition, the layout of the headings depends partly on the paragraph style
that individually apply to each one, and partly on the outline style of the
document (see the "Outline style" section in the present document).

Heading level
~~~~~~~~~~~~~
A heading owns a special property which indicates its hierarchical level in the
document. A "level" property can be set at creation time or later and changed at
any time. A heading without a level attribute is assumed to be at level 1, which
is the top level. The level may be any positive integer value (while the ODF
spec doesn't set an explicit limit, we don't recommend levels beyond 10).

Heading numbering
~~~~~~~~~~~~~~~~~~
Whatever the visibility of the numbers, all the headings of a given level are
potentially numbered. By default, the numbering is related to the whole
document starting to 1. However, optional properties allow the user to change
this behaviour.

An arbitrary, explicit numbering value can be set, so the automatic numbering
restarts from this value from the target heading element and apply to the
following headings at the same level.

The automatic numbering can be inhibited through an optional property which
prevents the current heading from being numbered.

In addition, the API allows the users to provide a heading with an arbitrary
hidden number. A hidden number is a static, user-provided value available for
applications that can't dynamically calculate the numbering, but safely ignored
by applications that support dynamic numbering in text documents.

Text spans
----------
A text span, in the lpOD scope, is a delimited area included in a paragraph or
a heading. It's a sub-paragraph text container whose essential function is to
associate a particular feature to a limited text run instead of a whole
paragraph.

There are several kinds of text spans.

- Style spans: a text span can be defined in order to apply a special style to
  a part of the content of a paragraph/heading. As a consequence, it's
  associated to a text style.
- Hyperlinks: a hyperlink can be defined in order to associate a part of the
  content of a paragraph/heading to another content element in the current
  document or to an external resource.

Unlike paragraphs and headings, spans are created "in place", i.e. their
creation methods create and directly insert them in an existing container.

A style span is created through a ``set_span()`` method  from the object that
will contain the span. This object is a paragraph, a heading or an existing
styling span. The method must be called with a ``style`` named parameter whose
value should be the name of any text style (common or automatic, existing or to
be created in the same document). ``set_span()`` may uses a string or a regular
expression, which may match zero, one or several times to the text content of
the calling object, so the spans can apply repeatedly to every substring that
matches. The string is provided through a ``filter`` parameter. Alternatively,
``set_span()`` may be called with given ``position`` and ``length`` parameters,
in order to apply the span once whatever the content. Note that ``position`` is
an offset that may be a positive integer (starting to 0 for the 1st position),
or a negative integer (starting to -1 for the last position) if the user prefers
to count back from the end of the target. If the ``length`` parameter is omitted
or set to 0 the span runs up to the end of the target content. If ``position``
is out of range, nothing is done; if ``position`` is OK, extra length (if any)
is ignored. The following instructions create two text spans with a so-called
"HighLight" style; the first one applies the given style to any "The lpOD
Project" substring while the second one does it once on fixed length substring
at a given position, ``p`` being the target paragraph::

   p.set_span(filter='The lpOD Project', style='HighLight')
   p.set_span(position=3, length=5, style='HighLight')

A hyperlink span is created through ``set_hyperlink()``, which waits for the
same positioning parameters (by regex or by position and length). However,
there is no style, and a ``url`` parameter (whose value is any kind of path
specification that is supported by the application) is required instead.
A hyperlink span can't contain any other span, while a style span can contain
one or more spans. As a consequence, the only one way to provide a hyperlink
span with a text style consists of embedding it in a style span.

The objects that can directly contain text spans are paragraphs, headings and
style spans. However, ``set_span()`` and ``set_hyperlink()`` may be called
from any higher level containers that can contain paragraphs or headings,
including the whole document. The span creation process may work recursively and
repeatedly in all the paragraphs, and spans below the calling ODF element. Both
return the list of the created span objects; a span object is an ODF element
itself. However, it's possible to prohibit this behaviour with a boolean
``norecurse`` parameter; if this option is set to ``true``, it prevents
``set_span()`` or ``set_hyperlink()`` from searching and processing the children
of the calling ODF element; of course, nothing is done when ``norecurse`` is the
current object is not able to directly able to contain text spans.

As an example, the instruction below applies the "HighLight" text style to
every "ODF" and "OpenDocument" substring in the ``p`` context::

   p.set_span(filter='ODF|OpenDocument', style='HighLight')

The following example associates an hyperlink in the last 5 characters of the
``p`` container (note that the ``length`` parameter is omitted, meaning that
the hyperlink will run up to the end)::

   p.set_hyperlink(position=-5, url='http://here.org')

The sequence hereafter show the way to set a style span and a hyperlink for
the same text run. The style span is created first, then it's used as the
context to create a hyperlink span that spreads over its whole content::

   s = p.set_span(filter='The lpOD Project', style='Outstanding')
   s.set_hyperlink(position=0, url='http://www.lpod-project.org')

