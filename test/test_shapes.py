# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.draw_page import odf_create_draw_page
from lpod.paragraph import odf_create_paragraph
from lpod.shapes import odf_create_ellipse, odf_create_connector
from lpod.shapes import odf_create_line, odf_create_rectangle



class TestShapes(TestCase):

    def setUp(self):
        self.document = document = odf_get_document('samples/base_shapes.odg')
        self.content = document.get_part('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_line(self):
        page = odf_create_draw_page('Page1')
        line = odf_create_line(p1=('2cm', '2cm'), p2=('1cm', '1cm'))
        page.append(line)
        expected = ('<draw:page draw:id="Page1">\n'
                    '  <draw:line svg:x1="2cm" svg:y1="2cm" svg:x2="1cm" '
                    'svg:y2="1cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_rectangle(self):
        page = odf_create_draw_page('Page1')
        rectangle = odf_create_rectangle(size=('2cm', '1cm'),
                                         position=('3cm', '4cm'))
        page.append(rectangle)
        expected = ('<draw:page draw:id="Page1">\n'
                    '  <draw:rect svg:width="2cm" svg:height="1cm" svg:x="3cm"'
                    ' svg:y="4cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_ellipse(self):
        page = odf_create_draw_page('Page1')
        svg_attrs = {
            'svg:width': '2cm',
            'svg:height': '2cm',
            'svg:x': '2cm',
            'svg:y': '2cm'}
        ellipse = odf_create_ellipse(size=('2cm', '1cm'), position=('3cm',
        '4cm'))
        page.append(ellipse)
        expected = ('<draw:page draw:id="Page1">\n'
                    '  <draw:ellipse svg:width="2cm" svg:height="1cm" '
                    'svg:x="3cm" svg:y="4cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_connector(self):
        page = odf_create_draw_page('Page1')
        rectangle = odf_create_rectangle(size=('2cm', '1cm'),
                                         position=('3cm', '4cm'),
                                         shape_id='rectangle')
        ellipse = odf_create_ellipse(size=('2cm', '1cm'),
                                     position=('3cm', '4cm'),
                                     shape_id='ellipse')
        connector = odf_create_connector(connected_shapes=(rectangle,
                                                           ellipse),
                                         glue_points=(1, 2))
        page.append(rectangle)
        page.append(ellipse)
        page.append(connector)
        expected = ('<draw:page draw:id="Page1">\n'
                    '  <draw:rect draw:id="rectangle" svg:width="2cm" '
                    'svg:height="1cm" svg:x="3cm" svg:y="4cm"/>\n'
                    '  <draw:ellipse draw:id="ellipse" svg:width="2cm" '
                    'svg:height="1cm" svg:x="3cm" svg:y="4cm"/>\n'
                    '  <draw:connector draw:start-shape="rectangle" '
                    'draw:end-shape="ellipse" draw:start-glue-point="1" '
                    'draw:end-glue-point="2"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)

    #
    # Lines
    #

    def test_get_draw_line_list(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        lines = page.get_draw_lines()
        self.assertEqual(len(lines), 2)


    def test_get_draw_line_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        lines = page.get_draw_lines(content=ur'èche*')
        self.assertEqual(len(lines), 1)


    def test_get_draw_line_list_draw_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        lines = page.get_draw_lines(draw_style=ur'gr2')
        self.assertEqual(len(lines), 1)


    def test_get_draw_line_list_draw_text_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        lines = page.get_draw_lines(draw_text_style=ur'P1')
        self.assertEqual(len(lines), 2)


    def test_get_draw_line_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        line = page.get_draw_line(content=ur'Ligne')
        expected = ('<draw:line draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:layer="layout" '
                    'svg:x1="3.5cm" svg:y1="2.5cm" svg:x2="10.5cm" '
                    'svg:y2="12cm">\n'
                    '     <text:p text:style-name="P1">Ligne</text:p>\n'
                    '    </draw:line>\n')
        self.assertEqual(line.serialize(pretty=True), expected)


    def test_get_draw_line_by_id(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        line = odf_create_line(shape_id=u'an id')
        page.append(line)
        line = page.get_draw_line(id=ur'an id')
        expected = '<draw:line draw:id="an id"/>\n'
        self.assertEqual(line.serialize(pretty=True), expected)

    #
    # Rectangles
    #

    def test_get_draw_rectangle_list(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles()
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(content=ur'angle')
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_list_draw_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(draw_style=ur'gr1')
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_list_draw_text_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangles = page.get_draw_rectangles(draw_text_style=ur'P1')
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangle = page.get_draw_rectangle(content=ur'Rect')
        expected = ('<draw:rect draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:id="id1" '
                    'draw:layer="layout" svg:width="6cm" svg:height="7cm" '
                    'svg:x="5cm" svg:y="4.5cm">\n'
                    '     <text:p text:style-name="P1">Rectangle</text:p>\n'
                    '    </draw:rect>\n')
        self.assertEqual(rectangle.serialize(pretty=True), expected)


    def test_get_draw_rectangle_by_id(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        rectangle = odf_create_rectangle(shape_id=u'an id')
        page.append(rectangle)
        rectangle = page.get_draw_rectangle(id=ur'an id')
        expected = ('<draw:rect draw:id="an id" svg:width="1cm" '
                    'svg:height="1cm"/>\n')
        self.assertEqual(rectangle.serialize(pretty=True), expected)

    #
    # Ellipses
    #

    def test_get_draw_ellipse_list(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses()
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(content=ur'rcle')
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_list_draw_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(draw_style=ur'gr1')
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_list_draw_text_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipses = page.get_draw_ellipses(draw_text_style=ur'P1')
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipse = page.get_draw_ellipse(content=ur'Cerc')
        expected = ('<draw:ellipse draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:id="id2" '
                    'draw:layer="layout" svg:width="4cm" svg:height="3.5cm" '
                    'svg:x="13.5cm" svg:y="5cm">\n'
                    '     <text:p text:style-name="P1">Cercle</text:p>\n'
                    '    </draw:ellipse>\n')
        self.assertEqual(ellipse.serialize(pretty=True), expected)


    def test_get_draw_ellipse_by_id(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        ellipse = odf_create_ellipse(shape_id=u'an id')
        page.append(ellipse)
        ellipse = page.get_draw_ellipse(id=ur'an id')
        expected = ('<draw:ellipse draw:id="an id" svg:width="1cm" '
                    'svg:height="1cm"/>\n')
        self.assertEqual(ellipse.serialize(pretty=True), expected)

    #
    # Connectors
    #

    def test_get_draw_connector_list(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connectors = page.get_draw_connectors()
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(content=ur'Con')
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_list_draw_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(draw_style=ur'gr4')
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_list_draw_text_style(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connectors = page.get_draw_connectors(draw_text_style=ur'P1')
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connector = page.get_draw_connector(content=ur'ecteur')
        expected = ('<draw:connector draw:style-name="gr4" '
                    'draw:text-style-name="P1" draw:layer="layout" '
                    'svg:x1="11cm" svg:y1="8cm" svg:x2="15.5cm" '
                    'svg:y2="8.5cm" draw:start-shape="id1" '
                    'draw:start-glue-point="1" draw:end-shape="id2" '
                    'draw:end-glue-point="2" '
                    'svg:d="m11000 8000h1250v1001h3250v-501">\n'
                    '     <text:p text:style-name="P1">Connecteur</text:p>\n'
                    '    </draw:connector>\n')
        self.assertEqual(connector.serialize(pretty=True), expected)


    def test_get_draw_connector_by_id(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        connector = odf_create_connector(shape_id=u'an id')
        page.append(connector)
        connector = page.get_draw_connector(id=ur'an id')
        expected = '<draw:connector draw:id="an id"/>\n'
        self.assertEqual(connector.serialize(pretty=True), expected)


    def test_get_draw_orphans_connector(self):
        body = self.content.get_body()
        page = body.get_draw_page()
        orphan_connector = odf_create_connector()
        orphan_connector.append(odf_create_paragraph(u'Orphan c'))
        body.append(orphan_connector)
        connectors = body.get_orphan_draw_connectors()
        self.assertEqual(len(connectors), 1)



if __name__ == '__main__':
    main()
