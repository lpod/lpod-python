#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

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



def get_date():
    date = _run_command(['git', 'log', '--pretty=format:%at', '-n1'])
    return datetime.fromtimestamp(int(date))



def get_branch():
    branches = _run_command(['git', 'branch'])
    for line in branches.splitlines():
        if line.startswith('*'):
            return line[2:].rstrip()
    else:
        raise ValueError



def get_git_files():
    files = _run_command(['git', 'ls-files'])
    return [ name.strip() for name in files.splitlines() ]



def get_release():
    date = get_date()
    date = date.strftime('%Y%m%d-%H%M')
    return '%s-%s' % (get_branch(), date)



if __name__ == '__main__':
    try:
        print get_release()
    except:
        print>>stderr, '%s: error: unable to read info' % basename(argv[0])


