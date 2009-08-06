# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from utils import _get_abspath

try:
    __version__ = open(_get_abspath('version.txt')).read().strip()
except:
    __version__ = None

__installation_path__ = _get_abspath('')


# Register element classes
import draw_page
import heading
import list
import paragraph
import style
