# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from lpod
from datatype import Boolean
from element import register_element_class, odf_create_element, odf_element
from utils import _get_style_tagname, _expand_properties, _merge_dicts
from utils import _get_element


def odf_create_style(family, name=None, display_name=None, parent=None,
        # Where properties apply
        area=None,
        # For family 'text':
        color=None, background_color=None, italic=False, bold=False,
        # For family 'paragraph'
        master_page=None,
        # For family 'master-page'
        layout=None, next=None,
        # For family 'table-cell'
        data_style=None, border=None, border_top=None, border_right=None,
        border_bottom=None, border_left=None, shadow=None,
        # For family 'table-row'
        height=None, use_optimal_height=None,
        # For family 'table-column'
        width=None, break_before=None, break_after=None,
        # Every other property
        **kw):
    """Create a style of the given family. The name is not mandatory at this
    point but will become required when inserting in a document as a common
    style.

    The display name is the name the user sees in an office application.

    The parent is the name of the style this style will inherit from.

    To set properties, pass them as keyword arguments. The area properties
    apply to is optional and defaults to the family.

    Arguments:

        family -- 'paragraph', 'text', 'section', 'table', 'table-column',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'list', 'number', 'page-layout'
                  'font-face', or 'master-page'

        name -- unicode

        display_name -- unicode

        parent -- unicode

        area -- str

    'text' Properties:

        italic -- bool

        bold -- bool

    'paragraph' Properties:

        master_page -- unicode

    'master-page' Properties:

        layout -- unicode

        next -- unicode

    'table-cell' Properties:

        border, border_top, border_right, border_bottom, border_left -- str,
        e.g. "0.002cm solid #000000" or 'none'

        shadow -- str, e.g. "#808080 0.176cm 0.176cm"

    'table-row' Properties:

        height -- str, e.g. '5cm'

        use_optimal_height -- bool

    'table-column' Properties:

        width -- str, e.g. '5cm'

        break_before -- 'page', 'column' or 'auto'

        break_after -- 'page', 'column' or 'auto'

    Return: odf_style
    """
    tagname, famattr = _get_style_tagname(family)
    element = odf_create_element(tagname)
    # Common attributes
    if name:
        element.set_style_name(name)
    if famattr:
        element.set_attribute('style:family', famattr)
    if display_name:
        element.set_attribute('style:display-name', display_name)
    if parent:
        element.set_attribute('style:parent-style-name', parent)
    # Paragraph
    if family == 'paragraph':
        if master_page:
            element.set_attribute('style:master-page-name', master_page)
    # Master Page
    if family == 'master-page':
        if layout:
            element.set_attribute('style:page-layout-name', layout)
        if next:
            element.set_attribute('style:next-style-name', next)
    # Properties
    if area is None:
        area = family
    # Text
    if area == 'text':
        if color:
            kw['fo:color'] = color
        if background_color:
            kw['fo:background-color'] = background_color
        if italic:
            kw['fo:font-style'] = 'italic'
            kw['style:font-style-asian'] = 'italic'
            kw['style:font-style-complex'] = 'italic'
        if bold:
            kw['fo:font-weight'] = 'bold'
            kw['style:font-weight-asian'] = 'bold'
            kw['style:font-weight-complex'] = 'bold'
    # Table cell
    elif area == 'table-cell':
        if border:
            kw['fo:border'] = border
        elif border_top or border_right or border_bottom or border_left:
            kw['fo:border-top'] = border_top or 'none'
            kw['fo:border-right'] = border_right or 'none'
            kw['fo:border-bottom'] = border_bottom or 'none'
            kw['fo:border-left'] = border_left or 'none'
        if shadow:
            kw['style:shadow'] = shadow
    # Table row
    elif area == 'table-row':
        if height:
            kw['style:row-height'] = height
        if use_optimal_height is not None:
            kw['style:use-optimal-row-height'] = Boolean.encode(
                    use_optimal_height)
    # Table column
    elif area == 'table-column':
        if width:
            kw['style:column-width']  = width
        if break_before:
            kw['fo:break-before'] = break_before
        if break_after:
            kw['fo:break-after'] = break_after
    if kw:
        element.set_style_properties(kw, area=area)
    return element



class odf_style(odf_element):
    """Specialised element for styles, yet generic to all style types.
    """
    def get_style_name(self):
        return self.get_attribute('style:name')


    def set_style_name(self, name):
        self.set_attribute('style:name', name)


    def get_style_display_name(self):
        return self.get_attribute('style:display-name')


    def get_style_family(self):
        return self.get_attribute('style:family')


    def set_style_family(self, family):
        self.set_attribute('style:family', family)


    def get_parent_style_name(self):
        """Will only return a name, not an object, because we don't have
        access to the XML part from here.

        See odf_styles.get_parent_style
        """
        return self.get_attribute('style:parent-style-name')


    def set_parent_style_name(self, name):
        self.set_attribute('style:parent-style-name', name)


    def get_style_properties(self, area=None):
        """Get the mapping of all properties of this style. By default the
        properties of the same family, e.g. a paragraph style and its
        paragraph properties. Specify the area to get the text properties of
        a paragraph style for example.

        Arguments:

            area -- str

        Return: dict
        """
        if area is None:
            area = self.get_style_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            return None
        properties = element.get_attributes()
        # Nested properties are nested dictionaries
        for child in element.get_children():
            properties[child.get_tag()] = child.get_attributes()
        return properties


    def set_style_properties(self, properties={}, style=None, area=None,
            **kw):
        """Set the properties of the "area" type of this style. Properties
        are given either as a dict or as named arguments (or both). The area
        is identical to the style family by default. If the properties
        element is missing, it is created.

        Instead of properties, you can pass a style with properties of the
        same area. These will be copied.

        Arguments:

            properties -- dict

            style -- odf_style

            area -- 'paragraph', 'text'...
        """
        if area is None:
            area = self.get_style_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            element = odf_create_element('style:%s-properties' % area)
            self.append(element)
        if properties or kw:
            properties = _expand_properties(_merge_dicts(properties, kw))
        elif style is not None:
            properties = style.get_style_properties(area=area)
            if properties is None:
                return
        for key, value in properties.iteritems():
            if value is None:
                element.del_attribute(key)
            else:
                element.set_attribute(key, value)


    def del_style_properties(self, properties=[], area=None, *args):
        """Delete the given properties, either by list argument or
        positional argument (or both). Remove only from the given area,
        identical to the style family by default.

        Arguments:

            properties -- list

            area -- str
        """
        if area is None:
            area = self.get_style_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            raise ValueError, "properties element is inexistent"
        for key in _expand_properties(properties):
            element.del_attribute(key)


    def set_background(self, color=None, uri=None, position='center',
                       repeat=None, opacity=None, filter=None):
        """Set the background color of a text style, or the background color
        or image of a paragraph style or page layout.

        With no argument, remove any existing background.

        The position is one or two of 'center', 'left', 'right', 'top' or
        'bottom'.

        The repeat is 'no-repeat', 'repeat' or 'stretch'.

        The opacity is a percentage integer (not a string with the '%s' sign)

        The filter is an application-specific filter name defined elsewhere.

        Though this method is defined on the base style class, it will raise
        an error if the style type is not compatible.

        Arguments:

            color -- '#rrggbb'

            uri -- str

            position -- str

            repeat -- str

            opacity -- int

            filter -- str
        """
        family = self.get_style_family()
        if family not in ('text', 'paragraph', 'page-layout', 'section',
                          'table', 'table-row', 'table-cell', 'graphic'):
            raise TypeError, 'no background support for this family'
        if uri is not None and family == 'text':
            raise TypeError, 'no background image for text styles'
        properties = self.get_element('style:%s-properties' % family)
        if properties is None:
            bg_image = None
        else:
            bg_image = properties.get_element('style:background-image')
        # Erasing
        if color is None and uri is None:
            if properties is None:
                return
            properties.del_attribute('fo:background-color')
            if bg_image is not None:
                properties.delete(bg_image)
            return
        # Add the properties if necessary
        if properties is None:
            properties = odf_create_element('style:%s-properties' % family)
            self.append(properties)
        # Add the color...
        if color:
            properties.set_attribute('fo:background-color', color)
            if bg_image is not None:
                properties.delete(bg_image)
        # ... or the background
        elif uri:
            properties.set_attribute('fo:background-color', 'transparent')
            if bg_image is None:
                bg_image = odf_create_element('style:background-image')
                properties.append(bg_image)
            bg_image.set_attribute('xlink:href',  uri)
            if position:
                bg_image.set_attribute('style:position', position)
            if repeat:
                bg_image.set_attribute('style:repeat', repeat)
            if opacity:
                bg_image.set_attribute('draw:opacity', str(opacity))
            if filter:
                bg_image.set_attribute('style:filter-name', filter)



class odf_list_style(odf_style):
    """A list style is a container for list level styles.
    """
    any_style = ('(text:list-level-style-number'
                 '|text:list-level-style-bullet'
                 '|text:list-level-style-image)')


    def get_style_family(self):
        return 'list'


    def get_level_style(self, level):
        return _get_element(self, self.any_style, 0, level=level)


    def set_level_style(self, level, type=None, format=None, prefix=None,
            suffix=None, character=None, uri=None, display_levels=None,
            start_value=None, style=None, clone=None):
        # Expected name
        level_style_name = 'text:list-level-style-%s' % type
        was_created = False
        # Cloning or reusing an existing element
        if clone is not None:
            level_style = clone.clone()
            level_style_name = level_style.get_tag()
            was_created = True
        else:
            level_style = self.get_level_style(level)
            if level_style is None:
                level_style = odf_create_element(level_style_name)
                was_created = True
        # Transmute if the type changed
        if level_style.get_tag() != level_style_name:
            level_style.set_tag(level_style_name)
        # Set the level
        level_style.set_attribute('text:level', str(level))
        # Set the main attribute
        if type == 'number':
            if clone is None and format is None:
                raise ValueError, "format is missing"
            level_style.set_attribute('fo:num-format', format)
        elif type == 'bullet':
            if clone is None and character is None:
                raise ValueError, "bullet character is missing"
            level_style.set_attribute('text:bullet-char', character)
        elif type == 'image':
            if clone is None and uri is None:
                raise ValueError, "image URI is missing"
            level_style.set_attribute('xlink:href', uri)
        elif clone is None:
            raise ValueError, "unknown level style type: %s" % type
        # Set attributes
        if prefix:
            level_style.set_attribute('style:num-prefix', prefix)
        if suffix:
            level_style.set_attribute('style:num-suffix', suffix)
        if display_levels:
            level_style.set_attribute('text:display-levels',
                                      str(display_levels))
        if start_value:
            level_style.set_attribute('text:start-value', str(start_value))
        if style:
            level_style.set_text_style(style)
        # Commit the creation
        if was_created:
            self.append(level_style)
        return level_style



class odf_outline_style(odf_list_style):

    # FIXME stubs
    def get_style_family(self):
        return 'outline'



class odf_page_layout(odf_style):
    """Physical presentation of a page.

    XXX to verify
    """
    def get_style_family(self):
        return 'page-layout'


    def set_style_family(self):
        raise ValueError, 'family is read-only'


    def get_header_style(self):
        return self.get_element('style:header-style')


    def set_header_style(self, new_style):
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)


    def get_footer_style(self):
        return self.get_element('style:footer-style')


    def set_footer_style(self, new_style):
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)



class odf_master_page(odf_style):
    """A master page is the style of a page.

    Physical presentation is in the associated page layout.

    XXX to verify
    """
    def __set_header_or_footer(self, text_or_element, name='header',
                               style=u"Header"):
        if name == 'header':
            header_or_footer = self.get_header()
        else:
            header_or_footer = self.get_footer()
        if header_or_footer is None:
            header_or_footer = odf_create_element('style:' + name)
            self.append(header_or_footer)
        else:
            header_or_footer.clear()
        if not isinstance(text_or_element, (list, tuple)):
            # Already a header or footer?
            if (isinstance(text_or_element, odf_element)
                    and text_or_element.get_tag() == 'style:%s' % name):
                self.delete(header_or_footer)
                self.append(text_or_element)
                return
            text_or_element = [text_or_element]
        # FIXME cyclic import
        from paragraph import odf_create_paragraph
        for item in text_or_element:
            if type(item) is unicode:
                paragraph = odf_create_paragraph(item, style=style)
                header_or_footer.append(paragraph)
            elif isinstance(item, odf_element):
                header_or_footer.append(item)


    #
    # Public API
    #

    def get_style_family(self):
        return 'master-page'


    def set_style_family(self):
        raise ValueError, 'family is read-only'


    def get_page_layout_name(self):
        return self.get_attribute('style:page-layout-name')


    def set_page_layout_name(self, name):
        self.set_attribute('style:page-layout-name', name)


    def get_header(self):
        """Get the element that contains the header contents.

        If None, no header was set.
        """
        return self.get_element('style:header')


    def set_header(self, text_or_element):
        """Create or replace the header by the given content. It can already
        be a complete header.

        If you only want to update the existing header, get it and use the
        API.

        Arguments:

            text_or_element -- unicode or odf_element or a list of them
        """
        return self.__set_header_or_footer(text_or_element)


    def get_footer(self):
        """Get the element that contains the footer contents.

        If None, no footer was set.
        """
        return self.get_element('style:footer')


    def set_footer(self, text_or_element):
        """Create or replace the footer by the given content. It can already
        be a complete footer.

        If you only want to update the existing footer, get it and use the
        API.

        Arguments:

            text_or_element -- unicode or odf_element or a list of them
        """
        return self.__set_header_or_footer(text_or_element, name='footer',
                                           style=u"Footer")


# FIXME stub
class odf_font_style(odf_style):

    def get_style_family(self):
        return 'font-face'



# FIXME stub
class odf_number_style(odf_style):

    def get_style_family(self):
        return 'number'



# FIXME stub
class odf_percentage_style(odf_style):

    def get_style_family(self):
        return 'percentage'



# FIXME stub
class odf_time_style(odf_style):

    def get_style_family(self):
        return 'time'



# FIXME stub
class odf_date_style(odf_style):

    def get_style_family(self):
        return 'date'



# FIXME stub
class odf_currency_style(odf_style):

    def get_style_family(self):
        return 'currency'



# Some predefined styles
def odf_create_default_number_style():
    return odf_create_element(
            """<number:number-style style:name="lpod-default-number-style">
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"/>
               </number:number-style>""")



def odf_create_default_percentage_style():
    return odf_create_element(
            """<number:percentage-style
                  style:name="lpod-default-percentage-style">
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"/>
                  <number:text>%</number:text>
               </number:percentage-style>""")



def odf_create_default_time_style():
    return odf_create_element(
            """<number:time-style style:name="lpod-default-time-style">
                  <number:hours number:style="long"/>
                  <number:text>:</number:text>
                  <number:minutes number:style="long"/>
                  <number:text>:</number:text>
                  <number:seconds number:style="long"/>
               </number:time-style>""")



def odf_create_default_date_style():
    return odf_create_element(
            """<number:date-style style:name="lpod-default-date-style">
                  <number:year number:style="long"/>
                  <number:text>-</number:text>
                  <number:month number:style="long"/>
                  <number:text>-</number:text>
                  <number:day number:style="long"/>
               </number:date-style>""")



def odf_create_default_boolean_style():
    return odf_create_element(
            """<number:boolean-style style:name="lpod-default-boolean-style">
                  <number:boolean/>
               </number:boolean-style>""")



def odf_create_default_currency_style():
    return odf_create_element(
            """<number:currency-style style:name="lpod-default-currency-style">
                  <number:text>-</number:text>
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"
                                 number:grouping="true"/>
                  <number:text> </number:text>
                  <number:currency-symbol
                      number:language="fr"
                      number:country="FR">€</number:currency-symbol>
               </number:currency-style>""")



registered_styles = []


def register_style(tagname, cls):
    register_element_class(tagname, cls)
    registered_styles.append(tagname)


# FIXME there are (many) more
for name in ('style:style', 'style:default-style', 'style:header-style',
        'style:footer-style', 'text:list-level-style-number',
        'text:list-level-style-bullet', 'text:list-level-style-image',
        'style:presentation-page-layout'):
    register_style(name, odf_style)
register_style('text:list-style', odf_list_style)
register_style('text:outline-style', odf_outline_style)
register_style('style:page-layout', odf_page_layout)
register_style('style:master-page', odf_master_page)
register_style('style:font-face', odf_font_style)
register_style('number:number-style', odf_number_style)
register_style('number:percentage-style', odf_percentage_style)
register_style('number:time-style', odf_time_style)
register_style('number:date-style', odf_date_style)
register_style('number:currency-style', odf_currency_style)
