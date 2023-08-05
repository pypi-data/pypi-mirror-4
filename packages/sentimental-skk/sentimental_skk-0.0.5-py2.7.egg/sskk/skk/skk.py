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

import sys, os

import kanadb
import eisuudb
import romanrule
import dictionary
import title
import mode
import terminfo

import tff

################################################################################
#
# CharacterContext
#
class CharacterContext:

    def __init__(self):
        # トライ木の生成
        self.__hira_tree = romanrule.makehiratree()
        self.__kata_tree = romanrule.makekatatree()
        self.hardreset()

    def toggle(self):
        if id(self.__current_tree) == id(self.__hira_tree):
            self.__current_tree = self.__kata_tree
        else:
            self.__current_tree = self.__hira_tree

    def reset(self):
        self.context = self.__current_tree

    def hardreset(self):
        self.__current_tree = self.__hira_tree
        self.reset()

    def isempty(self):
        return id(self.context) == id(self.__current_tree)

    def isfinal(self):
        return self.context.has_key('value')

    def drain(self):
        if self.context.has_key('value'):
            s = self.context['value']
            if self.context.has_key('next'):
                self.context = self.context['next']
            else:
                self.reset()
            return s
        return u''

    def getbuffer(self):
        return self.context['buffer']

    def put(self, c):
        if self.context.has_key(c):
            self.context = self.context[c]
            return True
        return False

    def back(self):
        self.context = self.context['prev']

# マーク
_SKK_MARK_COOK = u'▽'
_SKK_MARK_SELECT = u'▼'
_SKK_MARK_OKURI = u'*'
_SKK_MARK_OPEN = u'【'
_SKK_MARK_CLOSE = u'】'

################################################################################
#
# CandidateManager
#
class CandidateManager():

    def __init__(self):
        self.reset()

    def assign(self, key, value=[], okuri=u''):
        self.__index = 0
        self.__key = key
        self.__list = value
        self.__okuri = okuri

    def reset(self):
        self.__index = 0
        self.__list = None
        self.__okuri = None
        self.__key = None

    def isempty(self):
        return self.__list == None

    def getyomi(self):
        return self.__key

    def getcurrent(self, kakutei=False):
        length = len(self.__list) # 候補数
        self.__index %= length + 1
        if self.__index == length:
            value = self.__key
        else:
            value = self.__list[self.__index]
            if kakutei:
                self.__list.insert(0, self.__list.pop(self.__index))

        # 補足説明
        index = value.find(";")
        if index >= 0:
            result = value[:index]
            remarks = value[index:]
        else:
            result = value
            remarks = None

        return _SKK_MARK_SELECT + result + self.__okuri, remarks 

    def getwidth(self):
        if self.isempty():
            return 0
        result, remarks = self.getcurrent()
        return len(result) * 2

    def movenext(self):
        self.__index += 1

    def moveprev(self):
        self.__index -= 1

################################################################################
#
# OutputHandler
#
class OutputHandler(tff.DefaultHandler):

    def __init__(self):
        self.__super = super(OutputHandler, self)

#    def handle_csi(self, context, prefix, params, final):
#        self.__super.handle_csi(context, prefix, params, final)
#
#    def handle_esc(self, context, prefix, final):
#        self.__super.handle_esc(context, prefix, final)
#
    def handle_control_string(self, context, prefix, value):
        if prefix == 0x5d: # ']'
            try:
                pos = value.index(0x3b)
            except ValueError:
                pass 
            if pos == -1:
                pass
            elif pos == 0:
                num = [0]
            else:
                try:
                    num = value[:pos]
                except:
                    num = None 
            if not num is None:
                if num == [0x30] or num == [0x32]:
                    arg = value[pos + 1:]
                    title.setoriginal(u''.join([unichr(x) for x in arg]))
                    value = num + [0x3b] + [ord(x) for x in title.get()]
                    
        self.__super.handle_control_string(context, prefix, value)

#    def handle_char(self, context, c):
#        self.__super.handle_char(context, c)


################################################################################
#
# InputHandler
#
class InputHandler(tff.DefaultHandler):

    def __init__(self, stdout, termenc):
        self.__stdout = stdout
        self.__termenc = termenc
        self.__context = CharacterContext()
        self.__mode = mode.ModeManager()
        self.__word_buffer = u'' 
        self.__candidate = CandidateManager()
        self.__counter = 0

    def __reset(self):
        self.__clear()
        self.__context.reset()
        self.__candidate.reset()
        self.__mode.endeisuu()
        self.__word_buffer = u'' 
        self.__refleshtitle()

    def __clear(self):
        candidate_length = self.__candidate.getwidth()
        cooking_length = len(self.__word_buffer) * 2 + len(self.__context.getbuffer())
        s = u' ' * max(candidate_length, cooking_length)
        self.__write(u'%s%s%s\x1b[?25h' % (terminfo.sc, s, terminfo.rc))

    def __write(self, s):
        self.__stdout.write(s.encode(self.__termenc))
        self.__stdout.flush()

    def __settitle(self, value):
        title.setmessage(value)
        self.__refleshtitle()

    def __refleshtitle(self):
        self.__write(u'\x1b]0;%s\x07' % title.get())

    def __getface(self):
        self.__counter = 1 - self.__counter
        return [u'三 ┗( ^o^)┓ ＜', u'三 ┏( ^o^)┛ ＜'][self.__counter]

    def __display(self):
        if not self.__candidate.isempty():
            result, remarks = self.__candidate.getcurrent()

            self.__write(
                u'%s\x1b[1;4;32;44m%s\x1b[m%s\x1b[?25l'
                % (terminfo.sc, result, terminfo.rc))
            face = self.__getface()
            if remarks:
                self.__settitle(u'%s %s - %s' % (face, result, remarks))
            else:
                self.__settitle(u'%s %s' % (face, result))
        else:
            s1 = self.__word_buffer
            s2 = self.__context.getbuffer() 
            if not len(s1) + len(s2) == 0:
                self.__write(u'\x1b7\x1b[1;4;31m%s\x1b[1;4;33m%s\x1b[m\x1b8\x1b[?25l' % (s1, s2))
            else:
                self.__write(u'\x1b[?25h')

    def __draincharacters(self):
        s = self.__context.getbuffer()
        if s == 'n':
            self.__context.put(0x6e) # n
        s = self.__context.drain()
        return s

    def __fix(self):
        s = self.__draincharacters()
        if len(self.__word_buffer) == 0:
            self.__word_buffer += _SKK_MARK_COOK
        self.__word_buffer += s

    def __iscooking(self):
        if not self.__candidate.isempty():
            return True
        if len(self.__word_buffer) > 0:
            return True
        if not self.__context.isempty():
            return True
        return False

    def __convert_kana(self, value):
        if self.__mode.ishira():
            return kanadb.to_kata(value)
        elif self.__mode.iskata():
            return kanadb.to_hira(value)
        else:
            raise

    def __toggle_kana(self):
        self.__context.toggle()
        self.__mode.toggle()
        self.__reset()

    def __tango_henkan(self):
        key = self.__word_buffer[1:]

        if self.__mode.iskata():
            key = kanadb.to_hira(key)

        result = dictionary.gettango(key)

        if result: 
            face = self.__getface()
            self.__settitle(u'%s %s' % (face, key))
            self.__candidate.assign(key, result)
            self.__clear()
            self.__display()
            return True

        # かな読みだけを候補とする
        self.__candidate.assign(key)

        return True

    def __okuri_henkan(self):
        buf = self.__context.getbuffer()[0]
        s = self.__context.drain()
        self.__word_buffer += s
        key, okuri = self.__word_buffer[1:].split(_SKK_MARK_OKURI)

        if self.__mode.iskata():
            key = kanadb.to_hira(key)

        result = dictionary.getokuri(key + buf)

        face = self.__getface()
        self.__settitle(u'%s %s - %s' % (face, key, buf))
        if not result is None:
            self.__candidate.assign(key, result, okuri)
            self.__clear()
            self.__word_buffer = u''
            return True

        # かな読みだけを候補とする
        if self.__mode.iskata():
            key = kanadb.to_kata(key)
        self.__candidate.assign(key, [], okuri)

        return True

    def __kakutei(self, context):
        self.__fix()
        if self.__candidate.isempty():
            word = self.__word_buffer[1:]
        else:
            result, remarks = self.__candidate.getcurrent(kakutei=True)
            word = result[1:]
        self.__reset()
        context.writestring(word)
        self.__settitle(u'＼(^o^)／')

    def __restore(self):
        # 再変換
        self.__clear()
        self.__word_buffer = _SKK_MARK_COOK + self.__candidate.getyomi()
        self.__candidate.reset()
        self.__display()

    def __next(self):
        # 単語変換
        if self.__candidate.isempty():
            s = self.__draincharacters()
            self.__word_buffer += s
            if not self.__tango_henkan():
                self.__kakutei(context)
        else:
            self.__clear()
            self.__candidate.movenext()
            self.__display()

    def __prev(self):
        # 単語変換
        if not self.__candidate.isempty():
            self.__clear()
            self.__candidate.moveprev()
            self.__display()

    def handle_char(self, context, c):
        if c == 0xa5:
            c = 0x5c
        if c == 0x0a: # LF C-j
            if self.__mode.isdirect():
                self.__mode.toggle()
                self.__refleshtitle()
            else:
                if self.__iscooking():
                    self.__kakutei(context)
        elif c == 0x0d: # CR C-m
            if self.__iscooking():
                self.__kakutei(context)
            else:
                context.write(c)
        elif c == 0x07: # BEL
            if self.__candidate.isempty():
                self.__reset()
            else:
                self.__restore()
        elif c == 0x08 or c == 0x7f: # BS or DEL
            if self.__context.isempty():
                word = self.__word_buffer
                if not self.__candidate.isempty():
                    self.__restore()
                elif len(word) == 0:
                    context.write(c)
                else:
                    self.__clear()
                    self.__word_buffer = word[:-1]
                    self.__display()
            else:
                self.__clear()
                self.__context.back()
                self.__display()
        elif c == 0x0e:
            if self.__iscooking():
                self.__next()
            else:
                context.write(c)
        elif c == 0x10:
            if self.__iscooking():
                self.__prev()
            else:
                context.write(c)
        elif c == 0x20: # SP 
            if self.__mode.ishan():
                context.write(c)
            elif self.__mode.iszen():
                context.write(eisuudb.to_zenkaku_cp(c))
            else:
                if self.__iscooking():
                    self.__next()
                else:
                    context.write(c)
        elif c < 0x20 or 0x7f < c:
            if self.__mode.isdirect():
                context.write(c)
            else:
                self.__reset()
                context.write(c)
        else:
            if self.__mode.ishan():
                # 半角直接入力
                context.write(c)
            elif self.__mode.iszen():
                # 全角直接入力
                context.write(eisuudb.to_zenkaku_cp(c))
            elif self.__mode.iseisuu():
                # 英数変換モード
                if len(self.__word_buffer) == 0:
                    self.__word_buffer = _SKK_MARK_COOK
                self.__word_buffer += unichr(c)
                self.__display()
            elif self.__mode.ishira() or self.__mode.iskata():
                # ひらがな変換モード・カタカナ変換モード
                if c == 0x2f: # /
                    if self.__iscooking():
                        self.__word_buffer += unichr(c)
                        self.__display()
                    else:
                        self.__mode.starteisuu()
                        self.__refleshtitle()
                        self.__word_buffer = _SKK_MARK_COOK
                        self.__display()
                elif c == 0x71: # q
                    word = self.__word_buffer
                    if self.__iscooking():
                        self.__fix()
                        word = self.__word_buffer
                        self.__reset()
                        s = self.__convert_kana(word[1:])
                        context.writestring(s)
                    else:
                        self.__toggle_kana()
                elif c == 0x4c: # L
                    if self.__iscooking():
                        self.__kakutei(context)
                    self.__mode.startzen()
                    self.__reset()
                elif c == 0x6c: # l
                    if self.__iscooking():
                        self.__kakutei(context)
                    self.__mode.reset()
                    self.__reset()
                else:
                    # 変換中か
                    if not self.__candidate.isempty():
                        # 変換中であれば、現在の候補をバックアップしておく
                        backup, remarks = self.__candidate.getcurrent()
                        self.__word_buffer = u''
                    else:
                        backup = None

                    if 0x41 <= c and c <= 0x5a: # A - Z
                        # 大文字のとき
                        self.__context.put(c + 0x20) # 子音に変換し、文字バッファに溜める

                        # バックアップがあるか
                        if backup:
                            # バックアップがあるとき、変換候補をリセット
                            self.__candidate.reset()

                            # 現在の候補を確定
                            context.writestring(backup[1:])
                            self.__word_buffer = _SKK_MARK_COOK
                            if self.__context.isfinal():
                                # cが母音のとき、文字バッファを吸い出し、
                                s = self.__context.drain()
                                # 単語バッファに追加
                                self.__word_buffer += s
                            s = backup[1:]
                            s += self.__word_buffer
                            s += self.__context.getbuffer()
                            self.__write(u'\x1b7\x1b[1;4;35m%s\x1b[m\x1b8\x1b[?25l' % s)

                        # 先行する入力があるか
                        elif len(self.__word_buffer) > 1:
                            # 先行する入力があるとき、送り仮名マーク('*')をつける
                            if self.__word_buffer[-1] != _SKK_MARK_OKURI:
                                self.__word_buffer += _SKK_MARK_OKURI
                            # cが母音か
                            if self.__context.isfinal():

                                # 送り仮名変換
                                self.__okuri_henkan()
                        else:
                            # 先行する入力が無いとき、単語バッファを編集マーク('▽')とする
                            self.__word_buffer = _SKK_MARK_COOK
                            # cが母音か
                            if self.__context.isfinal():
                                # cが母音のとき、文字バッファを吸い出し、
                                s = self.__context.drain()
                                # 単語バッファに追加
                                self.__word_buffer += s

                    elif self.__context.put(c):
                        if not backup is None:
                            self.__candidate.reset()
                            context.writestring(backup[1:])
                            s = backup[1:]
                            s += self.__word_buffer
                            s += self.__context.getbuffer()
                            self.__write(u'\x1b7\x1b[1;4;31m%s\x1b[m\x1b8\x1b[?25l' % s)
                            self.__word_buffer = u''
                        if self.__context.isfinal():
                            if backup or len(self.__word_buffer) == 0:
                                s = self.__context.drain()
                                context.writestring(s)
                            else:
                                # 送り仮名変換
                                if self.__word_buffer[-1] == _SKK_MARK_OKURI:
                                    self.__okuri_henkan()
                                else:
                                    s = self.__context.drain()
                                    self.__word_buffer += s
                    else:
                        self.__reset()
                        context.write(c)
                    self.__display()

