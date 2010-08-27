# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
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

# Types and their default template
ODF_TYPES = {
        'text': 'templates/text.ott',
        'spreadsheet': 'templates/spreadsheet.ots',
        'presentation': 'templates/presentation.otp',
        # Follow the spec
        'drawing': 'templates/drawing.otg',
        # Follow the mimetype
        'graphics': 'templates/drawing.otg',
        # TODO
        #'chart': 'templates/chart.otc',
        #'image': 'templates/image.oti',
        #'formula': 'templates/image.otf',
        #'master': 'templates/image.odm',
        #'web': 'templates/image.oth',
}


ODF_TEXT = 'application/vnd.oasis.opendocument.text'
ODF_TEXT_TEMPLATE = 'application/vnd.oasis.opendocument.text-template'
ODF_SPREADSHEET = 'application/vnd.oasis.opendocument.spreadsheet'
ODF_SPREADSHEET_TEMPLATE = 'application/vnd.oasis.opendocument.spreadsheet-template'
ODF_PRESENTATION = 'application/vnd.oasis.opendocument.presentation'
ODF_PRESENTATION_TEMPLATE = 'application/vnd.oasis.opendocument.presentation-template'
ODF_DRAWING = 'application/vnd.oasis.opendocument.graphics'
ODF_DRAWING_TEMPLATE = 'application/vnd.oasis.opendocument.graphics-template'
ODF_CHART = 'application/vnd.oasis.opendocument.chart'
ODF_CHART_TEMPLATE = 'application/vnd.oasis.opendocument.chart-template'
ODF_IMAGE = 'application/vnd.oasis.opendocument.image'
ODF_IMAGE_TEMPLATE = 'application/vnd.oasis.opendocument.image-template'
ODF_FORMULA = 'application/vnd.oasis.opendocument.formula'
ODF_FORMULA_TEMPLATE = 'application/vnd.oasis.opendocument.formula-template'
ODF_MASTER = 'application/vnd.oasis.opendocument.text-master'
ODF_WEB = 'application/vnd.oasis.opendocument.text-web'


# File extensions and their mimetype
ODF_EXTENSIONS = {
        'odt': ODF_TEXT,
        'ott': ODF_TEXT_TEMPLATE,
        'ods': ODF_SPREADSHEET,
        'ots': ODF_SPREADSHEET_TEMPLATE,
        'odp': ODF_PRESENTATION,
        'otp': ODF_PRESENTATION_TEMPLATE,
        'odg': ODF_DRAWING,
        'otg': ODF_DRAWING_TEMPLATE,
        'odc': ODF_CHART,
        'otc': ODF_CHART_TEMPLATE,
        'odi': ODF_IMAGE,
        'oti': ODF_IMAGE_TEMPLATE,
        'odf': ODF_FORMULA,
        'otf': ODF_FORMULA_TEMPLATE,
        'odm': ODF_MASTER,
        'oth': ODF_WEB,
}


# Mimetypes and their file extension
ODF_MIMETYPES = {
        ODF_TEXT: 'odt',
        ODF_TEXT_TEMPLATE: 'ott',
        ODF_SPREADSHEET: 'ods',
        ODF_SPREADSHEET_TEMPLATE: 'ots',
        ODF_PRESENTATION: 'odp',
        ODF_PRESENTATION_TEMPLATE: 'otp',
        ODF_DRAWING: 'odg',
        ODF_DRAWING_TEMPLATE: 'otg',
        ODF_CHART: 'odc',
        ODF_CHART_TEMPLATE: 'otc',
        ODF_IMAGE: 'odi',
        ODF_IMAGE_TEMPLATE: 'oti',
        ODF_FORMULA: 'odf',
        ODF_FORMULA_TEMPLATE: 'otf',
        ODF_MASTER: 'odm',
        ODF_WEB: 'oth',
}


# Standard parts in the container (other are regular paths)
ODF_PARTS = ('content', 'meta', 'settings', 'styles')


# Presentation classes (for layout)
ODF_CLASSES = ('title', 'outline', 'subtitle', 'text', 'graphic', 'object',
        'chart', 'table', 'orgchart', 'page', 'notes', 'handout')
