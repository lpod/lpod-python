Notes
#####


Level 0
=======

Level 0.0
---------
::

    odf_container container

    container = odf_new_container_from_class({text, spreadsheet, presentation,
                                              drawing})
    container = odf_new_container_from_template(template_uri)
                    
    container = odf_get_container(uri)

    odf_container copy = container.clone()
    str data = container.get_part(part_name)
    container.set_part(part_name, data)
    container.del_part(part_name)


TODO
^^^^

::

    container.save()
    container.save(packaging)
    container.save(uri)
    container.save(uri, packaging)

with ``packaging = {flat, zip}``


Level 0.1
---------
::

    odf_xmlpart part

    part = odf_xmlpart(part_name, container)

    part.events
    part.container
    part.serialize()

    list l_elt = part.get_element_list("//xpath...")

    odf_element elt = l_elt[0]

    elt.get_element_list("//xpath...")

    value = elt.get_attribute(name)
    elt.set_attribute(name, value)

    unicode text = elt.get_text()
    elt.set_text(text)

    odf_element e2 = odf_create_element('<element[...]')
    elt.insert_element(e2, {previous_sibling, next_sibling, first_child,
                            last_child, <N>})
    e3 = elt.copy()

    elt.delete()


Level 1
=======
::

    odf_document document

    document = odf_get_document(uri)
    document = odf_new_document_from_class(odf_class)
    document = odf_new_document_from_template(template_uri)

    document.get_paragraph_list()
    document.get_paragraph_list(style)
    document.get_paragraph_list(context)
    document.get_paragraph_list(style, context)

      => '//text:p[@text:style-name="$style"]'

    document.get_heading_list()
    document.get_heading_list(style)
    document.get_heading_list(level)
    document.get_heading_list(context)
    document.get_heading_list(style, level)
    document.get_heading_list(style, level, context)

      => assert level >= 1
      => '//text:h[@text:style-name="%s"]' % style
      => '//text:h[@text:level="%s"]' % level

    document.get_paragraph(position)
    document.get_paragraph(position, context)

      => assert position >= 1
      => '//text:p[%s]' % position

    document.get_heading(position)
    document.get_heading(position, level)
    document.get_heading(position, context)
    document.get_heading(position, level, context)

      => assert position >= 1
      => assert level >= 1
      => '//text:h[@text:level="%s"][%s]' % (level, position)

    document.get_style(name)

      => only paragraph styles for now (family=paragraph)
      => search algorithm:
        - same part, automatic styles
        - same part, named styles
        - styles part, named styles
        - default style of the same family

    odf_element elt = odf_create_paragraph(style)

      => '<text:p text:style-name="$style"></text:p>'

    odf_element elt = odf_create_paragraph(style, text)

      => '<text:p text:style-name="$style">$text</text:p>'

    odf_element elt = odf_create_heading(style, level)

      => '<text:h text:style-name="$style" text:level="$level"></text:h>'

    odf_element elt = odf_create_heading(style, level, text)

      => '<text:h text:style-name="$style" text:level="$level">$text</text:h>'

    document.insert_paragraph(element)
    document.insert_paragraph(element, context)

    document.insert_heading(element)
    document.insert_heading(element, context)

Hint: preload the body, etc. for fast access to default contexts.


Styles
-------

- style type: font face, default style...
- style family: font family, text, paragraph, graphics, number...
- style parent (inheritance)
- [style class: ... ?]


TODO
====

list items, tables, table cells...

named styles, automatic styles
style families:

manifest?


XPath Requirements
==================

::

    //text:p
    //text:p[4]
    //text:section[4]/text:p[5]
    //text:p[@text:style-name="Note"]
    //draw:frame[@draw:name="image1"]/draw:image
    //text:p[@text:style-name="Note"][4]
