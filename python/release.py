#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
from subprocess import Popen, PIPE
from sys import stderr, argv
from datetime import datetime
from os.path import basename


def _run_command(command):
    popen = Popen(command, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = popen.communicate()
    if popen.returncode != 0 or stderrdata:
        raise ValueError
    return stdoutdata



def has_git():
    try:
        probe = _run_command(['git', 'branch'])
    except ValueError:
        return False
    return True



def get_release():
    output = _run_command(['git', 'describe',  '--tags', '--long'])
    return output.strip()



def get_git_files():
    files = _run_command(['git', 'ls-files'])
    return [ name.strip() for name in files.splitlines() ]



if __name__ == '__main__':
    try:
        print get_release()
    except:
        print>>stderr, '%s: error: unable to read info' % basename(argv[0])


