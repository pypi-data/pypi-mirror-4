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


import wcwidth
try:
    from CStringIO import StringIO
except:
    from StringIO import StringIO
import sys
#import logger

import sys, os, termios, select

def _get_pos():
    stdin = sys.stdin 
    stdout = sys.stdout
    stdin_fileno = stdin.fileno()
    vdisable = os.fpathconf(stdin_fileno, 'PC_VDISABLE')
    backup = termios.tcgetattr(stdin_fileno)
    new = termios.tcgetattr(stdin_fileno)
    new[3] &= ~(termios.ECHO | termios.ICANON)
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(stdin_fileno, termios.TCSANOW, new)
    try:
        stdout.write("\x1b[6n")
        stdout.flush()
        
        rfd, wfd, xfd = select.select([stdin_fileno], [], [], 2)
        if rfd:
            data = os.read(stdin_fileno, 32)
            assert data[:2] == '\x1b['
            assert data[-1] == 'R'
            y, x = [int(n) - 1 for n in  data[2:-1].split(';')]
            return y, x
    finally:
        termios.tcsetattr(stdin_fileno, termios.TCSANOW, backup)

_ATTR_BOLD       = 1
_ATTR_UNDERLINED = 4
_ATTR_BLINK      = 5
_ATTR_INVERSE    = 7
_ATTR_INVISIBLE  = 8
_ATTR_FG         = 14 
_ATTR_BG         = 23 
class Attribute():

    __value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG

    def __init__(self, value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG):
        self.__value = value

    def draw(self, s):
        params = []
        value = self.__value 
        for i in xrange(0, 8):
            if value & (2 << i):
                params.append(i) 

        fg = value >> _ATTR_FG & 0x1ff
        if fg == 0:
            pass
        elif fg < 8:
            params.append(30 + fg)
        elif fg == 0x100:
            params.append(39)
        else:
            params += [38, 5, fg]

        bg = value >> _ATTR_BG & 0x1ff
        if fg == 0:
            pass
        elif bg < 8:
            params.append(40 + bg)
        elif bg == 0x100:
            params.append(49)
        else:
            params += [48, 5, bg]
        s.write(u'\x1b[0;')
        s.write(';'.join([str(p) for p in params]))
        s.write('m')

    def clear(self):
        self.__value = value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG

    def get(self):
        return self.__value

    def set(self, pm):
        i = 0
        while i < len(pm):
            n = pm[i]
            if n == 0:
                self.__value = 0x100 << _ATTR_FG | 0x100 << _ATTR_BG
            elif n == 1:
                self.__value |= 2 << _ATTR_BOLD 
            elif n == 4:
                self.__value |= 2 << _ATTR_UNDERLINED 
            elif n == 5:
                self.__value |= 2 << _ATTR_BLINK 
            elif n == 7:
                self.__value |= 2 << _ATTR_INVERSE 
            elif n == 8:
                self.__value |= 2 << _ATTR_INVISIBLE 
            elif n == 21:
                self.__value &= ~(2 << _ATTR_BOLD)
            elif n == 22:
                self.__value &= ~(2 << _ATTR_BOLD | 2 << _ATTR_UNDERLINED)
            elif n == 24:
                self.__value &= ~(2 << _ATTR_UNDERLINED)
            elif n == 25:
                self.__value &= ~(2 << _ATTR_BLINK)
            elif n == 27:
                self.__value &= ~(2 << _ATTR_INVERSE)
            elif n == 28:
                self.__value &= ~(2 << _ATTR_VISIBLE)
            elif 30 <= n and n < 38:
                self.__value = self.__value & ~(0x1ff << _ATTR_FG) | (n - 30) << _ATTR_FG

            elif n == 38:
                i += 1
                n1 = pm[i]
                i += 1
                n2 = pm[i]
                if n1 == 5:
                    self.__value = self.__value & ~(0x1ff << _ATTR_FG) | (n2 << _ATTR_FG)
            elif n == 39:
                self.__value = self.__value & ~(0x1ff << _ATTR_FG) | (0x100 << _ATTR_FG)
            elif 40 <= n and n < 48:
                self.__value = self.__value & ~(0x1ff << _ATTR_BG) | (n - 40) << _ATTR_BG

            elif n == 48:
                i += 1
                n1 = pm[i]
                i += 1
                n2 = pm[i]
                if n1 == 5:
                    self.__value = self.__value & ~(0x1ff << _ATTR_BG) | (n2 << _ATTR_BG)
            elif n == 49:
                self.__value = self.__value & ~(0x1ff << _ATTR_BG) | (0x100 << _ATTR_BG)
            elif 90 <= n and n < 98:
                self.__value = self.__value & ~(0x1ff << _ATTR_FG) | (n - 90 + 8) << _ATTR_FG
            elif 100 <= n and n < 108:
                self.__value = self.__value & ~(0x1ff << _ATTR_BG) | (n - 100 + 8) << _ATTR_BG
            else:
               pass
               #logger.writeLine("SGR %d is ignored." % n)
            i += 1

class Cell():

    __value = None
    attr = 0

    def __init__(self):
        self.__value = u' '

    def write(self, value, attr):
        self.__value = unichr(value)
        self.attr = attr.get()

    def pad(self):
        self.__value = None 

    def combine(self, value):
        self.__value += unichr(value)

    def get(self):
        return self.__value

    def clear(self, attr):
        self.__value = u' '
        self.attr = attr.get()

class Line():

    def __init__(self, width):
        self.cells = [Cell() for cell in xrange(0, width)]
        self.dirty = True

    def resize(self, col):
        width = len(self.cells)
        if col < width:
            self.cells = self.cells[:col]
        elif col > width:
            self.cells += [Cell() for cell in xrange(0, col - width)]
        self.dirty = True

    def clear(self, attr):
        self.dirty = True
        for cell in self.cells:
            cell.clear(attr)

    def write(self, value, pos, attr):
        self.cells[pos].write(value, attr)

    def pad(self, pos):
        self.cells[pos].pad()

    def combine(self, value, pos):
        self.cells[max(0, pos - 1)].combine(value)

    def draw(self, s, left, right):
        self.dirty = False
        attr = -1
        cells = self.cells
        if left > 0:
            c = cells[left - 1].get()
            if c is None:
                s.write(u'\x08') # BS
                left -= 1
        for cell in cells[left:right]:
            c = cell.get()
            if not c is None:
                if attr != cell.attr:
                    attr = cell.attr
                    Attribute(attr).draw(s)
                s.write(c)
        if c is None:
            for cell in cells[right:]:
                c = cell.get()
                if not c is None:
                    if attr != cell.attr:
                        attr = cell.attr
                        Attribute(attr).draw(s)
                    s.write(c)
                    break

class Cursor():

    def __init__(self, y=0, x=0, attr=None):
        self.col = x
        self.row = y
        self.dirty = True
        if attr:
            self.attr = Attribute(attr)
        else:
            self.attr = Attribute()
        self.__backup = None

    def clear(self):
        self.col = 0
        self.row = 0
        self.dirty = True
        self.attr.clear()

    def save(self):
        self.__backup = Cursor(self.row, self.col, self.attr.get())

    def restore(self):
        if self.__backup:
            self.col = self.__backup.col
            self.row = self.__backup.row
            self.attr = self.__backup.attr
            self.__backup = None

    def draw(self, s):
        s.write("\x1b[%d;%dH" % (self.row + 1, self.col + 1))
        self.dirty = False

class Screen():

    tcem = True
    decawm = True
    decom = False

    width = 80
    height = 24

    _saved_pos = None

    def __init__(self, row=24, col=80, y=0, x=0):
        self.height = row
        self.width = col
        self._mainbuf = [Line(col) for line in xrange(0, row)]
        self._altbuf = [Line(col) for line in xrange(0, row)]
        self.lines = self._mainbuf
        self.cursor = Cursor(y, x)
        self.scroll_top = 0 
        self.scroll_bottom = self.height 
        self.__reset_tab()

    def resize(self, row, col):
        lines = self.lines
        height = len(lines)
        if row < height:
            while row != len(lines):
                lines.pop()
            for line in lines:
                line.resize(col)
        elif row > height:
            for line in lines:
                line.resize(col)
            while row != len(lines):
                lines.insert(0, Line(col))
        else:
            for line in lines:
                line.resize(col)
        assert row == len(lines)
        assert col == len(lines[0].cells)
        if self.scroll_top == 0 and self.scroll_bottom == self.height:
            self.scroll_top = 0
            self.scroll_bottom = row 
        self.height = row
        self.width = col
        self.__reset_tab()

    def drawrect(self, col, row, width, height):
        height = min(height, self.height)
        width =  min(width, self.width)
        s = StringIO()
        #y, x = _get_pos() 
        #s.write("\x1b7")
        s.write("\x1b[m")
        for i in xrange(row, row + height):
            s.write("\x1b[%d;%dH" % (i + 1, col + 1))
            self.lines[i].draw(s, col, col + width)
        #s.write("\x1b8")
        self.cursor.attr.draw(s) 
        #s.write("\x1b[%d;%dH" % (y + 1, x + 1))
        try:
            sys.stdout.write(s.getvalue())
            sys.stdout.flush()
        except:
            pass

    def draw(self):
        cursor = self.cursor
        s = StringIO()
        dirty = False
        for i, line in enumerate(self.lines):
            if line.dirty:
                dirty = True
                s.write("\x1b[%d;1H" % (i + 1))
                line.draw(s, 0, self.width)
        if self.tcem:
            dirty = True
            cursor.draw(s)
        if dirty:
            try:
                sys.stdout.write(s.getvalue())
                sys.stdout.flush()
            except:
                pass

    def save_pos(self):
        self._saved_pos = (self.cursor.row, self.cursor.col)

    def restore_pos(self):
        if self._saved_pos:
            self.cursor.row, self.cursor.col = self._saved_pos

    def switch_mainbuf(self):
        for line in self.lines:
            line.clear(self.cursor.attr)
        self.lines = self._mainbuf
        for line in self.lines:
            line.dirty = True

    def switch_altbuf(self):
        self.lines = self._altbuf
        for line in self.lines:
            line.clear(self.cursor.attr)

    def __wrap(self):
        self.cursor.col = 0 
        if self.decawm:
            self.lf()

    def write(self, c):
        row, col = self.cursor.row, self.cursor.col
        line = self.lines[row] 

        if col >= self.width:
            self.__wrap()
            row, col = self.cursor.row, self.cursor.col
            line = self.lines[row] 

        line.dirty = True

        width = wcwidth.mk_wcwidth(c)

        if width == 1: # normal (narrow) character
            if self.cursor.col >= self.width:
                self.cursor.col = self.width - 1
                col = self.cursor.col
            line.write(c, col, self.cursor.attr)
            self.cursor.dirty = True
            self.cursor.col += 1
            #if col > len(line.cells) - 1:
            #    self.cursor.col = len(line.cells) - 1
        elif width == 2: # wide character
            if self.cursor.col >= self.width - 1:
                self.cursor.col = self.width - 2
                col = self.cursor.col
            line.pad(col)
            line.write(c, col + 1, self.cursor.attr)
            self.cursor.dirty = True
            self.cursor.col += 2
            #if col > len(line.cells) - 1:
            #    self.cursor.col = len(line.cells) - 1
        elif width == 0: # combining character
            line.combine(c, col)

        
    def bs(self):
        if self.cursor.col >= self.width:
            self.cursor.col = self.width - 1

        if self.cursor.col <= 0:
            pass
        else:
            self.cursor.col -= 1
        self.cursor.dirty = True

    def lf(self):
        if self.cursor.col >= self.width:
            self.__wrap() 
        if self.cursor.row >= self.scroll_bottom - 1:
            for line in self.lines:
                line.dirty = True
            self.lines.pop(self.scroll_top)
            self.lines.insert(self.scroll_bottom - 1, Line(self.width))
            self.cursor.row = self.scroll_bottom - 1 
        else:
            self.cursor.row += 1
        self.cursor.dirty = True

    def ht(self):
        line = self.lines[self.cursor.row] 
        col = self.cursor.col
        if col < self.width:
            col += 1
            for stop in self.__tabstop:
                if col <= stop:
                    self.cursor.col = stop 
                    break
            else:
                self.cursor.col = self.width - 1 
        else: 
            self.cursor.col = 0
        self.cursor.dirty = True

    def ind(self):
        self.lf()

    def nel(self):
        self.cr()
        self.lf()

    def ri(self):
        if self.cursor.row <= self.scroll_top:
            for line in self.lines:
                line.dirty = True
            self.lines.insert(self.scroll_top, Line(self.width))
            self.lines.pop(self.scroll_bottom)
            self.cursor.row = self.scroll_top 
        else:
            self.cursor.row -= 1
        self.cursor.dirty = True

    def cr(self):
        self.cursor.col = 0
        self.cursor.dirty = True

    def decstbm(self, top, bottom):
        self.scroll_top = max(0, top)
        self.scroll_bottom = min(bottom + 1, self.height)
        self.cursor.row = self.scroll_top
        self.cursor.col = 0

    def dch(self, n):
        self.cursor.dirty = True

    def vpa(self, row):
        if row >= self.scroll_bottom:
            self.cursor.row = self.scroll_bottom - 1
        elif row < self.scroll_top:
            self.cursor.row = self.scroll_top
        else:
            self.cursor.row = row
        self.cursor.dirty = True

    def hvp(self, row, col):
        if row >= self.scroll_bottom:
            self.cursor.row = self.scroll_bottom - 1
        elif row < self.scroll_top:
            self.cursor.row = self.scroll_top
        else:
            self.cursor.row = row
        self.cursor.col = col
        self.cursor.dirty = True

    def cup(self, row, col):
        if self.decom:
            row += self.scroll_top
        if row >= self.scroll_bottom:
            self.cursor.row = self.scroll_bottom - 1
        elif row < self.scroll_top:
            self.cursor.row = self.scroll_top
        else:
            self.cursor.row = row
        self.cursor.col = col
        self.cursor.dirty = True

    def ed(self, ps):
        if ps == 0:
            line = self.lines[self.cursor.row] 
            line.dirty = True
            for cell in line.cells[self.cursor.col:]:
                cell.clear(self.cursor.attr)
            if self.cursor.row < self.height:
                for line in self.lines[self.cursor.row + 1:]:
                    line.clear(self.cursor.attr)

        elif ps == 1:
            line = self.lines[self.cursor.row] 
            line.dirty = True
            for cell in line.cells[:self.cursor.col]:
                cell.clear(self.cursor.attr)
            if self.cursor.row > 0:
                for line in self.lines[:self.cursor.row]:
                    line.clear(self.cursor.attr)

        elif ps == 2:
            for line in self.lines:
                line.clear(self.cursor.attr)

        else:
            raise

    def so(self):
        pass

    def si(self):
        pass

    def __reset_tab(self):
        self.__tabstop = [n for n in xrange(0, self.width + 1, 8)] 

    def hts(self):
        if self.cursor.col in self.__tabstop:
            pass
        elif len(self.__tabstop) > 0 and self.__tabstop[0] > self.cursor.col:
            self.__tabstop.insert(0, self.cursor.col)
        else:
            for i, stop in enumerate(self.__tabstop[0:]):
                if self.cursor.col < stop:
                    self.__tabstop.insert(i, self.cursor.col)
                    break
            else:
                self.__tabstop.append(self.cursor.col)

    def tbc(self, ps):
        if ps == 0:
            if self.cursor.col in self.__tabstop:
                self.__tabstop.remove(self.cursor.col)
        elif ps == 3:
            self.__tabstop = []

    def decaln(self):
        for line in self.lines:
            line.dirty = True
            for cell in line.cells:
                cell.write(0x45, self.cursor.attr) # E
        self.scroll_top = 0 
        self.scroll_bottom = self.height 

    def ris(self):
        for line in self.lines:
            line.dirty = True
            for cell in line.cells:
                cell.write(0x20, self.cursor.attr) # SP 
        self.tcem = True
        self.cursor.clear() 
        self.__reset_tab()

    def sgr(self, pm):
        self.cursor.attr.set(pm)

    def cuu(self, ps):
        if self.cursor.row >= self.scroll_top + ps:
            self.cursor.row -= ps 
        else:
            self.cursor.row = self.scroll_top 

    def cud(self, ps):
        if self.cursor.row < self.scroll_bottom - ps:
            self.cursor.row += ps 
        else:
            self.cursor.row = self.scroll_bottom - 1 

    def cuf(self, ps):
        if self.cursor.col < self.width - ps:
            self.cursor.col += ps 
        else:
            self.cursor.col = self.width - 1 

    def cub(self, ps):
        if self.cursor.col >= ps:
            self.cursor.col -= ps 
        else:
            self.cursor.col = 0 

    def dl(self, ps):
        row = self.cursor.row
        lines = self.lines
        bottom = self.scroll_bottom
        for line in lines[row + ps:bottom]:
            line.dirty = True
        for x in xrange(0, ps):
            lines.insert(bottom, Line(self.width))
            lines.pop(row)

    def il(self, ps):
        row = self.cursor.row
        lines = self.lines
        bottom = self.scroll_bottom
        for line in lines[row:bottom - ps]:
            line.dirty = True
        for x in xrange(0, ps):
            lines.pop(bottom - 1)
            lines.insert(row, Line(self.width))

    def el(self, ps):
        line = self.lines[self.cursor.row] 
        if ps == 0:
            cells = line.cells[self.cursor.col:]
        elif ps == 1:
            cells = line.cells[:self.cursor.col]
        elif ps == 2:
            cells = line.cells
        else:
            raise
        line.dirty = True
        for cell in cells:
            cell.clear(self.cursor.attr) 

