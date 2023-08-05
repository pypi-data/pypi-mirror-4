#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

CSSApplicator.py

Copyright 2011 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Read a CSS file and puts CSS properties into the style attribute of elements.
This was written to work around the huge deficiencies of the Amazon Kindlegen
application re. CSS.

"""

from __future__ import with_statement

import re
import operator
import xml.dom

from lxml import etree
from lxml.cssselect import CSSSelector
import cssutils

from epubmaker.lib.Logger import debug, error
from epubmaker.lib.GutenbergGlobals import NSMAP, xpath

re_ns = re.compile (r'(^|\s)([a-z]+)')

class CSSApplicator (object):
    """ Read a CSS file and puts CSS properties into the style
    attribute of elements.

    """
    
    shorthand_matrix = ( (), (0, 0, 0, 0), (0, 1, 0, 1), (0, 1, 2, 1), (0, 1, 2, 3) )
    shorthand_masks = 'margin%s padding%s border%s-color border%s-style border%s-width'.split ()
    shorthand_names = (s % '' for s in shorthand_masks)
    shorthands = zip (shorthand_names, shorthand_masks)
    
    def __init__ (self):
        pass

    @classmethod
    def explode_shorthands (cls, style):
        """ Explode {1,4}-type shorthand property. """
        
        for name, mask in cls.shorthands:
            if name in style:
                v = style[name].split ()
                del style[name]
                x = cls.shorthand_matrix[len (v)]

                style [mask % '-top']    = v[x[0]]
                style [mask % '-right']  = v[x[1]]
                style [mask % '-bottom'] = v[x[2]]
                style [mask % '-left']   = v[x[3]]
                    

    @staticmethod
    def css_zero (e, prop):
        try:
            return e.sd.get (prop, '0')[0] == '0'
        except xml.dom.DOMException:
            # debug (v)
            return False

    def init_style_dict (self, xhtml):
        # keep all element proxies alive,
        # see: http://lxml.de/element_classes.html#element-initialization
        self.proxy_cache = list (xhtml.iter ())
        
        for e in xhtml.iter ():
            sd = {}
            if 'style' in e.attrib:
                for s in cssutils.css.CSSStyleDeclaration (cssText = e.get ('style', '')):
                    sd[s.name] = s.value
                del e.attrib['style']
            e.sd = sd

                        
    def finalize_style_dict (self, xhtml):
        for e in xhtml.iter ():
            if isinstance (e, etree.ElementBase):
                if e.sd:
                    # do not remove zero margins because Kindlegen has an inheritance bug
                    # Kindle knows no margin-right
                    for prop in ('margin-right', ):
                        if prop in e.sd:
                            del e.sd[prop]
                    if len (e.sd):
                        e.set ('style', '; '.join (sorted (map (
                            lambda x: "%s: %s" % (x[0], x [1]), e.sd.iteritems ()))))
                del e.sd
                # don't delete 'pageno' class
                #if 'class' in e.attrib:
                #    del e.attrib['class']

                    
    def apply (self, xhtml):
        """ Read a CSS file and puts CSS properties into the style
        attribute of elements. """

        css = ''
        for style in xpath (xhtml, '//xhtml:style'):
            css += style.text
            style.getparent ().remove (style)

        parser = cssutils.CSSParser ()
        sheet = parser.parseString (css)

        declarations = []
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for selector in rule.selectorList:
                    # assure this is a stable sort
                    specificity = selector.specificity + (len (declarations), )
                    declarations.append ((selector, rule.style, specificity))

        # sort most specific selectors first
        declarations.sort (key = operator.itemgetter (2), reverse = True)

        for (selector, style, specificity) in declarations:
            selector_text = selector.selectorText
            selector_text = re_ns.sub (r'\1xhtml|\2', selector_text)
            sel = CSSSelector (selector_text, namespaces = NSMAP)
            elements = sel (xhtml)
            # debug ("Selector: %s matched %d elements" % (selector_text, len (elements)))

            # explode some shorthands
            self.explode_shorthands (style)

            # for s in style:
            #     debug ("  Setting: %s: %s" % (s.name, s.value))
                
            # iterate selected elements
            for e in elements:
                for s in style:
                    # earlier rules are more specific
                    if not s.name in e.sd:
                        e.sd[s.name] = s.value


    def collapse_margins (self, xhtml):
        """ Collapse CSS margins.

        Actually you cannot collapse correctly this early because you
        need to collapse computed values, which are not available
        yet. But its still better than not collapsing at all.
        
        """
        
        # FIXME: check if margin-* applies to the element or
        # we might collapse margin onto an element that doesn't
        # have margins.
        # FIXME check for floats and absolute positioning
        
        def collapse (e1, e2, prop1, prop2 = None):
            prop2 = prop2 or prop1
            # debug ("Collapsing %s %s with %s %s" % (e1.tag, prop1, e2.tag, prop2 ))
            try:
                v1 = cssutils.css.DimensionValue (e1.sd.get (prop1, '0'))
                v2 = cssutils.css.DimensionValue (e2.sd.get (prop2, '0'))
                if v1.dimension == v2.dimension:
                    if v1.value > v2.value:
                        e1.sd[prop1] = v1.cssText
                    else:
                        e1.sd[prop1] = v2.cssText
                    e2.sd[prop2] = '0'
            except xml.dom.DOMException:
                return
        
        for e in xhtml.xpath (
            '//xhtml:div|//xhtml:p|//xhtml:table|//xhtml:h1|//xhtml:h2|//xhtml:h3|//xhtml:h4|//xhtml:h5|//xhtml:h6',
            namespaces = NSMAP):
        
            p = e.getparent ()

            if p is not None:
                css_zero = self.css_zero
                # collapse top of first child with top of parent
                if e.getprevious () is None:
                    if (not css_zero (e, 'margin-top') and
                        not css_zero (p, 'margin-top') and
                        css_zero (e, 'border-top-width') and
                        css_zero (e, 'padding-top')):

                        collapse (p, e, 'margin-top')

                # collapse bottom of last child with bottom of parent
                if e.getnext () is None:
                    if (not css_zero (e, 'margin-bottom') and
                        not css_zero (p, 'margin-bottom') and
                        css_zero (e, 'border-bottom-width') and
                        css_zero (e, 'padding-bottom')):

                        collapse (p, e, 'margin-bottom')
                
            # collapse top with bottom of previous element
            
            prev = e.getprevious ()
            if prev is not None:
                collapse (e, prev, 'margin-top', 'margin-bottom')
