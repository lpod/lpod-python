#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import random
import cProfile
# Import from lpod
from lpod.table import odf_create_table, odf_create_row, odf_create_cell
from lpod import __version__ as version

DEBUG = False

class initial_compute:
    def __init__(self, lines = 100, cols = 100):
        self.lines = lines
        self.cols = cols
        self.rnd_line = self.do_rnd_order(lines)
        self.rnd_col = self.do_rnd_order(cols)
        self.py_table0 = self.populate_order()
        self.py_table = self.populate()
        print "-" * 50

    def do_rnd_order(self, length):
        random.seed(42)
        order = range(length)
        random.shuffle(order)
        return order

    def populate(self):
        random.seed(42)
        base = range(self.cols)
        tab = []
        for dummy in xrange(self.lines):
            random.shuffle(base)
            tab.append(base[:])
        return tab

    def populate_order(self):
        base = range(self.cols)
        tab = []
        for r in xrange(self.lines):
            tab.append([r * self.cols + base[c] for c in base ])
        return tab

class chrono:
    def __init__(self):
        self.t0 = time.time()

    def delta(self):
        t1 = time.time()
        print "%.1f sec" % (t1-self.t0)

    def value(self):
        return t1-self.t0

    def ratio(self, base):
        return self.value() / base

def test_append_rows(D):
    print "Test append_row", D.lines, "rows", D.cols, "cols"
    table = odf_create_table(u"Table")
    C = chrono()
    for line in xrange(D.lines):
        row = odf_create_row()
        row.set_values(D.py_table0[line])
        table.append_row(row)
    C.delta()
    print "Size of table :", table.get_size()
    if DEBUG:
        print table.to_csv()
    print "-" * 50

def test_set_rows(D):
    print "Test random set_row", D.lines, "rows", D.cols, "cols"
    table = odf_create_table(u"Table")
    C = chrono()
    for line in xrange(D.lines):
        row = odf_create_row()
        row.set_values(D.py_table0[line])
        if DEBUG:
            print D.rnd_line[line], "=>", D.py_table0[line]

        table.set_row(D.rnd_line[line], row)
        if DEBUG:
            print table.to_csv()

    C.delta()
    print "Size of table :", table.get_size()
    if DEBUG:
        print table.to_csv()
    print "-" * 50
    return table

def test_swap(D, table_ini):
    print "Test swap rows/cols from table", D.lines, "rows", D.cols, "cols"
    table = odf_create_table(u"swapped", D.lines, D.cols)
    C = chrono()
    for col in xrange(D.cols):
        values = table_ini.get_column_values(col)
        table.set_row_values(col, values)
    C.delta()
    print "Size of swapped table :", table.get_size()
    if DEBUG:
        print table.to_csv()
    print "-" * 50

def test_random_set_value(D):
    print "Test random set_value", D.lines, "rows", D.cols, "cols"
    table = odf_create_table(u"Table")
    cpt = 0
    C = chrono()
    for line in D.rnd_line:
        for col in range(D.cols):
            table.set_value((col, line), cpt)
            cpt += 1
    C.delta()
    print cpt, "values entered"
    print "Size of table :", table.get_size()
    if DEBUG:
        print table.to_csv()
    print "-" * 50
    return table

def test_random_get_value(D, table_ini):
    print "Test read random get_value", D.lines, "rows", D.cols, "cols"
    vals = []
    cpt = 0
    C = chrono()
    for line in D.rnd_line:
        for col in D.rnd_col:
            vals.append(table_ini.get_value((col, line)))
            cpt += 1
    C.delta()
    print cpt, "values read"
    if DEBUG:
        print vals
    print "-" * 50

def test_repeated(D):
    print "test random repeated lines", D.lines, "rows", D.cols, "cols"
    table = odf_create_table(u"Table")
    C = chrono()
    for line in xrange(D.lines):
        row = odf_create_row()
        row.set_values([(line * 10 + x) for x in  range(D.cols)])
        row.set_repeated(line)
        #if DEBUG:
        #    print D.rnd_line[line], "=>", row.get_values(), row.get_repeated()
        table.set_row(D.rnd_line[line], row)
    C.delta()
    print "Size of table :", table.get_size()
    if DEBUG:
        print table.to_csv()
    print "-" * 50
    return table


if __name__=="__main__":
    print version
    total = chrono()
    #for r,c  in [(10,8)]:
    for r,c  in [(10,10), (100, 10), (100,100), (1000,10)]:
        D = initial_compute(lines = r, cols = c)
        test_append_rows(D)
        t = test_set_rows(D)
        test_swap(D, t)
        ##cProfile.run('t = test_random_set_value(D)')
        t = test_random_set_value(D)
        test_random_get_value(D, t)
        test_repeated(D)
    print "Total",
    total.delta()
