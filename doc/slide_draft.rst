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

############################
Slides Draft for 2009-09-30
############################

Basic text containers
=====================

- Paragraphs and Headings
  ::

     heading = odf_create_heading('Heading', 1, u'Chapter')
     body.insert_element(heading, LAST_CHILD)

     text = u'The current chapter is: '

     paragraph = odf_create_paragraph('Standard', text)
     body.insert_element(paragraph, LAST_CHILD)

- Text spans

  - xxx
  - xxx

Text marks and indices
======================

- Bookmarks

  bla bla bla bla bla bla

- Links
- Tables of content
- Indices
- Annotations
- Change tracking

Structured containers
=====================

- Tables
- Lists
- Data pilot (pivot) tables
- Sections
- Draw pages

Fields and forms
================

- Declared fields and variables
- Text fields

Graphic content
===============

- Frames
- Shapes
- Images
- Animations
- Charts

Styles
======

- Text styles
- Graphic styles
- Page styles
- Data formatting styles

Metadata
========

- Pre-defined
- User defined

Application settings
====================


