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

######################
Level 0 API reference
######################

0.0 Physical access & persistence
=================================

This level provides the odf_container class only; this class encapsulates
the required logic for read & write operations regarding the ODF documents
and associated resources across a virtual file system.

.. figure:: figures/lpod_level0.*
   :align: center


class: odf_container
--------------------

The odf_container represents the physical Open Document package, whatever
the storage option. The package consists of either a zip compressed archive
including XML and non-XML parts, of a flat, uncompressed XML file.

An odf_container instance can be created by several ways:

1) from scratch by the lpOD API;

2) from a previously stored ODF template package;

3) from an existing ODF package.


Constructors
~~~~~~~~~~~~

odf_get_container(uri)
  Instantiates an odf_container object which is a read-write interface to
  an existing ODF package corresponding to the given URI. The package may
  be an ODF-compliant zip or an ODF-compliant flat XML file.

odf_new_container_from_class({document_class})
  Returns a new odf_container corresponding to the given ODF document class
  (i.e. presently text, spreadsheet, presentation, or drawing).

odf_new_container_from_template(uri)
  Returns a new odf_container instantiated from an existing ODF template
  package. Same as odf_get_container(), but the template package is read-only.

Methods
~~~~~~~

clone()
  Returns a new odf_container that is a copy of the current instance.

del_part(part_name)
  Deletes a part in the container. The target part is selected
  according to the same rules as with get_part().

  This part deletion applies to the odf_container object but not
  immediately to the physical underlying package. It's made
  persistent by the next save() call, like any other change
  regarding an odf_container.

get_part(part_name)
  Extracts and returns a part, i.e. either a member file of the package,
  if the physical container is a regular ODF zip archive, or a subset of
  the XML content, if the package is a flat XML file. The extracted part
  is returned as raw data; it's not parsed or interpreted in any way.

  The part to be extracted depends on the given part_name and is selected
  according to the following rules:

  If part_name is "content", "styles", "meta" or "settings", then the
  selected part is the "part_name.xml" member file in case of zip archive
  or the "office:document-part_name" in case of flat XML file.

  For any other part, the given part_name must be either the explicit
  path/name of the needed resource in the zip package, or the full name
  of the needed element in the XML flat file. With flat XML packages,
  it's assumed that the root element is always <office:document> and
  the selected part_name is always a direct child of the root element.

  The return value is null if the given part_name doesn't match an
  existing part.

save()
  Commits every change previously done through other odf_container
  methods and makes them persistent in the underlying physical
  container. Without argument, the changes are committed in the
  source container (i.e. the physical file used to create the
  odf_container instance using get_container()). Without argument,
  this method fails if the current odf_container has been created
  using odf_new_container() or odf_new_container_from_template().

save(packaging)
  Like save(), but with a specified packaging format, which possibly
  differs from the packaging format of the source document. Allowed
  package types are "zip" and "flat".

save(uri)
  Like save(), but with an explicit target which is not the source
  container. The source container remains unchanged. Behaves just like
  the "save as..." feature of a typical desktop application.

save(uri, packaging)
  Like save(), but with an explicit target which is not the source
  container and a specified packaging format, which possibly
  differs from the packaging format of the source document. Allowed
  package types are "zip" and "flat".

set_part(part_name, data)
  Creates or replaces a part in the current odf_container using external
  raw data.

  The target part_name is selected according to the same rules as with
  get_part().

  As with del_part(), the change applies to the odf_container object in
  memory but it doesn't affect the corresponding persistent package
  before the next call of the save() method.

  The provided data is used "as is", without any package consistency
  check. If the current odf_container is a flat XML package, the user
  is responsible of the XML well-formedness and ODF compliance of this
  material.

save(uri, packaging)
    Saves the container to the optionally given URI (or by default the same
    URI it was loaded from). The container is saved in the same packaging
    format than when it was open, unless it is given "flat" or "zip".

0.1 Basic XML access
====================

A physical ODF *container*, accessed through an odf_container object, can
contain one or more XML or non-XML *parts*. Non-XML parts included in ODF
packages can be referred to as external resources from within XML parts
(multimedia content), but they are out of the scope of the lpOD level 0
API. On the other hand, this API provides  in any XML part.

The XML oriented aspect of the level 0 API is provided through the
odf_xmlpart and odf_element classes.

class: odf_xmlpart
------------------

This class represents an individual XML member of any ODF package, whatever
its functional role and the global document class (text, spreadsheet,
presentation, drawing, etc). It provides all the basic logic needed to
retrieve, update, delete or create any XML element. The element retrieval
is implemented through an encapsulated XPath engine.

The external behaviour of an odf_xmlpart object is the same whatever the ODF
container from which its content is extracted, knowing that the ODF
specification allows two packaging types. As a consequence, an instance of
odf_xmlpart could be created either from an XML member file of an ODF
compressed archive, or from a particular element in a flat XML ODF file.

An odf_xmlpart is always created using a keyword indicating its functional
role in the whole document. Typical ODF roles are content, styles, meta and
settings. The real name of the part depends on the packaging type of the
container. With a regular ODF zip package, a given "part_name" is stored
as a "part_name.xml" member file, but with a flat XML package it's stored as
a "office:document-part_name" XML element. The lpOD API is able to hide the
difference; the application has just to know the functional name of the
part.

Constructor
~~~~~~~~~~~

odf_xmlpart(part_name, container)
  Instantiates an odf_xmlpart object from the XML content of a given
  part in a previously created odf_container object. The given part_name
  must correspond to an existing ODF XML part name. The given name is
  just the functional name of the part, not the real storage name which
  depends on the packaging type of the container. The return value is
  an odf_xmlpart instance, or null if case of failure for any reason.

General I/O Methods
~~~~~~~~~~~~~~~~~~~

container()
  Returns the odf_container object from which the current instance has
  been extracted.

events()
  **TBD**


odf_xmlpart
-----------

The odf_xmlpart object represents one of the XML components of an ODF document,
i.e. content, styles, meta, settings.

Constructors
~~~~~~~~~~~~

odf_xmlpart(part_name, container)
    Extracts the part from the container and load it as an XML part.

The main interface allows the application to retrieve odf_element lists or
individual instances according to given XPath expressions.

Methods
~~~~~~~

get_element_list(xpath_expr)
  Returns the list of odf_element matching the given XPath expression in the
  whole part. An empty list is returned if no element matches.

get_element(xpath_expr)
  Returns the first odf_element matching the given XPath expression in the
  whole part. Null is returned if no element matches.

serialize(pretty)
  Returns the part as an XML document string. If pretty is true, the XML is
  pretty printed.

delete(child)
    Deletes a child odf_element from the part.

odf_element
-----------

From the odf_xmlpart, you extract odf_element objects. They are an abstraction
of the XML library used behind so they offer a basic XML API.

The main interface is sending XPath queries to get odf_element's.

Constructors
~~~~~~~~~~~~~

odf_create_element(data)
    Creates an odf_element from a fragment of XML data. XML prefixes common to
    ODF are allowed.

Methods
~~~~~~~

get_name()
    Get the tag name with its prefix.

get_element_list(xpath_query)
    Get a list of odf_element children matching the given query. An empty list
    is returned if no element matches.

get_element(xpath_query)
    Returns the first odf_element child matching the given XPath query in the
    whole part. Null is returned if no element matches.

get_attributes()
    Returns the mapping (dictionary) of attributes carried by the element.
    An empty mapping is returned if the element has no attribute.

get_attribute(name)
    Returns the string value of the attribute having this name. The name must
    be prefixed.

set_attribute(name, value)
    Creates the attribute or updates its string value. The name must be
    prefixed.

del_attribute(name)
    Deletes the attribute having this name. The name must be prefixed.

get_text()
    Returns the text contents of the element in the most appropriate type for
    text, e.g. unicode. It is not recursive. Null is returned if the element
    contains no text.

set_text(text, after)
    Sets the text content of the element. The text is typed in the most
    appropriate type for text, e.g. unicode. If after is true, the text is set
    after the closing tag (useful for inserting an element in the middle of
    text content).

get_creator()
    Shortcut to get the creator value of odf_element's containing a
    "dc:creator" element. Null is returned if no creator is set.

get_date()
    Shortcut to get the date value of odf_element's containing a
    "dc:date" element. Null is returned if no creator is set.

get_text_content()
    Shortcut to get the text of paragraphs inside the element. An empty string
    is returned by default.

set_text_content(text)
    Shortcut to set text content inside a paragraph inside the element. The
    text is typed in the most appropriate type for text, e.g. unicode. Any
    previous child element is deleted.

insert_element(element, {FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING})
    Insert the given odf_element at the given position.
    FIRST_CHILD: the odf_element will be the first child.
    LAST_CHILD: the odf_element will be the last child.
    NEXT_SIBLING: the odf_element will be inserted just after.
    PREV_SIBLING: the odf_element will be inserted just before.

clear()
    Removes all children and text from the element.

copy()
    Returns another instance of the element with the same properties.

serialize()
    Returned an XML fragment string of the element.

delete(child)
    Removes the odf_element child.
