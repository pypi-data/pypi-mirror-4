#!/usr/bin/python

# This file is part of the M30W software.
# Copyright (C) 2012-2013 M30W developers.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# M30W follows PEP8 to increase readability. Why won't you?

from M30W.debug import debug
from M30W.GUI import show_app

def main():
    debug("Starting GUI...", 1)
    show_app()

if __name__ == '__main__':
    print "M30W Copyright (C) 2012 M30W developers."
    main()
