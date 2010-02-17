#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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

# Import from the Standard Library
from distutils import core
from os import listdir
from os.path import join
from sys import executable

# Import from lpod
from release import has_git, get_release, get_git_files


if has_git():
    # Make the version.txt file
    release = get_release()
    open('version.txt', 'w').write(release)
    # Make the MANIFEST file and search for the data
    filenames = get_git_files()
    filenames = [ name for name in filenames if not name.startswith('test') ]
    filenames.extend(['MANIFEST', 'version.txt'])
    open('MANIFEST', 'w').write('\n'.join(filenames))
else:
    release = open('version.txt').read().strip()
    filenames = [ line.strip() for line in open('MANIFEST') ]

# Find all non-Python source
data_files = [ name for name in filenames if not name.endswith('.py') ]

# Find all the scripts => It's easy: all the files in scripts/
scripts = [ join('scripts', filename) for filename in listdir('scripts') ]
scripts = [ name for name in scripts if name in filenames ]

# Make the python_path.txt file
open('python_path.txt', 'w').write(executable)

# And call core.setup ....
core.setup(description='lpOD Library',
           license='GPLv3 + Apache',
           name='lpod-python',
           package_data={'lpod': data_files},
           package_dir={'lpod': ''},
           scripts=scripts,
           packages=['lpod'],
           url='http://www.lpod-project.org/',
           version=release,
           author="lpOD Team",
           author_email="team@lpod-project.org")
