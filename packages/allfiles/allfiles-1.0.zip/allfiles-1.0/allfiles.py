#encoding:ascii
__all__ = 'allfiles alldirs'.split()

import sys
import os
from fnmatch import fnmatch, fnmatchcase
from os.path import (
    join,
    abspath,
)

if sys.version_info >= (3,):
    BaseString = str
else:
    BaseString = basestring

def create_filter(patterns, ignore_case):
    if ignore_case:
        fn = fnmatchcase
    else:
        fn = fnmatch

    if isinstance(patterns, BaseString):
        patterns = [patterns]
    patterns = list(patterns)
    return lambda name:any(fn(name, pat) for pat in patterns)


def allfiles(start="./", pattern="*", *, ignore_case=False, single_level=False, yield_files=True, yield_dirs=False):
    '''
    Iterate all files in a directory that match pattern.

    pattern is a string, or a collections of string.
    strings is recognized as Unix shell-style wildcards.
    allfiles yields only files which are matches any of strings.

    If single_level is Trhe, then this function will not search in subdirectries
    If yield_dirs is True, then this function yields direcotries too.
    '''

    filter = create_filter(pattern, ignore_case)

    for root, dirs, files in os.walk(start):
        elements = list()
        if yield_files:
            elements.extend(files)
        if yield_dirs:
            elements.extend(dirs)
        for name in elements:
            if filter(name):
                yield  abspath(join(root, name))
        if single_level:
            break


def alldirs(*a, **kw):
    '''
    Iterate all files in a directory that match pattern.

    The arguments except yield_dirs are the same as for the Popen constructor.
    '''
    return allfiles(yield_files=False, yield_dirs=True, *a, **kw)
