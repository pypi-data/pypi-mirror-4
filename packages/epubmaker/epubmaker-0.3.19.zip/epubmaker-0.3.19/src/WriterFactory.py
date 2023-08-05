#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

WriterFactory.py

Copyright 2009-10 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Writer factory. Dynamically loads all writers from a directory.

"""

from __future__ import with_statement

import os.path

from pkg_resources import resource_listdir # pylint: disable=E0611

from epubmaker.lib.Logger import debug

writers = {}

def load_writers ():
    """ See what types we can write. """

    for fn in resource_listdir ('epubmaker.writers', ''):
        modulename, ext = os.path.splitext (fn)
        if ext == '.py':
            if modulename.endswith ('Writer'):
                type_ = modulename.lower ().replace ('writer', '')
                debug ("Loading writer type %s from module %s" % (type_, modulename))
                module = __import__ ('epubmaker.writers.' + modulename, fromlist = [modulename])
                writers[type_] = module

    return writers.keys ()


def unload_writers ():
    """ Unload writer modules. """
    for k in writers.keys ():
        del writers[k]
    

def create (type_):
    """ Load writer module for type. """

    try:
        return writers[type_].Writer ()
    except KeyError:
        raise KeyError ('No writer for type %s' % type_)


