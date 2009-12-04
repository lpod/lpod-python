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

####################
Spreadsheet Cookbook
####################

Creating Spreadsheet
====================

Let's first create a spreadsheet document::

  >>> from lpod.document import odf_new_document_from_type
  >>> document = odf_new_document_from_type('spreadsheet')

As for text documents, content goes into the body::

  >>> body = document.get_body()

Now a spreadsheet is simply a series of tables. Each sheet you see in a
desktop application is a table.

New spreadsheet documents don't contain any table.

About Tables
============

Understanding the table model is necessary to use it with no surprise.

The content unit is cell. Cells generally contain a value, a type and its
representation in a paragraph, e.g. the value "2009-12-04T11:21", the type
"date", and the representation "Dec. 4th 2009 11:21", or "4 déc. 2009 11h21",
depending on the language used.

As in HTML, cells are contained in rows. Rows can be repeated so the cells
appear on several lines. Rows are referring to a "table-row" style that
basically sets the row height in units, or to use optimal height.

Columns don't contain cells, they are referring to a style that basically
sets the column width in units, and the default cell style. Columns can be
repeated so the style information applies to several columns of cells.

Maintaining a table with equal width on each row and column can be
cumbersome.  The specification allows for tables with unequal rows, but the
result is not guaranteed. For safety purposes, always use the table to access
rows and cells.

Creating Tables
===============

The only mandatory argument for creating a table is a name::

  >>> from lpod.table import odf_create_table
  >>> table = odf_create_table(u"Empty Table")
  >>> body.append_element(table)

If you opened the document, you would see a first sheet named "Empty Table".

This table is empty and only waits for new rows.

Creating a table filled with rows and columns is also possible::

  >>> table = odf_create_table(u"5x5 Table", width=5, height=3)

Although this table visually looks empty too, you can already access elements
and fill it.

Table Information
=================

The width and height::

  >>> table.get_table_width()
  5
  >>> table.get_table_height()
  3

If you need the pair::

  >>> table.get_table_size()
  (5, 3)

Rows
====

Accessing List of Rows
----------------------

Rows are referenced by their number, starting from 0. When reporting a number
from a desktop application, remember to decrement it.

You can iterate through rows::

  >>> table.traverse_rows()
  <generator object traverse_rows at 0x7fc3f1c11320>

Or filter rows::

  >>> table.get_row_list(regex=u"3.14")
  [(0, <lpod.table.odf_row object at 0x7fc3f1c06b50>),
   (2, <lpod.table.odf_row object at 0x7fc3f1c06ed0>)]

Here rows 0 and 2 contain a cell with "3.14" in its content.

Accessing Single Row
--------------------

Accessing a single row is straightforward::

  >>> first_row = table.get_row(0)
  >>> last_row = table.get_row(-1)

The object is for you to manipulate::

  >>> first_row.get_row_width()
  5
  >>> first_row.set_row_style(u"Another style")

Writing Row
-----------

The changes only happen it memory. You need to commit them::

  >>> table.set_row(0, first_row)

Will replace the old version by the new one. But nothing prevents you from
copying the row elsewhere::

  >>> table.set_row(-1, first_row)

Will replace the last row of the table.

Accessing Row Values
--------------------

Want to introspect a row?::

  >>> first_row.get_cell_values()
  [u"A string", 4, Decimal('3.14'),
   datetime.datetime(2009, 12, 4, 14, 38, 39, 836098) , None]

This last cell contains neither value nor content.

The row can be rewritten at once::

  >>> first_row.set_cell_values(range(5))

As long as you commit it::

  >>> table.set_row(2, first_row)

Inserting Rows
--------------

Existing rows can be inserted, for example at the top::

  >>> table.insert_row(0, some_row)

Or new rows::

  >>> table.insert_row(2, odf_create_row(width=5))

LpOD will prevent you from inserting a row of different width::

  >>> table.insert_row(0, odf_create_row())
  Traceback (most recent call last):
  ...
  ValueError: row mismatch: 5 cells expected

Appending Rows
--------------

Appending a row at the end of the table is simple::

  >>> table.append_row(some_row)

Deleting Rows
-------------

To delete a row of the table, its number is required::

  >>> table.delete_row(0)

Cells From Rows
===============

Accessing List of Cells
-----------------------

The row can iterate through its cells::

  >>> first_row.traverse_cells()
  <generator object traverse_cells at 0x7fc3f1c11320>

Or filter them::

  >>> first_row.get_cell_list(regex=u"3.14")
  [(3, <lpod.table.odf_cell object at 0x7fc3f1c257d0>),
   (4, <lpod.table.odf_cell object at 0x7fc3f1c25590>)]

Here the last two cells contain "3.14" in their content.

Accessing Single Cell
---------------------

Accessing a single cell is similar to a row::

  >>> first_cell = first_row.get_cell(0)

If you have difficulties translating the alphabetical numeration from desktop
applications to numbers, just use it::

  >>> far_cell = row.get_cell('ABC')

Would get the 731th cell of a big table.

Cells From Table
================

Cells can be accessed from the table too. The only difference is that you
need to provide, or you are provided the row number along with the cell
number.

So accessing the first cell is a matter of::

  >>> first_cell = table.get_cell((0, 0))

Or with the desktop application notation::

  >>> first_cell = table.get_cell('A1')

The easier for the last cell is the numeric numbering::

  >>> last_cell = table.get_cell((-1, -1))

Cells can be filtered as well::

  >>> table.get_cell_list(regex=u"3.14")
  [(0, 0, <lpod.table.odf_cell object at 0x7fc3f19c8850>),
   (2, 0, <lpod.table.odf_cell object at 0x7fc3f19c88d0>),
   (1, 1, <lpod.table.odf_cell object at 0x7fc3f19c89d0>),
   (3, 1, <lpod.table.odf_cell object at 0x7fc3f19c8a50>),
   (4, 2, <lpod.table.odf_cell object at 0x7fc3f19c8bd0>)]

Cells
=====

Now we have cells, let's see how to manipulate them.

A cell is more complicated than just a value. It may contain one or several
paragraphs, and the value itself requires specific serialization.

LpOD provides helpers for the most common cases.

Getting Value
-------------

  >>> first_cell.get_cell_value()
  dec('3.14')
  >>> first_cell.get_cell_type()
  'float'

Setting Value
-------------

But a cell that contains text is different::

  >>> first_cell.set_cell_value(u"A Text")
  >>> first_cell.get_cell_type()
  'string'

Setting Monetary Value
----------------------

And monetary cells are a bit more complicated::

  >>> first_cell.set_cell_value(15.24, representation=u"15.24 €",
          currency='EUR')
  >>> first_cell.get_cell_type()
  'float'
  >>> first_cell.get_cell_currency()
  'EUR'

Setting Cell Style
------------------

Assuming the following cell style is available::

  >>> first_cell.set_cell_style(u"With_20_borders")

Committing
----------

Commit the changes in the row::

  >>> first_row.set_cell(0, first_cell)
  >>> table.set_row(first_row)

Or in the table directly::

  >>> table.set_cell('A1', first_cell)

Or anywhere you want to replace an existing cell.

Columns
=======

Accessing List of Columns
-------------------------

Columns can be traversed as well::

  >>> table.traverse_columns()
  <generator object traverse_columns at 0x7fc3f19c57d0>

Or filtered::

  >>> table.get_column_list(style="Red_20_background")
  [(0, <lpod.table.odf_column object at 0x7fc3f1c06c90>),
  (4, <lpod.table.odf_column object at 0x7fc3f1c25b50>)]
 
Accessing Single Column
-----------------------

The method is now familiar::

  >>> first_column = table.get_column(0):

Inserting Column
----------------

Guess how to insert a column::

  >>> table.insert_column(3, odf_create_column())

But lpOD also expanded rows to match the new table width.

Appending Column
----------------

To extend the table on the right::

  >>> table.append_column(odf_create_column())

And lpOD expanded the rows as well.

Deleting Column
---------------

To remove the whole column along with cells at the same abscissa::

  >>> table.delete_column(2)

Accessing Column Values
-----------------------

Although the columns don't contain cells, lpOD offers an API to read all the
cells at this position::

  >>> column.get_column_cell_values()
  [2009, 2010, 2011]

and replace them::

  >>> column.set_column_cell_values([2010, 2011, 2012])

Importing from CSV
==================

To transform a series of CSV files into tables::

   >>> for filename in glob('files/*.csv'):
   >>>     table = import_from_csv(filename, unicode(filename, 'utf8'))
   >>>     body.append_element(table)

You can give either a file name or a file-like object. The former will be
opened and closed, but the latter will be left opened.

Exporting to CSV
================

Every table can be serialized to CSV::

  >>> f = open('/tmp/out.csv', 'w')
  >>> table.export_to_csv(f)

Inserting Image
===============

First add an image in the document::

  >>> image_uri = document.add_file('logo.png')

Images are in frame::

  >>> frame = odf_create_image_frame(image_uri, size=('1.87cm', '1.75cm'),
          position=('0cm', '0cm'))

Displaying an image in a cell is tricky: the document type must be given or
the table attached to the document.

That's why the API is available on the table level only::

    table.set_cell_image((-1, 0), frame, type=document.get_type())

Hint: Table Bigger Than Its Content
===================================

It happens that some tables produced by desktop applications contain an
excessive repetition of empty cells::

  >>> table.get_table_size()
  (5, 65536)

To remove empty columns on the right and empty rows below::

  >>> table.rstrip_table()
  >>> table.get_table_size()
  (5, 9)

Cells with style information are not considered empty.

Better do it as the first operation to save memory.

Saving Document
===============

Because we didn't do all of that for nothing::

   >>> document.save('spreadsheet.ods')
