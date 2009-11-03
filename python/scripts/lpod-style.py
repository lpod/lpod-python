#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library
from optparse import OptionParser
from sys import exit, stdout

# Import from lpod
from lpod import __version__
from lpod.document import odf_get_document
from lpod.style import odf_create_style
from lpod.styles import rgb2hex


translations = {
    # Families
    'paragraph': u'Paragraph styles',
    'text': u'Text styles',
    'graphic': u'Graphic styles',
    'table': u'Table styles',
    'list': u'List styles',
    'number': u'Number styles',
    'page-layout': u'Page layout styles',
    'master-page': u'Master page styles',
    # Style elements
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
    'style:master-page': u'Master page',
    'style:drawing-page-properties': u'Drawing page properties',
    'draw:layer-set': u'Layer set',
    'draw:layer': u'Layer',
    'text:list-style': u'List style',
    'text:list-level-style-bullet': u'List level style of bullet',
    'style:handout-master': u'Handout master',
    'draw:page-thumbnail': u'Page thumbnail',
    'draw:frame': u'Frame',
    'draw:image': u'Image',
    'presentation:notes': u'Notes',
    'draw:text-box': u'Text box',
    'text:p': u'Paragraph',
    'text:span': u'Span',
    'style:footer-style': u'Footer style',
    'style:header-footer-properties': u'Header and footer properties',
    'style:header-style': u'Header style',
    'style:footer': u'Footer',
    'text:h': u'Heading',
    'style:header': u'Header',
    'style:table-cell-properties': u'Cell properties',
    'style:footer-left': u'Footer left',
    'style:header-left': u'Header left',
    'style:region-left': u'Region left',
    'style:region-right': u'Region right',
    'text:date': u'Date'}


style_families = ['paragraph', 'text',  'graphic', 'page-layout',
                  'master-page']



def show(odf_file_url, families):
    """Show the different types of styles of a document and their properties.
    """
    # Ensure output is consistent across several runs (diff, etc.)
    families.sort()
    document = odf_get_document(odf_file_url)
    output = document.show_styles(family=families)
    # Translate titles into a more pertinent text
    for tag_name, translation in translations.iteritems():
        output = output.replace(tag_name + '\n', translation + '\n')
    # Print the styles
    stdout.write(output.encode('utf-8'))
    stdout.flush()



def merge(odf_file_url, from_file, pretty=False):
    source = odf_get_document(from_file)
    dest = odf_get_document(odf_file_url)
    dest.merge_styles_from(source)
    dest.save(pretty=pretty)
    print "Done (0 error, 0 warning)."



def highlight(odf_file_url, pattern, color, pretty=False):
    document = odf_get_document(odf_file_url)
    display_name = u"Highlight %s" % color
    print "display_name", display_name
    name = display_name.replace(u" ", u"_20_")
    print "name", name
    # Is our style already installed?
    style = document.get_style('text', name)
    if style is None:
        style = odf_create_style('text', name, display_name,
                background_color=rgb2hex(color))
        document.insert_style(style)
    body = document.get_body()
    i = -1
    for i, paragraph in enumerate(body.get_paragraph_list(regex=pattern)
            + body.get_heading_list(regex=pattern)):
        paragraph.set_span(name, regex=pattern)
    document.save(pretty=pretty)
    print (i + 1), "paragraphs changed (0 error, 0 warning)."



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'A command line interface to manipulate styles of ' \
                  'OpenDocument files.'
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --show
    help = ('show the styles of a document. The value is a comma separated '
            'list. Authorized values are automatic, default, master, named '
            'and all.')
    parser.add_option('-s', '--show', dest='show', action='store',
            default='', metavar='<style list>', help=help)
    # --merge
    help = ('copy styles from FILE to <file>. Any style with the same name '
            'will be replaced.')
    parser.add_option('-m', '--merge-styles-from', dest='merge',
            action='store', metavar='FILE', help=help)
    # --highlight
    help = ("highlight the text matching the regular expression PATTERN in "
            "the text (IN PLACE)")
    parser.add_option('-l', '--highlight', dest='highlight', action='store',
            metavar='PATTERN', help=help)
    # --color
    help = ("the name or #rrggbb color of the highlight: black, blue, "
            "brown, cyan, green, grey, magenta, orange, pink, red, violet, "
            "white, yellow (default)")
    parser.add_option('-c', '--color', dest='color', action='store',
            default='yellow', metavar='COLOR', help=help)
    # --pretty
    parser.add_option('-p', '--pretty', dest='pretty', action='store_true',
                      help="pretty print the XML of the output document")
    # Parse options
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit(1)
    odf_file_url = args[0]

    if options.show:
        if options.show in ('', 'all'):
            families = style_families
        else:
            # Transform the comma separated list into a true list object
            families = [family.strip() for family in options.show.split(',')]
        # Check if the style family is known
        for family in families:
            if family not in style_families:
                parser.error('Unknown %s family' % family)
        show(odf_file_url, families)
    elif options.merge:
        merge(odf_file_url, options.merge, pretty=options.pretty)
    elif options.highlight:
        highlight(odf_file_url, options.highlight, options.color,
                pretty=options.pretty)
    else:
        parser.print_help()
        exit(1)
