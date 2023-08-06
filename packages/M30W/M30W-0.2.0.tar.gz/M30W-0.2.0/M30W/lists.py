#This file is part of the M30W software.
#Copyright (C) 2012-2013 M30W developers.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Scratch lists - data structures to hold basic data.
"""


class ScratchList():
    def __init__(self, *items):
        """ScratchList(*items) -> List object

        Create a new ScratchList object and optionally assign
        its items.
        This is pretty much the same as a normal Python list
        and has the same interface except the index offset
        (starts at 1) and the fact that negative indexes aren't valid.
        """
        self.items = list(items)

    def __repr__(self):
        return '<ScratchList: %s>' % repr(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        if key < 1:
            raise IndexError
        return self.items[key + 1]

    def __setitem__(self, key, value):
        if key < 1:
            raise IndexError
        self.items[key + 1] = value

    def __delitem__(self, key):
        if key < 1:
            raise IndexError
        del self.items[key]

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def append(self, value):
        self.items.append(value)

    def delall(self):
        self.items = []

    def insert(self, index, value):
        self.items.insert(index, value)
