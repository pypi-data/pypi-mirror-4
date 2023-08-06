# -*- coding: utf-8 -*-
#
# util.py
#
# Copyright (C) 2012, 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-pptx and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Utility functions and classes that come in handy when working with PowerPoint
and Open XML.
"""

import os
import platform
import re

class BaseLength(int):
    """Base class for length classes Inches, Cm, Mm, Px, and Emu."""
    EMUS_PER_INCH = 914400
    EMUS_PER_CM   = 360000
    EMUS_PER_MM   = 36000
    EMUS_PER_PX   = 9525 if platform.system() == 'Windows' else 12700
    
    def __new__(cls, emu):
        return int.__new__(cls, emu)
    
    @property
    def inches(self):
        return self / float(self.EMUS_PER_INCH)
    
    @property
    def cm(self):
        return self / float(self.EMUS_PER_CM)
    
    @property
    def mm(self):
        return self / float(self.EMUS_PER_MM)
    
    @property
    def px(self):
        # round can somtimes return values like x.999999 which are truncated
        # to x by int(); adding the 0.1 prevents this
        return int(round(self / float(self.EMUS_PER_PX)) + 0.1)
    
    @property
    def emu(self):
        return self
    

class Inches(BaseLength):
    """Convenience constructor for length in inches."""
    def __new__(cls, inches):
        emu = int(inches * BaseLength.EMUS_PER_INCH)
        return BaseLength.__new__(cls, emu)
    

class Cm(BaseLength):
    """Convenience constructor for length in centimeters."""
    def __new__(cls, cm):
        emu = int(cm * BaseLength.EMUS_PER_CM)
        return BaseLength.__new__(cls, emu)
    

class Mm(BaseLength):
    """Convenience constructor for length in millimeters."""
    def __new__(cls, mm):
        emu = int(mm * BaseLength.EMUS_PER_MM)
        return BaseLength.__new__(cls, emu)
    

class Px(BaseLength):
    """Convenience constructor for length in pixels."""
    def __new__(cls, px):
        emu = int(px * BaseLength.EMUS_PER_PX)
        return BaseLength.__new__(cls, emu)
    

class Emu(BaseLength):
    """Convenience constructor for length in english metric units."""
    def __new__(cls, emu):
        return BaseLength.__new__(cls, int(emu))
    

class Partname(object):
    """
    Provides access to partname components such as the baseURI and the part
    index.
    """
    __filename_re = re.compile('([a-zA-Z]+)([1-9][0-9]*)?')
    
    def __init__(self, partname):
        super(Partname, self).__init__()
        self.__partname = partname
    
    @property
    def baseURI(self):
        return os.path.split(self.__partname)[0]
    
    @property
    def filename(self):
        return os.path.split(self.__partname)[1]
    
    @property
    def ext(self):
        return os.path.splitext(self.__partname)[1]
    
    @property
    def partname(self):
        return self.__partname
    
    @property
    def basename(self):
        """
        Return basename of partname, e.g. ``slide`` for
        ``/ppt/slides/slide1.xml``.
        """
        name = os.path.splitext(self.filename)[0]  # filename with ext removed
        match = self.__filename_re.match(name)
        return match.group(1)
    
    @property
    def idx(self):
        """
        Return partname index as integer for tuple partname or None for
        singleton partname.
        """
        name = os.path.splitext(self.filename)[0]  # filename with ext removed
        match = self.__filename_re.match(name)
        return int(match.group(2)) if match.group(2) else None
    

def emu(inches):
    """Return *inches* converted to English Metric Units (EMU)."""
    return int(inches * 914400)

# utility sequential integer generator, suitable for generating unique ids.
def intsequence(start=1):
    num = start
    while True:
        yield num
        num += 1

# indents second and later attributes on the root element so namespace
# declarations don't spread off the page in the text editor and can be more
# easily inspected
def prettify_nsdecls(xml):
    lines = xml.splitlines()
    if len(lines) < 2                   : return xml  # if XML is all on one line, don't mess with it
    if not lines[0].startswith('<?xml') : return xml  # if don't find xml declaration on first line, pass
    if not lines[1].startswith('<')     : return xml  # if don't find an unindented opening element on line 2, pass
    rootline = lines[1]
    # split rootline into element tag part and attributes parts
    attrib_re = re.compile(r'([-a-zA-Z0-9_:.]+="[^"]*" *>?)')
    substrings = [substring.strip() for substring in attrib_re.split(rootline) if substring]
    # substrings looks something like ['<p:sld', 'xmlns:p="html://..."', 'name="Office Theme>"']
    if len(substrings) < 3: # means there's at most one attributes so no need to indent
        return xml
    indent = ' ' * (len(substrings[0])+1)
    newrootline = ' '.join(substrings[:2])  # join element tag and first attribute onto same line
    for substring in substrings[2:]:        # indent remaining attributes on following lines
        newrootline += '\n%s%s' % (indent, substring)
    lines[1] = newrootline
    return '\n'.join(lines)

def sortedtemplatefilepaths(templatedir, searchdir, filenameroot, ext):
    # trim leading slash off of searchdir if present
    searchdir = searchdir[1:] if searchdir.startswith('/') else searchdir
    # form fully qualified path to search directory
    dirpath = os.path.join(templatedir, searchdir)
    # form list of all files in the directory
    filepaths = {}
    for name in os.listdir(dirpath):
        fqname = os.path.join(dirpath, name)
        if not os.path.isfile(fqname):
            continue
        if not name.startswith(filenameroot) or not name.endswith(ext):
            raise Exception('''Unexpected file '%s' found in template.''' % os.path.join(searchdir, name))
        filenamenumber = name[len(filenameroot):-(len(ext)+1)]
        sortkey = int(filenamenumber) if filenamenumber else 0
        filepaths[sortkey] = fqname
    # return file paths sorted in numerical order (not lexicographic order)
    return [filepaths[key] for key in sorted(filepaths.keys())]


# TECHDEBT: Not all files in the media directory are necessarily image files.
#           Audio and Video media can show up there too, although are perhaps
#           less likely to appear in a presentation template.
def templatemediafilepaths(templatedir):
    # form fully qualified path to search directory
    dirpath = os.path.join(templatedir, 'ppt/media')
    # if directory doesn't exist, it means the template doesn't contain any media files
    if not os.path.isdir(dirpath):
        return []
    # form list of all files in the directory
    filepaths = []
    for name in os.listdir(dirpath):
        filepath = os.path.join(dirpath, name)
        if not os.path.isfile(filepath):
            continue
        filepaths.append(filepath)
    return filepaths


    