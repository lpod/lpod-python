#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
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

# Import from the standard library
from optparse import OptionParser
from os import makedirs
from os.path import splitext, join, dirname, exists, isabs
from sys import exit

# Import from lpod
from lpod import __version__, ODF_META
from lpod.const import ODF_EXTENSIONS
from lpod.datatype import Unit
from lpod.document import odf_get_document, odf_new_document, odf_document
from lpod.paragraph import odf_create_paragraph
from lpod.rst2odt import convert as rst_convert
from lpod.scriptutils import check_target_file
from lpod.table import odf_create_table, odf_create_row
from lpod.utils import oooc_to_ooow


def spreadsheet_to_text(indoc, outdoc):
    inbody = indoc.get_body()
    outbody = outdoc.get_body()
    # Copy tables
    for intable in inbody.get_tables():
        # clone/rstrip the table
        clone = intable.clone()
        clone.rstrip(aggressive=True)
        # Skip empty table
        if clone.get_size() == (0, 0):
            continue
        # At least OOo Writer doesn't like formulas referencing merged
        # cells, so expand
        outtable = odf_create_table(clone.get_name(),
                style=clone.get_style())
        # Columns
        for column in clone.traverse_columns():
            outtable.append(column)
        # Rows
        for inrow in clone.traverse():
            outrow = odf_create_row(style=inrow.get_style())
            # Cells
            for cell in inrow.traverse():
                # Formula
                formula = cell.get_formula()
                if formula is not None:
                    if formula.startswith('oooc:'):
                        formula = oooc_to_ooow(formula)
                    else:
                        # Found an OpenFormula test case
                        raise NotImplementedError, formula
                    cell.set_formula(formula)
                outrow.append(cell)
            outtable.append_row(outrow)
        outbody.append(outtable)
        # Separate tables with an empty line
        outbody.append(odf_create_paragraph())
    # Copy styles
    for family in ('table', 'table-column', 'table-row', 'table-cell'):
        for style in indoc.get_style_list(family=family):
            automatic = (style.get_parent().get_tag()
                    == 'office:automatic-styles')
            default = style.get_tag() == 'style:default-style'
            outdoc.insert_style(style, automatic=automatic,
                    default=default)



def spreadsheet_to_csv(indoc, outdoc):
    inbody = indoc.get_body()

    # Copy only the first table
    tables =  inbody.get_tables()
    if not tables:
        return
    table = tables[0]

    # clone/rstrip the table
    table = table.clone()
    table.rstrip(aggressive=True)

    # Skip empty table
    if table.get_size() == (0, 0):
        return

    # And save
    table.to_csv(outdoc)



def spreadsheet_to_rst(indoc, outdoc):
    inbody = indoc.get_body()

    context = {'document': indoc,
               'footnotes': [],
               'endnotes': [],
               'annotations': [],
               'rst_mode': True,
               'img_counter': 0,
               'images': [],
               'no_img_level': 0}

    # Convert tables
    for table in inbody.get_tables():
        # clone/rstrip the table
        table = table.clone()
        table.rstrip(aggressive=True)

        # Skip empty table
        if table.get_size() == (0, 0):
            continue

        name = table.get_name().encode('utf-8')
        outdoc.write(name)
        outdoc.write('\n')
        outdoc.write('=' * len(name))
        outdoc.write('\n')
        outdoc.write(table.get_formatted_text(context).encode('utf-8'))
        outdoc.write('\n\n')



def rst_to_text(indoc, outdoc):
    rst_convert(outdoc, indoc)



def text_to_rst(indoc, outdoc):
    outdoc.write(indoc.get_formatted_text(True).encode('utf-8'))



def text_to_txt(indoc, outdoc):
    outdoc.write(indoc.get_formatted_text(False).encode('utf-8'))



def get_string(value, encoding):
    if value is None:
        return ''
    return value.strip().encode(encoding)



def write_presentation_header(indoc, outdoc, encoding):
    meta = indoc.get_part(ODF_META)
    lang = meta.get_language() or ''
    description = get_string(meta.get_description(), encoding)
    subject = get_string(meta.get_subject(), encoding)
    keywords = get_string(meta.get_keywords(), encoding)
    title = get_string(meta.get_title(), encoding)
    modified = str(meta.get_modification_date())
    author = get_string(meta.get_creator(), encoding)
    outdoc.write('''<?xml version="1.0" encoding="%(encoding)s"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="%(lang)s">
  <head>
    <meta http-equiv="Content-Type" content="text/html;
      charset=%(encoding)s"/>
    <title>%(title)s</title>
    <!-- metadata -->
    <meta name="generator" content="lpOD" />
    <meta name="version" content="%(version)s" />
    <meta name="presdate" content="%(modified)s" />
    <meta name="author" content="%(author)s" />
    <meta name="description" lang="%(lang)s" content="%(description)s"/>
    <meta name="subject" lang="%(lang)s" content="%(subject)s"/>
    <meta name="keywords" lang="%(lang)s" content="%(keywords)s"/>
    <!-- S5 integration: http://meyerweb.com/eric/tools/s5/v/1.1/s5-11.zip -->
    <!-- configuration parameters -->
    <meta name="defaultView" content="slideshow" />
    <meta name="controlVis" content="hidden" />
    <!-- style sheet links -->
    <link rel="stylesheet" href="ui/default/slides.css" type="text/css"
      media="projection" id="slideProj" />
    <link rel="stylesheet" href="ui/default/outline.css" type="text/css"
    media="screen" id="outlineStyle" />
    <link rel="stylesheet" href="ui/default/print.css" type="text/css"
      media="print" id="slidePrint" />
    <link rel="stylesheet" href="ui/default/opera.css" type="text/css"
      media="projection" id="operaFix" />
    <!-- S5 JS -->
    <script src="ui/default/slides.js" type="text/javascript"></script>
  </head>
  <body>
    <div class="layout">
      <div id="controls"><!-- DO NOT EDIT --></div>
      <div id="currentSlide"><!-- DO NOT EDIT --></div>
      <div id="header"></div>
      <div id="footer">
        <h1>%(title)s</h1>
        <h2>Generated by <a href="http://www.lpod-project.org/">lpOD</a></h2>
      </div>
    </div>

    <div class="presentation">\n''' % {'lang': lang, 'encoding': encoding,
        'version': __version__, 'modified': modified, 'author': author,
        'description': description, 'subject': subject, 'keywords': keywords,
        'title': title})



def write_presentation_footer(indoc, outdoc, encoding):
    outdoc.write('''    </div>
    <div id="generator">
      <p>Generated with lpOD %(version)s</p>
    </div>
  </body>
</html>''' % {'version': __version__})



def write_presentation_title(frame, outdoc, encoding):
    presentation_class = frame.get_presentation_class()
    tag = 'h1' if presentation_class == 'title' else 'h2'
    title = '<br/>'.join([get_string(p.get_text(recursive=True), encoding)
        for p in frame.get_paragraphs()])
    outdoc.write('<%(tag)s>%(title)s</%(tag)s>\n' % {'tag': tag, 'title':
        title})



def make_image_path(outdoc, src):
    filename = outdoc.name
    basedir = join(dirname(filename), dirname(src))
    if not exists(basedir):
        makedirs(basedir)
    path = join(dirname(filename), src)
    return path



def write_presentation_table(frame, outdoc, encoding):
    width, height = frame.get_size()
    width = Unit(width).convert('px')
    height = Unit(height).convert('px')
    outdoc.write('<table width="%(width)s" height="%(height)s">')
    table = frame.get_table()
    for y, row in table.get_rows():
        outdoc.write('  <tr>')
        for x, cell in row.get_cells():
            text = get_string(cell.get_text_content(), encoding)
            outdoc.write('    <td>%s</td>\n' % text)
        outdoc.write('  </tr>\n')
    outdoc.write('</table>\n')



def write_presentation_image(frame, indoc, outdoc, encoding):
    outdoc.write('<div class="image">\n')
    href = None
    listeners = frame.get_element('office:event-listeners')
    if listeners is not None:
        for listener in listeners.get_elements('presentation:event-listener'):
            href = listener.get_attribute('xlink:href')
            if href is not None:
                href = get_string(href, encoding)
                outdoc.write('  <a href="%s">' % href)
    image = frame.get_image()
    src = get_string(image.get_url(), encoding)
    src = src.lstrip('./')
    if not isabs(src):
        f = open(make_image_path(outdoc, src), 'wb')
        f.write(indoc.get_part(src))
        f.close()
    title = get_string(frame.get_svg_title(), encoding)
    description = get_string(frame.get_svg_description(), encoding)
    outdoc.write('  <img src="%(src)s" title="%(title)s" '
      'alt="%(description)s"/>' % {'src': src, 'title': title,
          'description': description})
    if href is None:
        outdoc.write('\n')
    else:
        outdoc.write('  </a>\n')
    outdoc.write('</div>\n')



def write_presentation_plugin(frame, indoc, outdoc, encoding):
    plugin = frame.get_element('draw:plugin')
    src = plugin.get_attribute('xlink:href')
    if not isabs(src):
        f = open(make_image_path(outdoc, src), 'wb')
        f.write(indoc.get_part(src))
        f.close()
    width, height = frame.get_size()
    width = Unit(width).convert('px')
    height = Unit(height).convert('px')
    text = plugin.get_text_content() # XXX get_svg_title?
    mimetype = plugin.get_attribute('draw:mime-type')
    outdoc.write('''<div class="plugin">
  <object data="%(src)s" type="%(mimetype)s" width="%(width)s"
    height="%(height)s">
    <param name="src" value="%(src)s"/>
    <param name="autoplay" value="false"/>
    <param name="autoStart" value="0"/>
    %(text)s
  </object>
</div>\n''' % {'src': src, 'mimetype': mimetype, 'width': width,
        'height': height, 'text': text})



def write_presentation_para(para, outdoc, encoding):
    # XXX lxml specific
    outdoc.write('<p>')
    outdoc.write(get_string(para.get_text(), encoding))
    for child in para.get_children():
        tag = child.get_tag()
        if tag == 'text:span':
            outdoc.write('<span>')
            outdoc.write(get_string(child.get_text(), encoding))
            for subchild in child.get_children():
                tag = subchild.get_tag()
                if tag == 'text:s':
                    outdoc.write('&nbsp;')
                    outdoc.write(get_string(subchild.get_tail(), encoding))
                elif tag == 'text:page-number':
                    # XXX
                    continue
                else:
                    print child.serialize()
                    raise NotImplementedError, tag
            outdoc.write('</span>')
            outdoc.write(get_string(child.get_tail(), encoding))
        else:
            print para.serialize()
            raise NotImplementedError, tag
    text = get_string(para.get_text(recursive=True), encoding)
    outdoc.write('</p>\n')



def write_presentation_list(liste, outdoc, encoding):
    outdoc.write('<ul>\n')
    for item in liste.get_children():
        tag = item.get_tag()
        if tag == 'text:list-header':
            for child in item.get_children():
                tag = child.get_tag()
                if tag == 'text:list':
                    write_presentation_list(child, outdoc, encoding)
                elif tag == 'text:p':
                    write_presentation_para(child, outdoc, encoding)
                else:
                    print item.serialize()
                    raise NotImplementedError, tag
            continue
        elif tag != 'text:list-item':
            raise NotImplementedError, tag
        outdoc.write('<li>\n')
        for child in item.get_children():
            tag = child.get_tag()
            if tag == 'text:list':
                write_presentation_list(child, outdoc, encoding)
            elif tag == 'text:p':
                write_presentation_para(child, outdoc, encoding)
            else:
                print item.serialize()
                raise NotImplementedError, tag
        outdoc.write('</li>\n')
    outdoc.write('</ul>\n')



def write_presentation_text(frame, outdoc, encoding):
    text_box = frame.get_element('draw:text-box')
    if text_box is None:
        text_box = frame
    for element in text_box.get_children():
        tag = element.get_tag()
        if tag == 'text:p':
            write_presentation_para(element, outdoc, encoding)
        elif tag == 'text:list':
            write_presentation_list(element, outdoc, encoding)
        elif tag == 'draw:enhanced-geometry':
            continue
        else:
            print text_box.serialize()
            raise NotImplementedError, tag



def cmp_frames(a, b):
    # XXX obsolete if "get_position" returns Unit
    ax, ay = a.get_position()
    ax = Unit(ax)
    ay = Unit(ay)
    bx, by = b.get_position()
    bx = Unit(bx)
    by = Unit(by)
    # Top-bottom then left-right
    return cmp((ay, ax), (by, bx))



def presentation_to_html(indoc, outdoc, encoding='utf-8'):
    # Header
    write_presentation_header(indoc, outdoc, encoding)
    # Pages
    body = indoc.get_body()
    for page in body.get_draw_pages():
        outdoc.write('<div class="slide">\n')
        frames = page.get_frames()
        # Add shapes because they contain text
        frames += page.get_shapes()
        # Sort by position
        for frame in sorted(frames, cmp=cmp_frames):
            presentation_class = frame.get_presentation_class()
            if presentation_class in ('title', 'subtitle'):
                write_presentation_title(frame, outdoc, encoding)
            elif presentation_class == 'notes':
                # XXX really?
                continue
            else:
                table = frame.get_table()
                image = frame.get_image()
                plugin = frame.get_element('draw:plugin')
                if table is not None:
                    write_presentation_table(frame, outdoc, encoding)
                elif image is not None:
                    write_presentation_image(frame, indoc, outdoc, encoding)
                elif plugin is not None:
                    write_presentation_plugin(frame, indoc, outdoc, encoding)
                else:
                    write_presentation_text(frame, outdoc, encoding)
        outdoc.write('</div>\n\n')
    # Footer
    write_presentation_footer(indoc, outdoc, encoding)



def get_extension(filename):
    root, ext = splitext(filename)
    # Remove the leading dot
    return ext[1:]



if  __name__ == '__main__':
    # Options initialisation
    usage = ("%prog [options] <input.ods> <output.odt>\n"
      "       %prog [options] <input.ods> <output.csv>\n"
      "       %prog [options] <input.ods> <output.rst>\n"
      "       %prog [options] <input.odt> <output.txt>\n"
      "       %prog [options] <input.odt> <output.rst>\n"
      "       %prog [options] <input.rst> <output.odt>\n"
      "       %prog [options] <input.odp> <output.html>")
    description = ("Convert an OpenDocument to another format. Possible "
            "combinations: ODS to ODT (tables and styles), ODS to CSV (only "
            "the first tab), ODS to RST, ODP to HTML (S5 format), and "
            "RST <=> ODT (RST = reStructuredText format)")
    parser = OptionParser(usage, version=__version__, description=description)
    # --styles
    help = "import the styles from the given file"
    parser.add_option("-s", "--styles", dest="styles_from", metavar="FILE",
            help=help)
    # Parse !
    options, args = parser.parse_args()
    # Container
    if len(args) != 2:
        parser.print_help()
        exit(1)
    # Open input document
    infile = args[0]
    extension = get_extension(infile)
    if extension == 'rst':
        indoc = open(infile, 'rb').read()
        intype = 'rst'
    else:
        indoc = odf_get_document(infile)
        intype = indoc.get_type()
    # Open output document
    outfile = args[1]
    extension = get_extension(outfile)
    if extension in ('csv', 'html', 'rst', 'txt'):
        outdoc = open(outfile, 'wb')
        outtype = extension
    else:
        if options.styles_from:
            outdoc = odf_get_document(options.styles_from).clone()
            outdoc.get_body().clear()
            outdoc.path = outfile
            outtype = outdoc.get_type()
        else:
            try:
                mimetype = ODF_EXTENSIONS[extension]
            except KeyError:
                raise ValueError, ("output filename not recognized: " +
                                   extension)
            outtype = mimetype[mimetype.rindex('.') + 1:]
            if '-template' in outtype:
                outtype = mimetype[mimetype.rindex('-') + 1:]
            outdoc = odf_new_document(outtype)
    # Convert function
    converter = locals().get('%s_to_%s' % (intype, outtype))
    if converter is None:
        raise NotImplementedError, "unsupported combination"
    # Remove output file
    check_target_file(outfile)
    # Convert!
    converter(indoc, outdoc)
    if isinstance(outdoc, odf_document):
        outdoc.save(outfile)
    else:
        outdoc.close()
