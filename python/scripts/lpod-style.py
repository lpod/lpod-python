#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document


translations = {
    'office:styles/style:default-style': u'Default styles',
    'office:styles/style:style': u'Named styles',
    'style:default-style': u'Default style',
    'style:style': u'Named style',
    'style:graphic-properties': u'Graphic properties',
    'style:paragraph-properties': u'Paragraph properties',
    'style:text-properties': u'Text properties',
    'style:table-properties': u'Table properties',
    'style:table-row-properties': u'Row properties',
    'style:style': u'Named style',
    'style:tab-stops': u'Tabulations width',
    'style:tab-stop': u'Tabulation width',
    'text:outline-style': u'Outline style',
    'text:outline-level-style': u'Level style',
    'style:list-level-properties': u'List level properties',
    'style:list-level-label-alignment': u'List level label alignment',
    'text:notes-configuration': u'Notes configuration',
    'text:linenumbering-configuration': u'Line numbering configuration',
    'office:automatic-styles': u'Automatic styles',
    'style:page-layout': u'Page layout',
    'style:page-layout-properties': u'Page layout properties',
    'style:footnote-sep': u'Footnote separation',
    'office:master-styles': u'Master page styles',
    'style:master-page': u'Master page'}

underline_lvl = ['#', '=', '-', ':', '`', "'", '"', '~', '^', '_', '*', '+']


def make_style_structure(style_element, child_to_search=None):
    sub_struct = []
    name = style_element.get_name()
    attributes = style_element.get_attributes()
    # Allow to handle named and default styles which are in the same
    # office:styles element unlike automatic and master page styles
    if child_to_search is not None:
        children = style_element.get_element_list(child_to_search)
        # Rebuild the name to have a pertinent translation
        name = '%s/%s' % (name, child_to_search)
    # Default behaviour
    else:
        children = style_element.get_children()
    for child in children:
        sub_struct.append(make_style_structure(child))
    return (name, attributes, sub_struct)



def structure_to_str(structure, level=0, overline=False):
    structure.sort()
    text = []
    for name, attributes, sub_struct in structure:
        # Don't show the empty elements
        if not sub_struct and not attributes:
            return None
        name = translations[name]
        # Underline and Overline the name
        if level < len(underline_lvl):
            underline = underline_lvl[level] * len(name)
            if overline:
                text.append(underline)
            text.append(name)
            text.append(underline)
        # Add a separation between name and attributes
        text[-1] += '\n'
        attrs = []
        # Attributes
        for key, value in attributes.iteritems():
            attrs.append('%s: %s' % (key, value))
        if attrs:
            attrs.sort()
            # Add a separation between attributes and children
            attrs[-1] += '\n'
            text.extend(attrs)
        # Children
        sub_struct_text = structure_to_str(sub_struct, level + 1)
        if sub_struct_text:
            text.append(sub_struct_text)
    return u'\n'.join(text)



def lpod_show(odf_file_url, style_types):
    """Show the different types of styles of a document and their properties.
    """
    style_elements = {
        'default': ('office:styles', 'style:default-style'),
        'named': ('office:styles', 'style:style'),
        'automatic': ('office:automatic-styles', None),
        'master': ('office:master-styles', None)}

    style_types.sort()
    document = odf_get_document(odf_file_url)
    styles = document.get_xmlpart('styles')
    for type in style_types:
        parent, name = style_elements[type]
        style = styles.get_element(parent)
        # Make the structure
        style_structure = make_style_structure(style, name)
        # Transform the structure to a multiline string
        output = '%s\n' % structure_to_str([style_structure], overline=True)
        # Print the styles
        stdout.write(output)
        stdout.flush()



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'A command line interface to manipulate styles of ' \
                  'OpenDocument files.'
    oparser = OptionParser(usage, version=__version__, description=description)
    # --show
    help = ('show the styles of a document. The value is a comma separated '
            'list. Authorized values are automatic, default, master, named '
            'and all.')
    oparser.add_option('--show', dest='show', action='store',
                       metavar='<style list>', help=help)
    # Parse options
    opts, args = oparser.parse_args()
    if len(args) < 1:
        oparser.print_help()
        exit(1)
    # Get the ODF file url
    odf_file_url = args[0]

    # Expand all
    style_types = opts.show.replace('all', 'default, named, automatic, master')
    # Transform the comma separated list into a true list object
    style_types = [type.strip() for type in style_types.split(',')]
    # Check if the style type is known
    for type in style_types:
        if type not in ('default', 'named', 'automatic', 'master'):
            oparser.error('Unknown %s style' % type)
    lpod_show(odf_file_url, style_types)

