#
# (c)2009 Arjan Scherpenisse <arjan@scherpenisse.net>
#
# MIT licenced, see LICENSE file for details.
#

""" File utilities for torrenthelper. """

import os, re

def extensions(files):
    return [(f.find(".")+1) and f.split(".")[-1].lower() or "" for f in files]

def extensions_cnt(files, ext):
    if type(ext) != type([]):
        ext = [ext]
        
    return sum([1 for x in extensions(files) if x in ext])

def extensions_all(files, ext):
    return extensions_cnt(files, ext) == len(files)

def extensions_any(files, ext):
    return extensions_cnt(files, ext) >= 1

def extensions_most(files, ext):
    return extensions_cnt(files, ext) >= 0.5 * len(files)


def matches(files, regexp):
    def m(f):
        if re.match(regexp, f, re.I):
            return True
        return False
    return filter(m, files)

def matches_all(files, regexp):
    return len(matches(files, regexp)) == len(files)

def matches_any(files, regexp):
    return len(matches(files, regexp)) >= 1

def matches_most(files, regexp):
    return len(matches(files, regexp)) >= 0.5 * len(files)


def common_basedirs (files, prefix=""):
    """ given a set files, group them into common base dirs, on the first level, and strip this level. """

    dirs = {}
    
    for f in files:

        p = f
        l = len(os.path.sep)
        o = l
        if p[0:len(os.path.sep)] == os.path.sep:
            o += l
            p = p[l:]
            
        while os.path.dirname(p) != "":
            p = os.path.dirname(p)

        file = f[len(p)+o:]
        if file:
            p += os.path.sep
            if prefix+p not in dirs:
                dirs[prefix+p] = []
            dirs[prefix+p].append(file)
        else:
            dirs[prefix+p] = None
    return dirs

def basedirs(files, p=""):
    dirs = common_basedirs(files)
    olddirs = dirs
    while len(dirs) == 1:
        prefix = dirs.keys()[0]
        olddirs = dirs
        if dirs[prefix] is None:
            break
        dirs = common_basedirs(dirs[prefix], p+prefix)

    files = []
    keys = olddirs.keys()
    for k in keys:
        if olddirs[k] is None:
            files.append(k)
            del olddirs[k]
    return olddirs, files


def one_folder (files):
    """ Return true if all files are in one common folder. """
    dirs = common_basedirs(files)
    while len(dirs) == 1:
        dirs = common_basedirs(dirs[dirs.keys()[0]])

    return len(dirs) == len(files) and dirs.values() == [None] * len(files)

