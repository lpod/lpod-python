#!/usr/bin/env python
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend
# LGPL modified compatible Apache

# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from sys import stderr, exit, argv
from datetime import datetime


def get_date():
    try:
        # Date
        date = Popen(['git', 'log', '--pretty=format:%at', '-n1'],
                     stderr=PIPE, stdout=PIPE)
        if date.wait() != 0:
            raise ValueError
        date = datetime.fromtimestamp(int(date.stdout.read()))
    except:
        print>>stderr, '%s: error: unable to read info' % argv[0].split(
                                                                '/')[-1]
        exit(-1)
    # Output
    return date


def get_branch():
    try:
        # Branch
        branches = Popen(['git', 'branch'], stderr=PIPE, stdout=PIPE)
        if branches.wait() != 0:
            raise ValueError
        for line in branches.stdout:
            if line.startswith('*'):
                branch = line[2:].rstrip()
                break
        else:
            raise ValueError
    except:
        print>>stderr, '%s: error: unable to read info' % argv[0].split(
                                                                '/')[-1]
        exit(-1)
    # Output
    return branch


if __name__ == '__main__':

    date = get_date()
    date = date.strftime('%Y%m%d-%H%M')
    version = '%s-%s' % (get_branch(), date)

    print version

