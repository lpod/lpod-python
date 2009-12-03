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

###################
Navigation Cookbook
###################

.. contents::
   :local:

In this first tutorial we will learn the basics of navigating through the
document and find the element we are looking for.

Let's first open a document::

    >>> from lpod.document import odf_get_document
    >>> document = odf_get_document('http://example.com/odf/cookbook')

As lpOD is built upon a Virtual File System, we can transparently open
documents through different URIs.

The `document` object is the central point of the API. From it you can
access parts of the document. The following parts are common:

  - `meta`: Specification-defined and user-defined metadata;
  - `content`: The content the user is typing and some automatic styles;
  - `styles`: Library of styles and the headers and footers of page layouts;

There are other optional parts like images and other media the document is
embedding.

See :doc:`Metadata Cookbook <cookbook-metadata>` or :doc:`Styles Cookbook
<cookbook-styles>` for specific information.

Accessing the Content
=====================

For the navigation purpose, we need to access the body::

    >>> content = document.get_content()
    >>> body = content.get_body()

The `content` object is a part object from where you can access the XML tree
and the automatic styles stored in this part.

This frequent usage can be shortened from the document::

    >>> body = document.get_body()

The `body` object is an XML element from which we can access one or several
other elements we are looking for.

Accessing a List of Elements
============================

Should you need to access all elements of a kind, there are the
`get_xxx_list` methods, where `xxx` can be `paragraph`, `heading`, `list`,
`table`, etc.

Some examples::

    >>> body.get_heading_list()
    [<lpod.heading.odf_heading object at 0x22a0090>, <lpod.heading.odf_hea...
    >>> body.get_paragraph_list()
    [<lpod.paragraph.odf_paragraph object at 0x22a04d0>, <lpod.paragraph.o...
    >>> body.get_list_list()
    [<lpod.list.odf_list object at 0x7f2f6ce2c5d0>, <lpod.list.odf_list ob...
    >>> body.get_table_list()
    [<lpod.element.odf_element object at 0x7f2f6ce2c850>, <lpod.element.od...
    >>> body.get_draw_page_list()
    [<lpod.element.odf_draw_page object at 0x7f23ba8e0c2f>, <lpod.element....


Each `get_xxx_list` method provides parameters for filtering the results. For
example headings can be listed by level, annotations by creator, etc. Almost
all of them accept filtering by style and content using a regular
expressions.

Some examples::

    >>> body.get_heading_list(level=1)
    [<lpod.heading.odf_heading object at 0x7f2f6ce2cb10>]
    >>> body.get_paragraph_list(regex=u"[Ll]ist")
    [<lpod.paragraph.odf_paragraph object at 0x7f2f6ce2c6d0>, <lpod.paragr...

A miss returns an empty list::

    >>> body.get_table_list(style=u"Invoice")
    []

Accessing a Single Element
==========================

To access a single element by name, position or a regular expression on the
content, use `get_xxx_by_<criteria>`, where criteria can be `position`,
`content`, or for some of them `name`, `id` `title`, `description`.

Some examples::

    >>> body.get_heading_by_position(1)
    <lpod.heading.odf_heading object at 0x7f2f6ce2cc50>
    >>> body.get_paragraph_by_content(u"highlight")
    <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2cd90>
    >>> body.get_table_by_name(u"Feuille1")
    <lpod.element.odf_element object at 0x7f2f6ce2c850>

A miss returns None::

    >>> print body.get_draw_page_by_name(u"Page1")
    None

Accessing Other Elements from an Element
========================================

Any element is a context for navigating but only on the subtree it contains.
Just like the body was, but since the body contains all content, we didn't
see the difference.

Let's get the first list of the document::

    >>> mylist = body.get_list_by_position(1)
    >>> print mylist
    <lpod.list.odf_list object at 0x7f2f6ce2c890> "text:list"

Notice that positions start at 0, just like in XPath (it calls an XPath query
actually). This may change in the future.

We can now access only the first paragraph contained in the list::
    >>> mypara = mylist.get_paragraph_by_position(1)
    >>> print mypara
    <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2ca10> "text:p"

The paragraph itself contains an link on `http://example.com`::

    >>> mylink = mypara.get_link_by_path(u"example.com")
    >>> print mylink
    <lpod.element.odf_element object at 0x7f2f6ce2cb10> "text:a"

Navigation Through Styles
=========================

Styles are a complex subject that deserves its own :doc:`cookbook
<cookbook-styles>`.

Introspecting Elements
======================

Should you be lost, remember elements are part of an XML tree::

  >>> mypara.get_children()
  >>> mypara.get_parent()

And so on.

And you can introspect any element as serialized XML::

    >>> mylink.serialize()
    <text:a xlink:href="http://example.com">Example</a>

See the :doc:`level 0 API <level0>` for details.
