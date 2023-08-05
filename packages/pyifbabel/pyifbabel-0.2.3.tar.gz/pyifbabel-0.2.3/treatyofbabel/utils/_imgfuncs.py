# -*- coding: utf-8 -*-
#
#       _imgfuncs.py
#       
#       Copyright © 2012 Brandon Invergo <brandon@brandoninvergo.com>
#       
#       This file is part of pyifbabel.
#
#       pyifbabel is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#
#       pyifbabel is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with pyifbabel.  If not, see <http://www.gnu.org/licenses/>.


from _binaryfuncs import read_char, read_long


class CoverImage(object):
    def __init__(self, data=None, img_format=None, width=None, height=None):
        self.data = data
        self.img_format = img_format
        self.width = width
        self.height = height


def get_jpeg_dim(img):
    if read_char(img, 0) != 0xff or read_char(img, 1) != 0xD8:
        return (None, None)
    dp = 2
    ep = len(img)
    while True:
        if dp > ep:
            return (None, None)
        t1 = read_char(img, dp)
        dp += 1
        while t1 != 0xff:
            if dp > ep:
                return (None, None)
            t1 = read_char(img, dp)
            dp += 1
        t1 = read_char(img, dp)
        dp += 1
        while t1 == 0xff:
            if dp > ep:
                return (None, None)
            t1 = read_char(img, dp)
            dp += 1
        if t1 & 0xF0 == 0xC0 and not (t1 == 0xC4 or t1 == 0xC8 or t1 == 0xCC):
            dp += 3
            if dp > ep:
                return (None, None)
            h = read_char(img, dp) * 2**8
            dp += 1
            if dp > ep:
                return (None, None)
            h = h | read_char(img, dp)
            dp += 1
            if dp > ep:
                return (None, None)
            w = read_char(img, dp) * 2**8
            dp += 1
            if dp > ep:
                return (None, None)
            w = w | read_char(img, dp)
            return (w, h)
        elif t1 == 0xD8 or t1 == 0xD9:
            break
        else:
            if dp > ep:
                return (None, None)
            l = read_char(img, dp) * 2**8
            dp += 1
            if dp > ep:
                return (None, None)
            l = l | read_char(img, dp)
            l -= 2
            dp += l
            if dp > ep:
                return (None, None)
    return (None, None)


def get_png_dim(img):
    if (len(img) < 33 or not (ord(img[0]) == 137 and ord(img[1]) == 80 and
                              ord(img[2]) == 78 and ord(img[3]) == 71 and
                              ord(img[4]) == 13 and ord(img[5]) == 10 and 
                              ord(img[6]) == 26 and ord(img[7]) == 10) or
                         not (img[12] == 'I' and img[13] == 'H' and
                              img[14] == 'D' and img[15] == 'R')):
        return (None, None)
    w = read_long(img, 16)
    h = read_long(img, 20)
    return (w, h)
