#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from sys import argv
from os.path import basename, exists

# Import from lpod
from scriptutils import printerr


try:
    # builtin on Windows
    WindowsError
except NameError:
    class WindowsError(OSError):
        pass


def _run_command(command):
    popen = Popen(command, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = popen.communicate()
    if popen.returncode != 0 or stderrdata:
        raise ValueError
    return stdoutdata



def has_git():
    if not exists('.git'):
        return False
    try:
        _run_command(['git', 'branch'])
    except (ValueError, OSError, WindowsError):
        return False
    return True



def get_release():
    # XXX do it in one git command
    output = _run_command(['git', 'branch'])
    for line in output.splitlines():
        if line.startswith('*'):
            branch = line[2:]
            break
    output = _run_command(['git', 'describe',  '--tags']).strip()
    if not '-' in output:
        return output
    version, delta, sha = output.split('-')
    if branch == 'master':
        return '-'.join((version, delta, sha))
    return '-'.join((branch, version, delta, sha))



def get_git_files():
    files = _run_command(['git', 'ls-files'])
    return [ name.strip() for name in files.splitlines() ]



if __name__ == '__main__':
    try:
        print get_release()
    except:
        printerr('%s: unable to read info' % basename(argv[0]))


