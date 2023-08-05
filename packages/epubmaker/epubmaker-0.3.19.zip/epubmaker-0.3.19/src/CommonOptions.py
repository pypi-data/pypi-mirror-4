#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

CommonOptions.py

Copyright 2010 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Common options for programs.

"""

from __future__ import with_statement

import optparse
import ConfigParser
import os

class Struct (object):
    pass

def cb_option_range (option, opt_str, value, parser):
    """ read a range from user input """

    try:
        r = map (lambda x: int (x) if x else None, value.split ('-'))
    except ValueError:
        raise optparse.OptionValueError (
            "%s must be one or two numbers eg. 42 or 42-69" % opt_str)

    if len (r) > 2:
        raise optparse.OptionValueError (
            "%s must be at most two numbers eg. 42-69" % opt_str)
        
    if len (r) == 1: 
        r.append (r[0])

    if r[1] and r[0] > r[1]:
        raise optparse.OptionValueError (
            "%s descending ranges not allowed." % opt_str)

    setattr (parser.values, option.dest, r)


def add_common_options (op):
    """ Add options common to all programs. """
    
    op.add_option (
        "-c", "--config",
        metavar  = "FILE",
        dest     = "config_name", 
        action   = "store",
        default  = "config",
        help     = "use config file (default: config)")

    op.add_option (
        "-v", "--verbose",
        dest     = "verbose", 
        action   = "count",
        help     = "be verbose (-v -v be more verbose)")

    op.add_option (
        "--validate",
        dest     = "validate", 
        action   = "count",
        help     = "validate epub through epubcheck")

    op.add_option (
        "--section",
        metavar  = "TAG.CLASS",
        dest     = "section_tags", 
        default  = [],
        action   = "append",
        help     = "split epub on TAG.CLASS")


def get_parser (**kwargs):
    op = optparse.OptionParser (**kwargs)
    add_common_options (op)
    return op
    

def parse_args (op, params = {}, defaults = {}):
    (options, args) = op.parse_args ()

    cp = ConfigParser.SafeConfigParser (params)
    cp.read ( [options.config_name,
               os.path.expanduser ('~/.epubmaker.conf'),
               '/etc/epubmaker.conf' ] )

    options.config = Struct ()

    for name, value in defaults.iteritems ():
        setattr (options.config, name.upper (), value)
        
    for section in cp.sections ():
        for name, value in cp.items (section):
            #if value == 'None':
            #    value = None
            # print section, name, value
            setattr (options.config, name.upper (), value)

    return options, args


