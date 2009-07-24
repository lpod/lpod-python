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


