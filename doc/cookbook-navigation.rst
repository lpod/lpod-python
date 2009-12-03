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

- Open an existing document::

    >>> from lpod.document import odf_get_document
    >>> document = odf_get_document('http://example.com/odf/cookbook')

- Access the content of the document::

    >>> body = document.get_body()

- A list of all elements of a kind is accessible through "get_*_list"::

    >>> body.get_heading_list()
    [<lpod.heading.odf_heading object at 0x22a0090>, <lpod.heading.odf_head...
    >>> body.get_paragraph_list()
    [<lpod.paragraph.odf_paragraph object at 0x22a04d0>, <lpod.paragraph.od...
    >>> body.get_list_list()
    [<lpod.list.odf_list object at 0x7f2f6ce2c5d0>, <lpod.list.odf_list obj...
    >>> body.get_table_list()
    [<lpod.element.odf_element object at 0x7f2f6ce2c850>, <lpod.element.odf...
    >>> body.get_draw_page_list()
    [<lpod.element.odf_draw_page object at 0x7f23ba8e0c2f>, <lpod.element.od...

- The list can be more finely grained::

    >>> body.get_heading_list(level=1)
    [<lpod.heading.odf_heading object at 0x7f2f6ce2cb10>]
    >>> body.get_paragraph_list(regex=u"[Ll]ist")
    [<lpod.paragraph.odf_paragraph object at 0x7f2f6ce2c6d0>, <lpod.paragrap...

- No result returns an empty list::

    >>> body.get_table_list(style=u"Invoice")
    []

- To access a single element by name, position or a regular expression on the
  content, use "get_*_by_<criteria>"::

    >>> body.get_heading_by_position(1)
    <lpod.heading.odf_heading object at 0x7f2f6ce2cc50>
    >>> body.get_paragraph_by_content(u"highlight")
    <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2cd90>
    >>> body.get_table_by_name(u"Feuille1")
    <lpod.element.odf_element object at 0x7f2f6ce2c850>

- No result returns None::

    >>> print body.get_draw_page_by_name(u"Page1")
    None

- Any element is a context for navigating inside it::

    >>> l = body.get_list_by_position(1)
    >>> print l
    <lpod.list.odf_list object at 0x7f2f6ce2c890> "text:list"
    >>> p = l.get_paragraph_by_position(1)
    >>> print p
    <lpod.paragraph.odf_paragraph object at 0x7f2f6ce2ca10> "text:p"
    >>> a = p.get_link_by_path(u"example.com")
    >>> print a
    <lpod.element.odf_element object at 0x7f2f6ce2cb10> "text:a"
    >>> a.serialize()
    <text:a xlink:href="http://example.com">Example</a>
