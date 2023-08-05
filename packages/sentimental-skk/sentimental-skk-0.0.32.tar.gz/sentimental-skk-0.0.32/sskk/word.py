#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012  Hayaki Saito <user@zuse.jp>
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

_SKK_WORD_NONE  = 0
_SKK_WORD_MAIN  = 1
_SKK_WORD_OKURI = 2

class WordBuffer():

    __main = u""
    __mode = _SKK_WORD_NONE
    _wcswidth = None

    def __init__(self, termprop):
        self.reset()
        self._wcswidth = termprop.wcswidth

    def reset(self):
        self.__mode = _SKK_WORD_NONE 
        self.__main = u""

    def isempty(self):
        return self.__mode == _SKK_WORD_NONE 
    
    def get(self):
        if self.__mode == _SKK_WORD_NONE:
            return u""
        elif self.__mode == _SKK_WORD_MAIN:
            return self.__main
        else:
            assert self.__mode == _SKK_WORD_OKURI
            return self.__main

    def append(self, value):
        if self.__mode == _SKK_WORD_NONE:
            self.startedit()
        elif self.__mode == _SKK_WORD_MAIN:
            self.__main += value 
        else: # self.__mode == _SKK_WORD_OKURI:
            self.__main += value 

    def back(self):
        if self.__mode == _SKK_WORD_MAIN:
            self.__main = self.__main[:-1]
            if len(self.__main) == 0:
                self.__mode = _SKK_WORD_NONE
        elif self.__mode == _SKK_WORD_OKURI:
            self.__mode = _SKK_WORD_MAIN 
        else:
            raise Exception("Cannot back: %s" % self.__main)

    def startedit(self):
        self.__mode = _SKK_WORD_MAIN

    def startokuri(self):
        self.__mode = _SKK_WORD_OKURI

    def has_okuri(self):
        return self.__mode == _SKK_WORD_OKURI

    def length(self):
        if self.__mode == _SKK_WORD_NONE:
            return 0
        elif self.__mode == _SKK_WORD_MAIN:
            return self._wcswidth(self.__main)
        else:
            assert self.__mode == _SKK_WORD_OKURI
            return self._wcswidth(self.__main)


