#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

HTMLWriter.py

Copyright 2009 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Writes an HTML file

"""

from __future__ import with_statement

import os
import copy

from lxml import etree
from pkg_resources import resource_string # pylint: disable=E0611

import epubmaker.lib.GutenbergGlobals as gg
from epubmaker.lib.GutenbergGlobals import xpath
from epubmaker.lib.Logger import info, debug, error, exception

from epubmaker import writers

PRIVATE_CSS = """
.pageno       { position: absolute; right: 95%; font: medium sans-serif; text-indent: 0 }
.pageno:after { color: gray; content: '[' attr(title) ']' }
.lineno       { position: absolute; left:  95%; font: medium sans-serif; text-indent: 0 }
.lineno:after { color: gray; content: '[' attr(title) ']' }
.toc-pageref  { float: right }
pre           { font-family: monospace; font-size: 0.9em; white-space: pre-wrap }
"""


class Writer (writers.HTMLishWriter):
    """ Class for writing HTML files. """


    def add_dublincore (self, tree):
        """ Add dublin core metadata to <head>. """
        source = gg.archive2files (
            self.options.ebook, self.options.candidate.filename)

        if hasattr (options.config, 'FILESDIR'):
            self.options.dc.source = source.replace (options.config.FILESDIR, options.config.PGURL)
        
        for head in xpath (tree, '//xhtml:head'):
            for e in self.options.dc.to_html ():
                e.tail = '\n'
                head.append (e)


    def build (self):
        """ Build HTML file. """

        htmlfilename = os.path.join (self.options.outputdir, 
                                     self.options.outputfile)
        try:
            os.remove (htmlfilename)
        except OSError:
            pass
                                     
        try:
            info ("Creating HTML file: %s" % htmlfilename)

            for p in self.spider.parsers:
                # Do html only. The images were copied earlier by PicsDirWriter.

                xhtml = None
                if hasattr (p, 'rst2html'):
                    xhtml = p.rst2html ()
                elif hasattr (p, 'xhtml'):
                    p.parse ()
                    xhtml = copy.deepcopy (p.xhtml)

                if xhtml is not None:
                    self.make_links_relative (xhtml, p.url)

                    self.add_dublincore (xhtml)

                    # makes iphones zoom in
                    self.add_meta (xhtml, 'viewport', 'width=device-width')
                    self.add_meta_generator (xhtml)

                    self.add_internal_css (xhtml, PRIVATE_CSS)

                    preamble = "%s\r\n%s\r\n" % (gg.XML_DECLARATION, gg.XHTML_DOCTYPE)
                    html = etree.tostring (xhtml, 
                                           method = 'xml',
                                           encoding = 'utf-8', 
                                           pretty_print = True,
                                           xml_declaration = False)
                    
                    self.write_with_crlf (htmlfilename, preamble + html)

            # self.copy_aux_files (self.options.outputdir)
        
            info ("Done HTML file: %s" % htmlfilename)

        except StandardError, what:
            exception ("Error building HTML %s: %s" % (htmlfilename, what))
            if os.access (htmlfilename, os.W_OK):
                os.remove (htmlfilename)
            raise what


