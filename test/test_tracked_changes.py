# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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
from datetime import datetime

# Import from lpod
from lpod.document import odf_get_document


class TestTrackedChanges(TestCase):

    def setUp(self):
        file = 'samples/tracked_changes.odt'
        self.document = document = odf_get_document(file)
        self.content = document.get_content()


    def tearDown(self):
        del self.content
        del self.document


    def test_get_tracked_changes(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        expected = ('<text:tracked-changes>\n'
                    '    <text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T19:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n'
                    '    <text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Herv&#233; Cauwelier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n'
                    '    <text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n'
                    '   </text:tracked-changes>\n')
        self.assertEqual(tracked_changes.serialize(pretty=True), expected)


    def test_get_changed_region_list(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        regions = tracked_changes.get_changed_region_list()
        self.assertEqual(len(regions), 3)


    def test_get_changed_region_list_creator(self):
        creator = 'Romain Gauthier'
        content = self.content
        tracked_changes = content.get_tracked_changes()
        regions = tracked_changes.get_changed_region_list(creator=creator)
        expected = ('<text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T19:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_list_date(self):
        date = datetime(2009, 8, 21, 17, 27, 00)
        content = self.content
        tracked_changes = content.get_tracked_changes()
        regions = tracked_changes.get_changed_region_list(date=date)
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_list_regex(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        regions = tracked_changes.get_changed_region_list(regex=ur'amis')
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_by_id(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        region = tracked_changes.get_changed_region_by_id('ct-1371898680')
        expected = ('<text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Herv&#233; Cauwelier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_creator(self):
        creator = 'David Versmisse'
        content = self.content
        tracked_changes = content.get_tracked_changes()
        region = tracked_changes.get_changed_region_by_creator(creator)
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_date(self):
        date = datetime(2009, 8, 21, 18, 27, 00)
        content = self.content
        tracked_changes = content.get_tracked_changes()
        region = tracked_changes.get_changed_region_by_date(date)
        expected = ('<text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Herv&#233; Cauwelier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_content(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        region = tracked_changes.get_changed_region_by_content(ur'les')
        expected = ('<text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T19:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changes_ids(self):
        content = self.content
        body = content.get_body()
        paragraph = body.get_paragraph_by_content(ur'Bonjour')
        changes_ids = paragraph.get_changes_ids()
        expected = ['ct-1371898904', 'ct-1371898680', 'ct-1371898456']
        self.assertEqual(changes_ids, expected)



if __name__ == '__main__':
    main()
