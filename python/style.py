# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import register_element_class, odf_create_element, odf_element
from paragraph import odf_create_paragraph
from utils import _get_style_tagname, _expand_properties, _merge_dicts
from utils import _get_element


def odf_create_style(family, name=None, display_name=None, parent=None,
                     area=None, **kw):
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
                  'control', 'ruby', 'list', 'number', 'page-layout' or
                  'master-page'

        name -- unicode

        display_name -- unicode

        parent -- unicode

        area -- str

    Return: odf_style
    """
    tagname, famattr = _get_style_tagname(family)
    element = odf_create_element('<%s/>' % tagname)
    if name:
        element.set_style_name(name)
    if famattr:
        element.set_attribute('style:family', famattr)
    if display_name:
        element.set_attribute('style:display-name', display_name)
    if parent:
        element.set_attribute('style:parent-style-name', parent)
    if kw:
        if area is None:
            area = family
        element.set_style_properties(kw, area=area)
    return element



class odf_style(odf_element):
    """Specialised element for styles, yet generic to all style types.
    """
    def get_style_name(self):
        return self.get_attribute('style:name')


    def set_style_name(self, name):
        self.set_attribute('style:name', name)


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
            area = self.get_attribute('style:family')
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            return None
        properties = element.get_attributes()
        # Nested properties are nested dictionaries
        for child in element.get_children():
            properties[child.get_name()] = child.get_attributes()
        return properties


    def set_style_properties(self, properties={}, style=None, area=None, **kw):
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
            area = self.get_attribute('style:family')
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            element = odf_create_element('<style:%s-properties/>' % area)
            self.append_element(element)
        if properties:
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
            area = self.get_attribute('style:family')
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

        The opacity is an percentage integer (no string with the '%s' sign)

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
            properties = odf_create_element('<style:%s-properties/>'
                                            % family)
            self.append_element(properties)
        # Add the color...
        if color:
            properties.set_attribute('fo:background-color', color)
            if bg_image is not None:
                properties.delete(bg_image)
        # ... or the background
        elif uri:
            properties.set_attribute('fo:background-color', 'transparent')
            if bg_image is None:
                bg_image = odf_create_element('<style:background-image/>')
                properties.append_element(bg_image)
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
    any_style = 'text:list-level-style-(number|bullet|image)',
    def get_level_style(self, level):
        return _get_element(self.any_style, level=level)


    def set_level_style(self, level, type=None, format=None, prefix=None,
            suffix=None, character=None, uri=None, display_levels=None,
            start_value=None, style=None, clone=None):
        # Expected name
        level_style_name = 'text:list-level-style-%s' % type
        was_created = False
        # Cloning or reusing an existing element
        if clone is not None:
            level_style = clone.clone()
            was_created = True
        else:
            level_style = self.get_level_style(level)
            if level_style is None:
                level_style = odf_create_element(level_style_name)
                was_created = True
        # Transmute if the type changed
        if level_style.get_name() != level_style_name:
            level_style.set_name(level_style_name)
        # Set the main attribute
        if type == 'number':
            if format is None:
                raise ValueError, "format is missing"
            level_style.set_attribute('fo:num-format', format)
        elif type == 'bullet':
            if character is None:
                raise ValueError, "bullet character is missing"
            level_style.set_attribute('text:bullet-char', character)
        elif type == 'image':
            if uri is None:
                raise ValueError, "image URI is missing"
            level_style.set_attribute('xlink:href', uri)
        else:
            raise ValueError, "unknown level style type: %s" % type
        # Set attributes
        if display_levels:
            level_style.set_attribute('text:display-levels', display_levels)
        if start_value:
            level_style.set_attribute('text:start-value', start_value)
        if style:
            level_style.set_attribute('text:style-name', style)
        # Commit the creation
        if was_created:
            level_style.set_attribute('text:level', level)
            self.append_element(level_style)
        return level_style



class odf_page_layout(odf_style):
    """Phyisical presentation of a page.

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
        self.append_element(new_style)


    def get_footer_style(self):
        return self.get_element('style:footer-style')


    def set_footer_style(self, new_style):
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append_element(new_style)



class odf_master_page(odf_style):
    """A master page is the style of a page.

    Phyisical presentation is in the associated page layout.

    XXX to verify
    """
    def __set_header_or_footer(self, text_or_element, name='header',
                               style=u"Header"):
        if name == 'header':
            header_or_footer = self.get_header()
        else:
            header_or_footer = self.get_footer()
        if header_or_footer is None:
            header_or_footer = odf_create_element('<style:%s/>' % name)
            self.append_element(header_or_footer)
        else:
            header_or_footer.clear()
        if not isinstance(text_or_element, (list, tuple)):
            # Already a header or footer?
            if (isinstance(text_or_element, odf_element)
                    and text_or_element.get_name() == 'style:%s' % name):
                self.delete(header_or_footer)
                self.append_element(text_or_element)
                return
            text_or_element = [text_or_element]
        for item in text_or_element:
            if type(item) is unicode:
                paragraph = odf_create_paragraph(item, style=style)
                header_or_footer.append_element(paragraph)
            elif isinstance(item, odf_element):
                header_or_footer.append_element(item)


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



# FIXME there are (many) more
for name in ('style:style', 'style:default-style', 'style:header-style',
             'style:footer-style', 'text:list-level-style-number',
             'text:list-level-style-bullet', 'text:list-level-style-image'):
    register_element_class(name, odf_style)
register_element_class('text:list-style', odf_list_style)
register_element_class('style:page-layout', odf_page_layout)
register_element_class('style:master-page', odf_master_page)
