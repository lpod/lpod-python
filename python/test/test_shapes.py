# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.draw_page import odf_create_draw_page
from lpod.shapes import odf_create_line, odf_create_rectangle
from lpod.shapes import odf_create_ellipse, odf_create_connector



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



if __name__ == '__main__':
    main()
