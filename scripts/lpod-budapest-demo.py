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
from sys import exit, stderr
from urllib2 import urlopen, HTTPPasswordMgrWithDefaultRealm
from urllib2 import HTTPBasicAuthHandler, build_opener
from urlparse import urlsplit, urlunsplit

# Import from lpod
from lpod import __version__, ODF_META, ODF_STYLES, ODF_MANIFEST
from lpod.document import odf_new_document, odf_get_document
from lpod.draw_page import odf_create_draw_page
from lpod.frame import odf_create_frame
from lpod.list import odf_create_list
from lpod.scriptutils import add_option_output, check_target_file
from lpod.scriptutils import printerr, printinfo, printwarn


def get_frame(presentation_class, position, size,
        master_page):
    return odf_create_frame(position=position, size=size,
            presentation_class=presentation_class, layer="layout")



def get_title_frame(master_page):
    position = ('1.90cm', '2.54cm')
    size = ('19.47cm', '3.18cm')
    return get_frame("title", position, size, master_page)



def get_outline_frame(master_page):
    position = ('1.90cm', '6.14cm')
    size = ('12.60cm', '11.59cm')
    return get_frame("outline", position, size, master_page)



def get_graphic_frame(master_page):
    position = ('15.30cm', '6.14cm')
    size = ('8.55cm', '11.59cm')
    return get_frame("graphic", position, size, master_page)



if  __name__ == '__main__':
    # Options initialisation
    usage = "%prog -o FILE <file1> [<file2> ...]"
    description = "Catalog all input files in a presentation"
    parser = OptionParser(usage, version=__version__,
            description=description)
    # --output
    add_option_output(parser, complement='("-" for stdout)')

    # Parse !
    options, filenames = parser.parse_args()

    # Arguments
    if not filenames:
        parser.print_help()
        exit(1)
    target = options.output
    if target is None:
        printerr('"-o" option mandatory (use "-" to print to stdout)')
        exit(1)
    check_target_file(target)

    output_document = odf_new_document('presentation')
    output_meta = output_document.get_part(ODF_META)
    output_meta.set_title(u"Interop Budapest Demo")

    # Styles
    styles = output_document.get_part(ODF_STYLES)
    first_master_page = styles.get_master_page()
    if first_master_page is None:
        raise ValueError, "no master page found"

    for i, filename in enumerate(filenames):
        # TODO folders and collections
        printinfo("Processing %s..." % filename)
        result = urlsplit(filename)
        scheme = result.scheme
        if not scheme:
            file = open(filename)
        elif result.username:
            if result.port:
                netloc = '%s:%s' % (result.hostname, result.port)
            else:
                netloc = result.hostname
            url = urlunsplit((scheme, netloc, result.path, result.query,
                result.fragment))
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, url, result.username,
                    result.password)
            handler = HTTPBasicAuthHandler(password_mgr)
            opener = build_opener(handler)
            file = opener.open(url)
        else:
            file = urlopen(filename)
        input_document = odf_get_document(file)
        # Page
        page = odf_create_draw_page(name=u"page%d" % (i + 1),
                master_page=first_master_page)
        # Title Frame
        title_frame = get_title_frame(first_master_page)
        name = unicode(filename.split('/')[-1])
        source = u"filesystem" if not scheme else scheme
        title_frame.set_text_content(u"%s (%s)" % (name, source))
        page.append(title_frame)
        # Get info
        info = []
        input_meta = input_document.get_part(ODF_META)
        info.append(u"Title: %s" % input_meta.get_title())
        stats = input_meta.get_statistic()
        info.append(u"# pages: %s" % stats['meta:page-count'])
        input_body = input_document.get_body()
        info.append(u"# images: %s" % len(input_body.get_images()))
        info.append(u"# tables: %s" % len(input_body.get_tables()))
        # Outline Frame
        info_list = odf_create_list(info)
        outline_frame = get_outline_frame(first_master_page)
        outline_frame.set_text_content(info_list)
        page.append(outline_frame)
        # Graphic Frame
        first_image = input_body.get_image(1)
        if not first_image:
            first_image = input_body.get_image(0)
        sibling = (first_image is not None
                and first_image.get_prev_sibling() or None)
        if sibling is not None and sibling.get_tag() == 'draw:object-ole':
            # TODO in lpOD
            first_image = None
        if first_image is None:
            printwarn('no image found in "%s"' % filename, indent=2)
            continue
        input_href = first_image.get_href()
        part = input_document.get_part(input_href)
        try:
            output_document.get_part(input_href)
        except KeyError:
            output_href = input_href
        else:
            # XXX Quick & dirty
            output_href = "%s-1" % input_href
        output_document.set_part(output_href, part)
        input_manifest = input_document.get_part(ODF_MANIFEST)
        media_type = input_manifest.get_media_type(input_href)
        output_manifest = output_document.get_part(ODF_MANIFEST)
        output_manifest.add_full_path(output_href, media_type)
        graphic_frame = get_graphic_frame(first_master_page)
        graphic_frame.append(first_image)
        page.append(graphic_frame)
        output_body = output_document.get_body()
        output_body.append(page)

    output_document.save(target, pretty=True)
    print >> stderr
    print >> stderr,  "%s generated" % target
