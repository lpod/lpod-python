# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

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
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_create_line(self):
        page = odf_create_draw_page(u'Page')
        line = odf_create_line(p1=('2cm', '2cm'), p2=('1cm', '1cm'))
        page.append_element(line)
        expected = ('<draw:page draw:name="Page">\n'
                    '  <draw:line svg:x1="2cm" svg:y1="2cm" svg:x2="1cm" '
                    'svg:y2="1cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_rectangle(self):
        page = odf_create_draw_page(u'Page')
        rectangle = odf_create_rectangle(size=('2cm', '1cm'), position=('3cm',
        '4cm'))
        page.append_element(rectangle)
        expected = ('<draw:page draw:name="Page">\n'
                    '  <draw:rect svg:width="2cm" svg:height="1cm" svg:x="3cm"'
                    ' svg:y="4cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_ellipse(self):
        page = odf_create_draw_page(u'Page')
        svg_attrs = {
            'svg:width': '2cm',
            'svg:height': '2cm',
            'svg:x': '2cm',
            'svg:y': '2cm'}
        ellipse = odf_create_ellipse(size=('2cm', '1cm'), position=('3cm',
        '4cm'))
        page.append_element(ellipse)
        expected = ('<draw:page draw:name="Page">\n'
                    '  <draw:ellipse svg:width="2cm" svg:height="1cm" '
                    'svg:x="3cm" svg:y="4cm"/>\n'
                    '</draw:page>\n')
        self.assertEqual(page.serialize(pretty=True), expected)


    def test_create_connector(self):
        page = odf_create_draw_page(u'Page')
        rectangle = odf_create_rectangle(size=('2cm', '1cm'),
                                         position=('3cm', '4cm'),
                                         shape_id='rectangle')
        ellipse = odf_create_ellipse(size=('2cm', '1cm'),
                                     position=('3cm', '4cm'),
                                     shape_id='ellipse')
        connector = odf_create_connector(connected_shapes=(rectangle, ellipse),
                                         glue_points=(1, 2))
        page.append_element(rectangle)
        page.append_element(ellipse)
        page.append_element(connector)
        expected = ('<draw:page draw:name="Page">\n'
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
        page = body.get_draw_page_by_position(1)
        lines = page.get_draw_line_list()
        self.assertEqual(len(lines), 2)


    def test_get_draw_line_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        lines = page.get_draw_line_list(regex=ur'èche*')
        self.assertEqual(len(lines), 1)


    def test_get_draw_line_list_style(self):
        # XXX Fail until draw:style-name is supported
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        lines = page.get_draw_line_list(style=ur'gr2')
        self.assertEqual(len(lines), 1)


    def test_get_draw_line_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        line = page.get_draw_line_by_content(ur'Ligne')
        expected = ('<draw:line draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:layer="layout" '
                    'svg:x1="3.5cm" svg:y1="2.5cm" svg:x2="10.5cm" '
                    'svg:y2="12cm">\n'
                    '     <text:p text:style-name="P1">Ligne</text:p>\n'
                    '    </draw:line>\n')
        self.assertEqual(line.serialize(pretty=True), expected)

    #
    # Rectangles
    #

    def test_get_draw_rectangle_list(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        rectangles = page.get_draw_rectangle_list()
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        rectangles = page.get_draw_rectangle_list(regex=ur'angle')
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_list_style(self):
        # XXX Fail until draw:style-name is supported
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        rectangles = page.get_draw_rectangle_list(style=ur'gr1')
        self.assertEqual(len(rectangles), 1)


    def test_get_draw_rectangle_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        rectangle = page.get_draw_rectangle_by_content(ur'Rect')
        expected = ('<draw:rect draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:id="id1" '
                    'draw:layer="layout" svg:width="6cm" svg:height="7cm" '
                    'svg:x="5cm" svg:y="4.5cm">\n'
                    '     <text:p text:style-name="P1">Rectangle</text:p>\n'
                    '    </draw:rect>\n')
        self.assertEqual(rectangle.serialize(pretty=True), expected)

    #
    # Ellipses
    #

    def test_get_draw_ellipse_list(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        ellipses = page.get_draw_ellipse_list()
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        ellipses = page.get_draw_ellipse_list(regex=ur'rcle')
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_list_style(self):
        # XXX Fail until draw:style-name is supported
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        ellipses = page.get_draw_ellipse_list(style=ur'gr2')
        self.assertEqual(len(ellipses), 1)


    def test_get_draw_ellipse_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        ellipse = page.get_draw_ellipse_by_content(ur'Cerc')
        expected = ('<draw:ellipse draw:style-name="gr1" '
                    'draw:text-style-name="P1" draw:id="id2" '
                    'draw:layer="layout" svg:width="4cm" svg:height="3.5cm" '
                    'svg:x="13.5cm" svg:y="5cm">\n'
                    '     <text:p text:style-name="P1">Cercle</text:p>\n'
                    '    </draw:ellipse>\n')
        self.assertEqual(ellipse.serialize(pretty=True), expected)

    #
    # Connectors
    #

    def test_get_draw_connector_list(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        connectors = page.get_draw_connector_list()
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_list_regex(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        connectors = page.get_draw_connector_list(regex=ur'Con')
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_list_style(self):
        # XXX Fail until draw:style-name is supported
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        connectors = page.get_draw_connector_list(style=ur'gr4')
        self.assertEqual(len(connectors), 1)


    def test_get_draw_connector_by_content(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        connector = page.get_draw_connector_by_content(ur'ecteur')
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


    def test_get_draw_orphans_connector(self):
        body = self.content.get_body()
        page = body.get_draw_page_by_position(1)
        orphan_connector = odf_create_connector()
        orphan_connector.append_element(odf_create_paragraph(u'Orphan c'))
        body.append_element(orphan_connector)
        connectors = body.get_draw_orphans_connectors()
        self.assertEqual(len(connectors), 1)



if __name__ == '__main__':
    main()
