# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_create_element, odf_element


class odf_style(odf_element):
    """Specialised element for styles, yet generic to all style types.
    """
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



# FIXME there are (many) more
for name in ('style:style',):
    register_element_class(name, odf_style)
