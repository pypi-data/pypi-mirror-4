#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012-2013  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

import abc


class IWindow():

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self, rect):
        pass

    @abc.abstractmethod
    def getrect(self):
        pass


class Rect():
    left = 0
    top = 0
    width = 0
    height = 0

    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

class Rects():

    def __init__(self, row, col):
        self._windows = []
        self._rects = [Rect(0, 0, self._col, self._row)]


def xor():
    pass


class Region():

    _windows = None
    _row = 0
    _col = 0

    def __init__(self, row, col):
        self._windows = []
        self._rects = [ Rect(0, 0, self._col, self._row) ]

    def handle_resize(self, context, row, col):
        pass

    def register(self, window):
        self._windows.insert(0, window)

    def update(self):
        for window in self._windows:
            rect = window.getrect()
            self.exclude(rect)
        pass

    def exclude(self, rect):
        lefttop = (rect.left, rect.top)
        self._rect

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
