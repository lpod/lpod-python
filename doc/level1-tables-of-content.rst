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


Tables of contents
==================

.. contents::
   :local:

A table of contents (TOC) is represented by an ``odf_toc`` object, which is
created using the ``odf_create_toc()`` constructor.

TOC constructor parameters
--------------------------

- ``name``: the internal name of the TOC (default="Table of contents");
- ``title``: an optional title (to be displayed at the TOC head);
- ``style``: the name of a section style applying to the TOC;
- ``protected``: a boolean flag that tells the editing applications if the
  section is write-protected (default=``true``);
- ``outline level``: specifies the last outline level to be used used when
  generating the TOC from headings; if this parameter is omitted, all the
  outline levels are used by default.
- ``use outline``: a boolean flag that specifies if the TOC must be generated
  from headings (default=``true``), knowing that, if ``false``, the TOC is
  generated from TOC marks.

TOC methods
-----------

The ``odf_toc`` elements provide the following methods:

- ``get_title()`` and ``set_title()`` to get or change the display TOC title;
- ``get_outline_level()`` and ``set_outline_level()`` to get or change the
  current outline level property;
- ``get_formatted_text()``: returns the plain text content of the TOC, with some
  formatting features;
- ``fill``: builds the body of the TOC (beware, this method is far less rich
  the TOC generation feature of a typical interactive text processor).

