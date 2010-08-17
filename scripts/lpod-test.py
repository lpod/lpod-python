#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
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

# Import from the standard library
from optparse import OptionParser
from sys import exit

# Import from lpod
from lpod import __version__
from lpod.release import _run_command


if  __name__ == "__main__":
    # Options initialisation
    usage = "%prog <filename>"
    description = ("Validate an ODF document thanks to the ODFPY project "
                   "cf http://odfpy.forge.osor.eu/")
    parser = OptionParser(usage, version=__version__,
            description=description)
    # Parse options
    options, args = parser.parse_args()

    # Document
    if len(args) != 1:
        parser.print_help()
        exit(1)
    document = args[0]

    # Finish me :-)
    print _run_command(["odflint", document])
