# -*- coding: utf-8 -*-
#
#       blorb.py
#       
#       Copyright © 2009, 2010 Per Liedman <per@liedman.net>
#       Copyright © 2011 Brandon Invergo <b.invergo@gmail.com>
#       
#       This file is part of Grotesque.
#
#       Grotesque is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#
#       Grotesque is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with Grotesque.  If not, see <http://www.gnu.org/licenses/>.


from treatyofbabel.utils._binaryfuncs import read_int
from treatyofbabel.utils._imgfuncs import CoverImage, get_jpeg_dim, get_png_dim
import treatyofbabel.ifiction as ifiction


FORMAT = "blorb"
FORMAT_EXT = [".blorb", ".blb", ".zblorb", ".zlb", ".gblorb", ".glb"]
HOME_PAGE = "http://eblong.com/zarf/blorb"


def get_format_name():
    return FORMAT


def get_story_file_extension(file_buffer):
    if claim_story_file(file_buffer):
        story_format = get_story_format(file_buffer)
        if story_format == "zcode":
            return FORMAT_EXT[2]
        elif story_format == "glulx":
            return FORMAT_EXT[4]
        else:
            return FORMAT_EXT[0]
    return None


def get_home_page():
    return HOME_PAGE


def get_file_extensions():
    return FORMAT_EXT 


def claim_story_file(file_buffer):
    if len(file_buffer) < 16 or not file_buffer.startswith('FORM') \
            or file_buffer[8:12] != 'IFRS':
        return False
    return True


def get_story_file_meta(file_buffer, truncate=False):
    index, length = _get_chunk(file_buffer, 'IFmd')
    if index is None:
        return None
    return file_buffer[index:index + length]


def get_story_file_cover(file_buffer):
    i, length = _get_chunk(file_buffer, 'Fspc')
    if length < 4:
        return None
    i = read_int(file_buffer, i)
    pict_i, pict_len = _get_resource(file_buffer, 'Pict', i)
    if pict_i is None:
        return None
    cover_data = file_buffer[pict_i:pict_i + pict_len]
    cover_format = file_buffer[pict_i - 8:pict_i - 4]
    if cover_format == 'PNG ':
        ext = 'png'
        (width, height) = get_png_dim(cover_data)
    elif cover_format == 'JPEG':
        ext = 'jpg'
        (width, height) = get_jpeg_dim(cover_data)
    if width is None or height is None:
        raise Exception, "Image corrupted: cannot determine dimensions"
    cover = CoverImage(cover_data, ext, width, height)
    return cover


def get_story_file_ifid(file_buffer):
    meta = get_story_file_meta(file_buffer)
    if meta is None:
        return [_get_embedded_ifid(file_buffer)]
    story_dom = ifiction.get_ifiction_dom(meta) 
    story = ifiction.get_all_stories(story_dom)[0]
    ident = ifiction.get_identification(story)
    ifid_list = ident.get("ifid_list")
    if ifid_list is None or len(ifid_list) == 0:
        return [_get_embedded_ifid(file_buffer)]
    return ifid_list


def get_story_file(file_buffer):
    index, length = _get_resource(file_buffer, 'Exec', 0)
    if index is None:
        return None
    return file_buffer[index:index + length]


def get_story_format(file_buffer):
    treaty_registry = {'ZCOD': 'zcode', 'GLUL': 'glulx', 'TAD2': 'tads2',
                       'TAD3': 'tads3'}
    for story_format in treaty_registry:
        index, length = _get_chunk(file_buffer, story_format)
        if index is not None:
            return treaty_registry[story_format]
    return None


def _get_embedded_ifid(file_buffer):
    story_file = get_story_file(file_buffer)
    story_format = get_story_format(file_buffer)
    if story_format == "zcode":
        from treatyofbabel.formats import zcode as handler
    elif story_format == "glulx":
        from treatyofbabel.formats import glulx as handler
    elif story_format == "tads2":
        from treatyofbabel.formats import tads2 as handler
    elif story_format == "tads3":
        from treatyofbabel.formats import tads3 as handler
    else:
        raise Exception, "Unknown story format"
    return handler.get_story_file_ifid(story_file)


def _get_chunk(file_buffer, chunk_id):
    i = 12
    while i < len(file_buffer) - 8:
        length = read_int(file_buffer, i + 4)
        if file_buffer[i:i + 4] == chunk_id:
            if length > file_buffer:
                return (None, None)
            #return file_buffer[i + 8:i + 8 + length]
            return (i + 8, length)
        if length % 2 != 0:
            length = length + 1
        i = i + length + 8
    return (None, None)


def _get_resource(file_buffer, resource, n):
    i, length = _get_chunk(file_buffer, 'RIdx')
    if i is None:
        return (None, None)
    ridx = file_buffer[i+4:]
    ridx_len = read_int(file_buffer, i)
    for i in range(ridx_len):
        if (ridx[i * 12:i * 12 + 4] == resource and
                read_int(ridx, i * 12 + 4) == n):
            j = i
            i = read_int(ridx, j * 12 + 8)
            begin = i + 8
            out_len = read_int(file_buffer, i + 4)
            return (begin, out_len)
    return (None, None)


def _get_resources(file_buffer):
    index, length = _get_chunk('RIdx')
    number_resources = read_int(index, 0)
    result = []
    for i in xrange(0, number_resources):
        rsc_name = index[4 + i * 12:8 + i * 12]
        rsc_number = read_int(index, 8 + i * 12)
        result.append((rsc_name, rsc_number))
    return result

