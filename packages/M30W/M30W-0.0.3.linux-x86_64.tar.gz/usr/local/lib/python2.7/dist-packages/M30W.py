#!/usr/bin/python
"""This is the M30W software.
Copyright (C) 2012 M30W developers.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
#M30W follows PEP8 to increase readability. Why won't you?

print """M30W Copyright (C) 2012 M30W developers.
"""
from core.debug import debug
from core.GUI import show_app

debug("Starting GUI...", 1)
show_app()
