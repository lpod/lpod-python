# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import register_element_class, odf_element


class odf_tracked_changes(odf_element):

    def get_changed_region_list(self, creator=None, date=None, regex=None):
        changed_regions = self.get_element_list('text:changed-region')
        # Filer by creator
        if creator is not None:
            filter = []
            for region in changed_regions:
                if creator == region.get_dc_creator():
                    filter.append(region)
            changed_regions = filter
        # Filer by date
        if date is not None:
            filter = []
            for region in changed_regions:
                if date == region.get_dc_date():
                    filter.append(region)
            changed_regions = filter
        # Filter by regex
        if regex is not None:
            changed_regions = [region for region in changed_regions
                                      if region.match(regex)]
        return changed_regions


    def get_changed_region(self, creator=None, date=None, regex=None):
        changed_regions = self.get_changed_region_list(creator=creator,
                                                       date=date, regex=None)
        if changed_regions:
            return changed_regions[0]
        return None


    def get_changed_region_by_id(self, id):
        return self.get_element("text:changed-region[@text:id = '%s']" % id)


    def get_changed_region_by_creator(self, creator):
        return self.get_changed_region(creator=creator)


    def get_changed_region_by_date(self, date):
        return self.get_changed_region(date=date)


    def get_changed_region_by_content(self, regex):
        return self.get_changed_region(regex=regex)



register_element_class('text:tracked-changes', odf_tracked_changes)
