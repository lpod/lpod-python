# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
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

# Import from lpod
from element import register_element_class, odf_element
from utils import _get_elements, _get_element, obsolete


class odf_tracked_changes(odf_element):

    def get_changed_regions(self, creator=None, date=None, content=None):
        return _get_elements(self, 'text:changed-region', dc_creator=creator,
                dc_date=date, content=content)

    get_changed_region_list = obsolete('get_changed_region_list',
            get_changed_regions)


    def get_changed_region(self, position=0, text_id=None, creator=None,
            date=None, content=None):
        return _get_element(self, 'text:changed-region', position,
                text_id=text_id, dc_creator=creator, dc_date=date,
                content=content)



register_element_class('text:tracked-changes', odf_tracked_changes)
