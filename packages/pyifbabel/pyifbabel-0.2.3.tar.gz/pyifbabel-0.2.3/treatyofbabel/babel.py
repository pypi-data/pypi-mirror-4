# -*- coding: utf-8 -*-
#
#       babel.py
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


import sys
import os.path
import xml.dom.minidom

import ifiction
from babelerrors import BabelError
from formats import (adrift, advsys, agt, alan, executable, glulx, hugo, level9,
                     magscrolls, quest, tads2, tads3, zcode)
from wrappers import blorb


VERSION = "0.2.3"
TREATY_VERSION = "7"
HANDLERS = [adrift, advsys, agt, alan, executable, glulx, hugo, level9, 
            magscrolls, quest, tads2, tads3, zcode]
EXTENSION_MAP = {}


for h in HANDLERS:
    for ext in h.get_file_extensions():
        EXTENSION_MAP[ext] = h


def deduce_handler(story_file, story_buffer):
    """Deduce the handler for a story file.
    """

    if story_file is None:
        raise UnboundError() 
    elif story_file == "":
        raise ValueError()
    basename = os.path.basename(story_file)
    extension = os.path.splitext(basename)[1]
    handler = EXTENSION_MAP.get(extension)
    if handler is None or not handler.claim_story_file(story_buffer):
        for h in HANDLERS:
            if h.claim_story_file(story_buffer):
                handler = h
    if handler is None:
        raise BabelError, 'Unknown story format'
    return handler


def _get_story_data(story_file):
    if story_file is None or story_file == "":
        raise ValueError, "No story file specified"
    with open(story_file, 'rb') as story_handle:
        story_data = story_handle.read()
    # If the data read is less than 20 bytes (arbitrarily chosen), it probably
    # doesn't contain a valid story file.
    if len(story_data) < 20:
        raise ValueError, "Truncated story file"
    return story_data


def deduce_format(story_file):
    """Deduce the format of a story file.
    """

    story_data = _get_story_data(story_file)
    if blorb.claim_story_file(story_data):
        story_format = blorb.get_story_format(story_data)
        return "blorbed {0}".format(story_format)
    else:
        handler = deduce_handler(story_file, story_data)
        return handler.get_format_name()


def get_ifids(story_file):
    """Get the IFID from a story file or from an ifiction
    file.
    """

    try:
        xml_doc = xml.dom.minidom.parse(story_file)
    except:
        story_data = _get_story_data(story_file) 
        if blorb.claim_story_file(story_data):
            return blorb.get_story_file_ifid(story_data)
        else:
            handler = deduce_handler(story_file, story_data)
            return [handler.get_story_file_ifid(story_data)]
    else:
        if not ifiction.is_ifiction(xml_doc):
            return None
        ifids = []
        stories = ifiction.get_all_stories(xml_doc)
        for story in stories:
            ifids.append(ifiction.get_identification(story)["ifid"])
        return ifids


def get_meta(story_file, truncate=False):
    """Get the available metadata for a story file.
    """

    story_data = _get_story_data(story_file)
    if blorb.claim_story_file(story_data):
        return blorb.get_story_file_meta(story_data)
    else:
        handler = deduce_handler(story_file, story_data)
        if handler.HAS_META:
            return handler.get_story_file_meta(story_data, truncate)
    return None


def get_cover(story_file):
    """Extract cover art from a story file.
    """

    story_data = _get_story_data(story_file)
    if blorb.claim_story_file(story_data):
        return blorb.get_story_file_cover(story_data)
    else:
        handler = deduce_handler(story_file, story_data)
        if handler.HAS_COVER:
            return handler.get_story_file_cover(story_data)
    return None


def get_story(story_file):
    """Extract a story from a file (i.e. a blorb).
    """

    story_data = _get_story_data(story_file)
    if blorb.claim_story_file(story_data):
        return blorb.get_story_file(story_data)
    else:
        return story_data


def verify_ifiction(story_file):
    """Verify the integrity of an iFiction file.
    """

    pass


def ifiction_lint(story_file):
    """Verify the style of an iFiction file.
    """

    pass


def complete_ifiction(story_file):
    """Generate a complete iFiction file from a sparse one.
    """

    pass


def make_blorb(story_file, ifiction_handle, output_handle, coverart_handle=None):
    """Bundle story file and ifiction into a blorb.
    """
    
    pass
