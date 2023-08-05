# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytils.translit import translify #, slugify
import hashlib
import sys
import os
import re

StringTypes = [type(str('str')),type(u'unicode')]
FNsp=re.compile(r'\s+')
FNbss=re.compile(r'^_+')
FNess=re.compile(r'_+$')
FNdsp = [
    re.compile(r'_\.'),
    re.compile(r'\._'),
    re.compile(r'-\.'),
    re.compile(r'\.-'),
]
FNdspsp = [
    re.compile(r'_-'),
    re.compile(r'-_'),
    re.compile(r'--'),
]
FNmsp = re.compile(r'_+')
#FNother=re.compile(r'[\\\(\)\'\"\@\#\$\%\^\&\*\!\/]')
FNother=re.compile(r'[^-\.\w]')
#---------------------------------------------------------------
#---------------------------------------------------------------
class Enum(object):
    def __init__(self, **kwargs):
        self._attrs = kwargs
    def __getattr__(self, name):
        if name not in self._attrs:
            raise AttributeError(name)
        return self._attrs[name]
    def __iter__(self):
        return self._attrs.iteritems()
#---------------------------------------------------------------
#---------------------------------------------------------------
def Str2Int(a,D=0):
    '''
    Convert String to Integer if it's possible
    return D or zerro if not possible
    '''
    try:
      rv = int(a)
    except:
      rv = D
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def CleanFileName(filename):
    '''
    Transliting filename from russian language
    Removing double spaces, commas, dots, dashes, and some condition chars from filename
    '''
    filename=FNsp.sub('_',filename)
    filename=translify(filename)
    filename=FNother.sub('',filename.lower())
    for i in FNdsp:
        filename=i.sub('.',filename)
    for i in FNdspsp:
        filename=i.sub('-',filename)
    n = filename.count('.')
    if (n > 1):
        filename = filename.replace('.','_',n-1)
        filename = filename.replace('_.','.')
    filename=FNmsp.sub('_',filename)
    filename=FNbss.sub('',filename)
    filename=FNess.sub('',filename)
    return filename
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_file_hash(filename, algo='sha512', buffsize=1024*1024):
    rv = None
    h = hashlib.new(algo)
    with open(filename,'rb') as fd:
        while True:
            b = fd.read(buffsize)
            if not b:
                break
            h.update(b)
    rv = h.hexdigest()
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_pname():
    pname = sys.argv[0].split(os.sep)[-1]
    pname = pname.split('.')[0]
    return pname
#---------------------------------------------------------------
#---------------------------------------------------------------
def u8(c):
    if (sys.version_info.major < 3):
        rv = c.encode('utf-8')
    else:
        rv = c
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
