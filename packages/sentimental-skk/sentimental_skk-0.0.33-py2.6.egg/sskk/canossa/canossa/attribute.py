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



_ATTR_BOLD       = 1    # 00000000 00000000 00000000 00000010
_ATTR_UNDERLINED = 4    # 00000000 00000000 00000000 00010000
_ATTR_BLINK      = 5    # 00000000 00000000 00000000 00100000
_ATTR_INVERSE    = 7    # 00000000 00000000 00000000 10000000
_ATTR_INVISIBLE  = 8    # 00000000 00000000 00000001 00000000
_ATTR_FG         = 13   # 00000000 00111111 11100000 00000000
_ATTR_BG         = 22   # 01111111 11000000 00000000 00000000

class Attribute():

    _value = (0x100 << _ATTR_FG | 0x100 << _ATTR_BG, 0x42)

    def __init__(self, value = (0x100 << _ATTR_FG | 0x100 << _ATTR_BG, 0x42)):
        self._value = value

    def draw(self, s):
        params = [0]
        value, charset = self._value 
        for i in (1, 4, 5, 7, 8):
            if value & (1 << i):
                params.append(i) 

        fg = value >> _ATTR_FG & 0x1ff
        if fg == 0x100:
            pass
            #params.append(39)
        elif fg < 8:
            params.append(30 + fg)
        elif fg < 16:
            params.append(90 + fg - 8)
        else:
            params.append(38)
            params.append(5)
            params.append(fg)

        bg = value >> _ATTR_BG & 0x1ff
        if bg == 0x100:
            pass
            #params.append(49)
        elif bg < 8:
            params.append(40 + bg)
        elif bg < 16:
            params.append(100 + bg - 8)
        else:
            params.append(48)
            params.append(5)
            params.append(bg)
        s.write(u'\x1b(%c\x1b[%sm' % (charset, ';'.join([str(p) for p in params])))

    def clear(self):
        self._value = (0x100 << _ATTR_FG | 0x100 << _ATTR_BG, 0x42)

    def clone(self):
        return Attribute(self._value)

    def set_charset(self, charset):
        value, old = self._value
        self._value = (value, charset)

    def set_sgr(self, pm):
        i = 0
        if len(pm) == 0:
            value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG
            return
        value, charset = self._value
        while i < len(pm):
            n = pm[i]
            if n == 0:
                value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG
            elif n == 1:
                value |= 1 << _ATTR_BOLD 
            elif n == 4:
                value |= 1 << _ATTR_UNDERLINED 
            elif n == 5:
                value |= 1 << _ATTR_BLINK 
            elif n == 7:
                value |= 1 << _ATTR_INVERSE 
            elif n == 8:
                value |= 1 << _ATTR_INVISIBLE 
            elif n == 21:
                value &= ~(1 << _ATTR_BOLD)
            elif n == 22:
                value &= ~(1 << _ATTR_BOLD | 1 << _ATTR_UNDERLINED)
            elif n == 24:
                value &= ~(1 << _ATTR_UNDERLINED)
            elif n == 25:
                value &= ~(1 << _ATTR_BLINK)
            elif n == 27:
                value &= ~(1 << _ATTR_INVERSE)
            elif n == 28:
                value &= ~(1 << _ATTR_VISIBLE)

            elif 30 <= n and n < 38:
                value = (value & ~(0x1ff << _ATTR_FG)) | (n - 30) << _ATTR_FG
            elif n == 38:
                i += 1
                n1 = pm[i]
                i += 1
                n2 = pm[i]
                if n1 == 5:
                    value = value & ~(0x1ff << _ATTR_FG) | (n2 << _ATTR_FG)
            elif n == 39:
                value = value & ~(0x1ff << _ATTR_FG) | (0x100 << _ATTR_FG)

            elif 40 <= n and n < 48:
                value = (value & ~(0x1ff << _ATTR_BG)) | (n - 40) << _ATTR_BG
            elif n == 48:
                i += 1
                n1 = pm[i]
                i += 1
                n2 = pm[i]
                if n1 == 5:
                    value = value & ~(0x1ff << _ATTR_BG) | (n2 << _ATTR_BG)
            elif n == 49:
                value = value & ~(0x1ff << _ATTR_BG) | (0x100 << _ATTR_BG)

            elif 90 <= n and n < 98:
                value = (value & ~(0x1ff << _ATTR_FG)) | (n - 90 + 8) << _ATTR_FG
            elif 100 <= n and n < 108:
                value = (value & ~(0x1ff << _ATTR_BG)) | (n - 100 + 8) << _ATTR_BG

            else:
               pass
               #logger.writeLine("SGR %d is ignored." % n)
            i += 1
        self._value = (value, charset)

    def equals(self, other):
        return False
        return self._value == other._value

    def __str__(self):
        import StringIO
        s = StringIO.StringIO()
        self.draw(s)
        return s.getvalue().replace("\x1b", "<ESC>")

def test():
    """
    >>> attr = Attribute() 
    >>> print attr
    >>> attr.set_sgr([0])
    >>> print attr.equeals(Attribute())
    >>> print attr
    >>> attr.set_charset("A")
    >>> print attr
    >>> attr.set_sgr([0, 5, 6])
    >>> print attr
    >>> attr.set_sgr([7, 8])
    >>> print attr
    >>> attr.set_sgr([17, 18])
    >>> print attr
    >>> attr.set_sgr([38, 5, 200, 48, 5, 100])
    >>> print attr
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    print "attribute test."
    test()

