# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Luis Belmar-Letelier <luis@itaapy.com>
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

# Import from the Standard Library
from cStringIO import StringIO
from ftplib import FTP
from unittest import TestCase, main
from urllib2 import urlopen

# Import from lpod
from lpod.const import ODF_EXTENSIONS, ODF_CONTENT, ODF_MANIFEST, ODF_META
from lpod.const import ODF_STYLES
from lpod.content import odf_content
from lpod.document import odf_new_document, odf_get_document
from lpod.manifest import odf_manifest
from lpod.meta import odf_meta
from lpod.styles import odf_styles


class NewDocumentFromTemplateTestCase(TestCase):

    def test_bad_template(self):
        self.assertRaises(IOError, odf_new_document,
                '../templates/notexisting')

    def test_text_template(self):
        path = '../templates/text.ott'
        self.assert_(odf_new_document(path))


    def test_spreadsheet_template(self):
        path = '../templates/spreadsheet.ots'
        self.assert_(odf_new_document(path))


    def test_presentation_template(self):
        path = '../templates/presentation.otp'
        self.assert_(odf_new_document(path))


    def test_drawing_template(self):
        path = '../templates/drawing.otg'
        self.assert_(odf_new_document(path))


    def test_mimetype(self):
        path = '../templates/drawing.otg'
        document = odf_new_document(path)
        mimetype = document.get_part('mimetype')
        self.assertFalse('template' in mimetype)
        manifest = document.get_part(ODF_MANIFEST)
        media_type = manifest.get_media_type('/')
        self.assertFalse('template' in media_type)



class NewdocumentFromTypeTestCase(TestCase):

    def test_bad_type(self):
        self.assertRaises(IOError, odf_new_document, 'foobar')


    def test_text_type(self):
        document = odf_new_document('text')
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odt'])


    def test_spreadsheet_type(self):
        document = odf_new_document('spreadsheet')
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['ods'])


    def test_presentation_type(self):
        document = odf_new_document('presentation')
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odp'])


    def test_drawing_type(self):
        document = odf_new_document('drawing')
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odg'])



class GetDocumentTestCase(TestCase):

    def test_filesystem(self):
        path = 'samples/example.odt'
        self.assert_(odf_get_document(path))


    def test_odf_xml(self):
        path = 'samples/example.xml'
        self.assert_(odf_get_document(path))


    def test_http(self):
        file = urlopen('http://ftp.lpod-project.org/example.odt')
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odt'])


    def test_ftp(self):
        ftp = FTP('ftp.lpod-project.org')
        ftp.login()
        file = StringIO()
        ftp.retrbinary('RETR example.odt', file.write)
        ftp.quit()
        file.seek(0)
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odt'])



class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = odf_get_document('samples/example.odt')


    def test_get_mimetype(self):
        mimetype = self.document.get_mimetype()
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])

    def test_get_content(self):
        content = self.document.get_part(ODF_CONTENT)
        self.assert_(type(content) is odf_content)


    def test_get_meta(self):
        meta = self.document.get_part(ODF_META)
        self.assert_(type(meta) is odf_meta)


    def test_get_styles(self):
        styles = self.document.get_part(ODF_STYLES)
        self.assert_(type(styles) is odf_styles)


    def test_get_manifest(self):
        manifest = self.document.get_part(ODF_MANIFEST)
        self.assert_(type(manifest) is odf_manifest)


    def test_get_body(self):
        body = self.document.get_body()
        self.assertEqual(body.get_tag(), 'office:text')


    def test_clone(self):
        document = self.document
        document.get_part(ODF_CONTENT)
        self.assertNotEqual(document._odf_document__xmlparts, {})
        clone = document.clone()
        self.assertNotEqual(clone._odf_document__xmlparts, {})
        parts = clone._odf_document__xmlparts
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts.keys(), ['content.xml'])
        container = clone.container
        self.assertEqual(container.path, None)


    def test_save_nogenerator(self):
        document = self.document
        temp = StringIO()
        document.save(temp)
        temp.seek(0)
        new = odf_get_document(temp)
        generator = new.get_part(ODF_META).get_generator()
        self.assert_(generator.startswith(u"lpOD Python"))


    def test_save_generator(self):
        document = self.document.clone()
        document.get_part(ODF_META).set_generator(u"toto")
        temp = StringIO()
        document.save(temp)
        temp.seek(0)
        new = odf_get_document(temp)
        generator = new.get_part(ODF_META).get_generator()
        self.assertEqual(generator, u"toto")



class TestStyle(TestCase):

    def setUp(self):
        self.document = odf_get_document('../templates/lpod_styles.odt')


    def test_get_style_list(self):
        document = self.document
        styles = document.get_style_list()
        self.assertEqual(len(styles), 73)


    def test_get_style_list_family_paragraph(self):
        document = self.document
        styles = document.get_style_list(family='paragraph')
        self.assertEqual(len(styles), 33)


    def test_get_style_list_family_text(self):
        document = self.document
        styles = document.get_style_list(family='text')
        self.assertEqual(len(styles), 4)


    def test_get_style_list_family_graphic(self):
        document = self.document
        styles = document.get_style_list(family='graphic')
        self.assertEqual(len(styles), 1)


    def test_get_style_list_family_page_layout(self):
        document = self.document
        styles = document.get_style_list(family='page-layout')
        self.assertEqual(len(styles), 2)


    def test_get_style_list_family_master_page(self):
        document = self.document
        styles = document.get_style_list(family='master-page')
        self.assertEqual(len(styles), 2)


    def test_get_style_automatic(self):
        document = self.document
        style = document.get_style('paragraph', u'P1')
        self.assertNotEqual(style, None)


    def test_get_style_named(self):
        document = self.document
        style = document.get_style('paragraph', u'Heading_20_1')
        self.assertNotEqual(style, None)


    def test_show_styles(self):
        # XXX hard to unit test
        document = self.document
        all_styles = document.show_styles()
        self.assert_(u"auto   used:" in all_styles)
        self.assert_(u"common used:" in all_styles)
        common_styles = document.show_styles(automatic=False)
        self.assert_(u"auto   used:" not in common_styles)
        self.assert_(u"common used:" in common_styles)
        automatic_styles = document.show_styles(common=False)
        self.assert_(u"auto   used:" in automatic_styles)
        self.assert_(u"common used:" not in automatic_styles)
        no_styles = document.show_styles(automatic=False, common=False)
        self.assertEqual(no_styles, u"")



if __name__ == '__main__':
    main()
