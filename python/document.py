# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from datetime import datetime

# Import from lpod
from container import ODF_PARTS, odf_get_container
from container import odf_new_container_from_template
from container import odf_new_container_from_class, odf_container
from content import odf_content
from meta import odf_meta
from styles import odf_styles
from utils import _check_arguments, Date, DateTime, _set_value_and_type
from xmlpart import odf_xmlpart, LAST_CHILD
from xmlpart import odf_create_element, odf_element


#
# odf creation functions
#

def odf_create_section(style):
    """Create a section element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    _check_arguments(style=style)
    data = '<text:section text:style-name="%s"></text:section>' % style
    return odf_create_element(data)



def odf_create_paragraph(style, text=u''):
    """Create a paragraph element of the given style containing the optional
    given text.
    Arguments:

        style -- str
        text -- unicode

    Return: odf_element
    """
    _check_arguments(style=style, text=text)
    data = '<text:p text:style-name="%s">%s</text:p>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, text))



def odf_create_span(style, text=u''):
    """Create a span element of the given style containing the optional
    given text.
    Arguments:

        style -- str
        text -- unicode

    Return: odf_element
    """
    _check_arguments(style=style, text=text)
    data = '<text:span text:style-name="%s">%s</text:span>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, text))



def odf_create_heading(style, level, text=u''):
    """Create a heading element of the given style and level, containing the
    optional given text.
    Arguments:

        style -- str
        level -- int
        text -- unicode

    Return: odf_element

    Level count begins at 1.
    """
    _check_arguments(style=style, level=level, text=text)
    data = '<text:h text:style-name="%s" text:outline-level="%d">%s</text:h>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, level, text))



def odf_create_frame(name, style, width, height, page=None, x=None, y=None):
    """Create a frame element of the given style, width and height,
    optionally positionned at the given x and y coordinates, in the given
    page.
    Arguments:

        style -- str
        width -- str
        height -- str
        page -- int
        x -- str
        y -- str

    Return: odf_element

    Width, height, x and y are strings including the units, e.g. "10cm".
    """
    if page is None:
        anchor = 'text:anchor-type="paragraph"'
    else:
        anchor = 'text:anchor-type="page" text:anchor-page-number="%d"' % page
        if x is not None:
            anchor += ' svg:x="%s"' % x
        if y is not None:
            anchor += ' svg:y="%s"' % y
    data = ('<draw:frame draw:name="%s" draw:style-name="%s" '
            'svg:width="%s" svg:height="%s" %s/>')

    return odf_create_element(data % (name, style, width, height, anchor))



def odf_create_image(uri):
    """Create an image element showing the image at the given URI.
    Arguments:

        uri -- str

    Return: odf_element
    """
    return odf_create_element('<draw:image xlink:href="%s"/>' % uri)



def odf_create_cell(value=None, representation=None, cell_type=None,
                    currency=None):
    """Create a cell element containing the given value. The textual
    representation is automatically formatted but can be provided. Cell type
    can be deduced as well, unless the number is a percentage or currency. If
    cell type is "currency", the currency must be given.
    Arguments:

        value -- bool, int, float, Decimal, date, datetime, str, unicode,
                 timedelta
        representation -- unicode
        cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'
        currency -- three-letter str

    Return: odf_element
    """

    cell = odf_create_element('<table:table-cell/>')

    representation = _set_value_and_type(cell, value=value,
                                         representation=representation,
                                         value_type=cell_type,
                                         currency=currency)

    if representation is not None:
        cell.set_text_content(representation)

    return cell



def odf_create_row(width=None):
    """Create a row element, optionally filled with "width" number of cells.
    Arguments:

        width -- int

    Return: odf_element
    """
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell(u"")
            row.insert_element(cell, LAST_CHILD)
    return row



def odf_create_column(style):
    """Create a column element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    data = '<table:table-column table:style-name="%s"/>'
    return odf_create_element(data % style)



def odf_create_table(name, style, width=None, height=None):
    """Create a table element of the given style, with "width" columns and
    "height" rows.
    Arguments:

        style -- str
        width -- int
        height -- int

    Return: odf_element
    """
    data = '<table:table table:name="%s" table:style-name="%s"/>'
    table = odf_create_element(data % (name, style))
    if width is not None or height is not None:
        width = width if width is not None else 1
        height = height if height is not None else 1
        for i in xrange(height):
            row = odf_create_row(width)
            table.insert_element(row, LAST_CHILD)
    return table



def odf_create_list_item(text=None):
    """Create a list item element.
    Arguments:

        text -- unicode

    Return: odf_element

    The "text" argument is just a shortcut for the most common case. To create
    a list item with several paragraphs or anything else (except tables),
    first create an empty list item, insert it in the document, and insert
    your element using the list item as the context.
    """
    element = odf_create_element('<text:list-item/>')
    if text is not None:
        _check_arguments(text=text)
        element.set_text_content(text)
    return element



def odf_create_list(style):
    """Create a list element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    return odf_create_element('<text:list text:style-name="%s"/>' % style)



def odf_create_style(name, family):
    """Create a style element with the given name, related to the given
    family.
    Arguments:

        name -- str
        family -- 'paragraph', 'text', 'section', 'table', 'tablecolumn',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control' or 'ruby'
    Return: odf_element
    """
    _check_arguments(family=family)
    data = '<style:style style:name="%s" style:family="%s"/>'
    return odf_create_element(data % (name, family))



def odf_create_style_text_properties():
    """Create a text properties element.
    Return: odf_element
    """
    # TODO should take parameters
    return odf_create_element('<style:text-properties/>')



def odf_create_note(text, note_class='footnote', id=None, body=None):
    """Create either a footnote or a endnote element with the given text,
    optionally referencing it using the given id.
    Arguments:

        text -- unicode
        note_class -- 'footnote' or 'endnote'
        id -- str
        body -- an odf_element or an unicode object

    Return: odf_element
    """
    _check_arguments(text=text, note_class=note_class)
    data = ('<text:note text:note-class="%s">'
              '<text:note-citation>%s</text:note-citation>'
              '<text:note-body/>'
            '</text:note>')
    text = text.encode('utf_8')
    note = odf_create_element(data % (note_class, text))

    if id is not None:
        note.set_attribute('text:id', id)

    if body is not None:
        note_body = note.get_element('text:note-body')

        # Autocreate a paragraph if body = unicode
        if isinstance(body, unicode):
            note_body.set_text_content(body)
        elif isinstance(body, odf_element):
            note_body.insert_element(body, LAST_CHILD)
        else:
            raise ValueError, 'unexpected type for body: "%s"' % type(body)

    return note



def odf_create_annotation(creator, text, date=None):
    """Create an annotation element credited to the given creator with the
    given text, optionally dated (current date by default).
    Arguments:

        creator -- unicode
        text -- unicode
        date -- datetime

    Return: odf_element
    """
    # TODO allow paragraph and text styles
    _check_arguments(creator=creator, text=text, date=date)
    data = ('<office:annotation>'
               '<dc:creator>%s</dc:creator>'
               '<dc:date>%s</dc:date>'
               '<text:p>%s</text:p>'
            '</office:annotation>')
    creator = creator.encode('utf_8')
    if date is None:
        date = datetime.now()
    date = DateTime.encode(date)
    text = text.encode('utf_8')
    return odf_create_element(data % (creator, date, text))



def odf_create_variable_decls():
    return odf_create_element('<text:variable-decls />')



def odf_create_variable_decl(name, value_type):
    data = '<text:variable-decl office:value-type="%s" text:name="%s"/>'
    return odf_create_element(data % (value_type, name))



def odf_create_variable_set(name, value, value_type=None, display=False,
                            representation=None, style=None):

    data = '<text:variable-set text:name="%s" />'
    variable_set = odf_create_element(data % name)

    representation = _set_value_and_type(variable_set, value=value,
                                         value_type=value_type,
                                         representation=representation)

    if not display:
        variable_set.set_attribute('text:display', 'none')
    else:
        variable_set.set_text(representation)

    if style is not None:
        variable_set.set_attribute('style:data-style-name', style)

    return variable_set



def odf_create_variable_get(name, value, value_type=None, representation=None,
                            style=None):

    data = '<text:variable-get text:name="%s" />'
    variable_get = odf_create_element(data % name)

    representation = _set_value_and_type(variable_get, value=value,
                                         value_type=value_type,
                                         representation=representation)

    variable_get.set_text(representation)

    if style is not None:
        variable_get.set_attribute('style:data-style-name', style)

    return variable_get



def odf_create_user_field_decls():
    return odf_create_element('<text:user-field-decls />')



def odf_create_user_field_decl(name, value, value_type=None):

    data = '<text:user-field-decl text:name="%s"/>'
    user_field_set = odf_create_element(data % name)

    _set_value_and_type(user_field_set, value=value, value_type=value_type)

    return user_field_set



def odf_create_user_field_get(name, value, value_type=None,
                              representation=None, style=None):

    data = '<text:user-field-get text:name="%s" />'
    user_field_get = odf_create_element(data % name)

    representation = _set_value_and_type(user_field_get, value=value,
                                         value_type=value_type,
                                         representation=representation)

    user_field_get.set_text(representation)

    if style is not None:
        user_field_get.set_attribute('style:data-style-name', style)

    return user_field_get



def odf_create_page_number(select_page=None, page_adjust=None):
    """page_adjust is an integer to add (or subtract) to the page number

    select_page -- string in ('previous', 'current', 'next')
    page_adjust -- int
    """

    page_number = odf_create_element('<text:page-number/>')

    if select_page is None:
        select_page = 'current'
    page_number.set_attribute('text:select-page', select_page)

    if page_adjust is not None:
        page_number.set_attribute('text:page-adjust', str(page_adjust))

    return page_number



def odf_create_page_count():
    return odf_create_element('<text:page-count />')



def odf_create_date(date, fixed=False, data_style=None, representation=None):
    data = '<text:date text:date-value="%s"/>'
    date_elt = odf_create_element(data % DateTime.encode(date))

    if fixed:
        date_elt.set_attribute('text:fixed', 'true')

    if data_style is not None:
        date_elt.set_attribute('style:data-style-name', data_style)

    if representation is None:
        representation = Date.encode(date)
    date_elt.set_text(representation)

    return date_elt


#
# The odf_document object
#

class odf_document(object):
    """An abstraction of the Open Document file.
    """
    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

        # Cache of XML parts
        self.__xmlparts = {}


    #
    # Public API
    #

    def get_xmlpart(self, part_name):
        if part_name not in ODF_PARTS:
            raise ValueError, '"%s" is not an XML part' % part_name
        parts = self.__xmlparts
        part = parts.get(part_name)
        if part is None:
            container = self.container
            if part_name == 'content':
                part = odf_content(part_name, container)
            elif part_name == 'meta':
                part = odf_meta(part_name, container)
            elif part_name == 'styles':
                part = odf_styles(part_name, container)
            else:
                part = odf_xmlpart(part_name, container)
            parts[part_name] = part
        return part


    def clone(self):
        """Return an exact copy of the document.
        Return: odf_document
        """
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name == '_odf_document__xmlparts':
                xmlparts = {}
                for key, value in self.__xmlparts.iteritems():
                    xmlparts[key] = value.clone()
                setattr(clone, name, xmlparts)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, uri=None, packaging=None, pretty=False):
        """Save the document, at the same place it was opened or at the given
        URI. It can be saved as a Zip file or as a plain XML file. The XML
        can be pretty printed.
        Arguments:

            uri -- str
            packaging -- 'zip' or 'flat'
            pretty -- bool
        """
        # Synchronize data with container
        for part_name, part in self.__xmlparts.items():
            if part is not None:
                self.container.set_part(part_name, part.serialize(pretty))

        # Save the container
        self.container.save(uri, packaging)


    #
    # Styles over several parts
    #

    def get_style_list(self, family=None, category=None):
        _check_arguments(family=family)
        attributes = {}
        if family is not None:
            attributes['style:family'] = family
        styles = self.get_xmlpart('styles')
        if category is None or category == 'automatic':
            content = self.get_xmlpart('content')
            return (styles.get_style_list(family=family, category=category)
                    + content.get_style_list(family=family,
                                             category=category))
        return styles.get_style_list(family=family, category=category)


    def get_style(self, name, family, retrieve_by='name'):
        _check_arguments(family=family)
        # 1. content
        # TODO except retrieve_by is "display-name"
        content = self.get_xmlpart('content')
        element = content.get_style(name, family)
        if element is not None:
            return element
        # 2. styles
        styles = self.get_xmlpart('styles')
        return styles.get_style(name, family, retrieve_by=retrieve_by)



#
# odf_document factories
#

def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.

    Example::

        >>> uri = 'uri://of/a/document.odt'
        >>> document = odf_get_document(uri)
    """
    container = odf_get_container(uri)
    return odf_document(container)



def odf_new_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.

    Example::

        >>> uri = 'uri://of/a/template.ott'
        >>> document = odf_new_document_from_template(uri)
    """
    container = odf_new_container_from_template(template_uri)
    return odf_document(container)



def odf_new_document_from_class(odf_class):
    """Return an "odf_document" instance of the given class.
    Arguments:

        odf_class -- 'text', 'spreadsheet', 'presentation' or 'drawing'

    Example::

        >>> document = odf_new_document_from_class('spreadsheet')
    """
    container = odf_new_container_from_class(odf_class)
    return odf_document(container)
