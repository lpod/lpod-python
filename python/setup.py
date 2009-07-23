# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from distutils import core
from sys import executable

# Import from lpod
from release import get_release, get_git_files



# Make the version.txt file
release = get_release()
open('version.txt', 'w').write(release)

# Make the MANIFEST file and search for the data
filenames = get_git_files()
filenames.remove('.gitignore')
filenames.extend(['MANIFEST', 'version.txt'])
filenames = [ name for name in filenames if not name.startswith('test') ]
open('MANIFEST', 'w').write('\n'.join(filenames))
data_files = [ name for name in filenames if not name.endswith('.py') ]

# Make the python_path.txt file
open('python_path.txt', 'w').write(executable)

# And call core.setup ....
core.setup(description = 'lpOD Library',
           license = 'GNU Lesser General Public License (LGPL)',
           name = 'lpod',
           package_data = {'lpod': data_files},
           package_dir = {'lpod': ''},
           packages = ['lpod'],
           url = 'http://www.lpod-project.org/',
           version = release)

