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
    families.sort()
    document = odf_get_document(odf_file_url)
    output = document.show_styles(family=families)
    # Translate titles into a more pertinent text
    for tag_name, translation in translations.iteritems():
        output = output.replace(tag_name + '\n', translation + '\n')
    # Print the styles
    stdout.write(output.encode('utf-8'))
    stdout.flush()



def merge(source_url, dest_url):
    source = odf_get_document(source_url)
    dest = odf_get_document(dest_url)
    dest.merge_styles_from(source)
    dest.save(pretty=True)
    print "Done (0 error, 0 warning)."



if  __name__ == '__main__':

    # Options initialisation
    usage = '%prog <file>'
    description = 'A command line interface to manipulate styles of ' \
                  'OpenDocument files.'
    oparser = OptionParser(usage, version=__version__,
                           description=description)
    # --show
    help = ('show the styles of a document. The value is a comma separated '
            'list. Authorized values are automatic, default, master, named '
            'and all.')
    oparser.add_option('-s', '--show', dest='show', action='store',
                       default='', metavar='<style list>', help=help)
    # --merge
    help = ('Copy styles from FILE to <file>. Any style with the same name '
            'will be replaced.')
    oparser.add_option('-m', '--merge-styles-from', dest='merge',
                       action='store', metavar='FILE', help=help)
    # Parse options
    opts, args = oparser.parse_args()
    if len(args) != 1:
        oparser.print_help()
        exit(1)
    odf_file_url = args[0]

    if opts.show:
        if opts.show in ('', 'all'):
            families = style_families
        else:
            # Transform the comma separated list into a true list object
            families = [family.strip() for family in opts.show.split(',')]
        # Check if the style family is known
        for family in families:
            if family not in style_families:
                oparser.error('Unknown %s family' % family)
        show(odf_file_url, families)
    elif opts.merge:
        merge(opts.merge, odf_file_url)
    else:
        oparser.print_help()
        exit(1)
