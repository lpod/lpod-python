.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Luis Belmar-Letelier <luis@itaapy.com>
            David Versmisse <david.versmisse@itaapy.com>

   This file is part of Lpod (see: http://lpod-project.org).
   Lpod is free software; you can redistribute it and/or modify it under
   the terms of either:

   a) the GNU General Public License as published by the Free Software
      Foundation, either version 3 of the License, or (at your option)
      any later version.
      Lpod is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.
      You should have received a copy of the GNU General Public License
      along with Lpod.  If not, see <http://www.gnu.org/licenses/>.

   b) the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0


.. contents:: Scripting
   :local:

lpod-show.py
=============
::

  luis@spinoza ~/lpod $ lpod-show.py -h
  Usage: lpod-show.py <file>
  
  Dump text from an OpenDocument file to the standard output, optionally styles
  and meta.
  
  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -d DIRNAME, --dirname=DIRNAME
                          dump output in files in the given directory.
    -m, --meta            dump metadata (if -d DIR add DIR/meta.txt)
    -s, --styles          dump styles (if -d DIR add DIR/styles.txt)


lpod-style.py
=============
::

  luis@spinoza ~/lpod $ lpod-style.py -h
  Usage: lpod-style.py <file>
  
  A command line interface to manipulate styles of OpenDocument files.
  
  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -a, --automatic       show automatic styles only
    -c, --common          show common styles only
    -p, --properties      show properties of styles
    -d, --delete          delete all styles (except default)
    -m FILE, --merge-styles-from=FILE
                          copy styles from FILE to <file>. Any style with the
                          same name will be replaced.

lpod-meta.py
=============
::

  luis@spinoza ~/lpod $ lpod-meta.py -h
  Usage: lpod-meta.py [options] <file>
  
  Dump metadata informations on the standard output
  
  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -s NAME=VALUE, --set=NAME=VALUE
                          Replace and/or set the metadata NAME with the value
                          VALUE

lpod-merge.py
=============
::

  luis@spinoza ~/lpod $ lpod-merge.py -h
  Usage: lpod-merge.py <file1> [<file2> ...]
  
  Merge all input files in an unique OpenDocument file
  
  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -o FILE, --output=FILE
                          Place output in file FILE (out.od[t|s|p] by default)

    
