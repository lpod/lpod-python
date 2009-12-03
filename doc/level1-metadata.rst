.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: David Versmisse <david.versmisse@itaapy.com>
            Hervé Cauwelier <herve@itaapy.com>
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


Metadata
========

.. contents::
   :local:

lpOD presently supports global metadata, i.e. metadata that describe a whole
document. Some of them are defined in the ODF specification, others may be defined by the applications. 

Access to the metadata
----------------------

Prior to any access to the metadata, the application have to instantiate an ``odf_meta`` object through the ``get_meta()`` method of an existing ``odf_document``::

  meta = document.get_meta()

All the methods related to global metadata belong to the ``odf_meta`` object.

Single-item pre-defined metadata
--------------------------------

For each pre-defined elementary piece of metadata, lpOD provides both a read accessor and a write accessor, whose name are respectively ``get_xxx()`` and ``set_xxx()``, where `xxx` is the mnemonic name of the target. For example, the title of the document may be got, then changed, through the following sequence::

  meta = document.get_meta()
  old_title = meta.get_title()
  meta.set_title("The new title")

The ``get_xxx()`` and ``set_xxx()`` accessors are available for the following elements:

- ``creation_date``: the date of the initial version of the document;
- ``creator``: the name of the user who created the current version of the document;
- ``description``: the long description (or subtitle);
- ``editing_cycles``: the number of edit sessions (may be regarded as a version number);
- ``editing_duration``: the total editing time through interactive software, expressed as
  a time delta;
- ``generator``: the signature of the application that created the document;
- ``initial_creator``: the name of the user who created the first version of the document;
- ``language``: the ISO code of the main language used in the document;
- ``modification_date``: the date of the last modification (i.e. ot the current version);
- ``subject``: the subject of the document;
- ``title``: the title of the document.

Complex pre-defined metadata
----------------------------

Some methods pre-defined pieces of metadata contain multiple items, so they can't be get or set through the simple accessors described above.

Knowing that a document may be "tagged" by one or more keywords, ``odf_meta`` provides a ``get_keywords()`` method that returns the list of the current keywords as a comma-separated string. Conversely, ``set_keywords()`` allows the user to set a full list of keywords, provided as a single comma-separated string; the provided list replaces any previously existing keyword; this method, used without argument or with an empty string, just removes all the keywords.

``set_keyword()`` appends a new, given keyword to the list; it's neutral if the given keyword is already present.

``check_keyword()`` returns ``true`` if its argument (which may be a regular expression) matches an existing keyword, or ``false`` if the keyword is not present.

``remove_keyword()`` deletes any keyword that matches the argument (which may be a regular expression).

Document statistic metadata may be get or set using ``get_statistics()`` or ``set_statistics()``. The first one returns a hash table whose keys are ODF attribute names of statistic data, as defined in §3.1.18 of the ODF 1.1 specification (for example, ``meta:page-count``, ``meta-character-count``, and so on). The second one must be provided with a similar data structure. The application is responsible for the accuracy of the values provides through ``set_statistics()``; there is no consistency check in the lpOD API between these values and the statistical data of the real document content.

User defined metadata [todo]
----------------------------

