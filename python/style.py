# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import register_element_class, odf_create_element, odf_element
from paragraph import odf_create_paragraph


def odf_create_style(name, family, area=None, **kw):
    """Create a style element with the given name, related to the given
    family.

    Arguments:

        name -- unicode

        family -- 'paragraph', 'text', 'section', 'table', 'tablecolumn',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'list', 'number', 'page-layout' or
                  'master-page'

        area -- the "<area>-properties" where to store properties,
                identical to the family by default

        kw -- properties to create on the fly

    Return: odf_element
    """
    data = u'<style:style style:name="%s" style:family="%s"/>'
    element = odf_create_element(data % (name, family))
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


    def set_style_properties(self, properties=None, area=None, **kw):
        """Set the properties of the "area" type of this style. Properties
        are given either as a dict or as named arguments (or both). The area
        is identical to the style family by default. If the properties
        element is missing, it is created.
        Arguments:

            properties -- dict
            area -- str
        """
        if area is None:
            area = self.get_attribute('style:family')
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            element = odf_create_element('<style:%s-properties/>' % area)
            self.append_element(element)
        if properties is not None:
            for key, value in properties.iteritems():
                if value is None:
                    element.del_attribute(key)
                else:
                    element.set_attribute(key, value)
        for key, value in kw.iteritems():
            if value is None:
                element.del_attribute(key)
            else:
                element.set_attribute(key, value)


    def del_style_properties(self, properties=None, area=None, *args):
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
        if properties is not None:
            for key in properties:
                element.del_attribute(key)
        for key in args:
            element.del_attribute(key)



class odf_page_layout(odf_style):
    """Phyisical presentation of a page.

    XXX to verify
    """
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
             'style:footer-style'):
    register_element_class(name, odf_style)
register_element_class('style:page-layout', odf_page_layout)
register_element_class('style:master-page', odf_master_page)
