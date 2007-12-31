# -*- coding: UTF-8 -*-

# Copyright 2004-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

from xml.dom import NotFoundErr
#import os
#import sys
#import StringIO
#import xml.sax.saxutils import quoteattr,escape

class DomRewriter:
    """
    The old DOM rewriter is still around for index based stuff. It can
    be used for all the complex stuff but portage needed features should
    be in StreamRewriterBase subclasses as they are much faster.
    """
    from xml.dom import NotFoundErr
    def __init__(self, modifyElems = None, attributes = None , values=None, index=None):
        self.modifyElems = modifyElems
        self.attributes = attributes
        self.values = values
        self.index = index


    def delete_elements(self, document, **kwargs):
        if not self.modifyElems:
            return

        tomodify = []
        for tag in self.modifyElems:
            matches = document.getElementsByTagName(tag)
            if matches:
                if self.index == None:
                    for match in matches:
                        tomodify.append(match)
                else:
                    tomodify.append(matches[self.index])

        for elem in tomodify:
            for i,attr in enumerate(self.attributes):
                if self.values:
                    elem.setAttribute(attr, self.values[i])
                else:
                    try:
                        elem.removeAttribute(attr)
                    except DomRewriter.NotFoundErr:
                        continue


    def add_gentoo_classpath(self,document,**kwargs):
        newcp = kwargs.has_key('classpath') and kwargs['classpath'] or "void"
        newcp = newcp.split(":")
        gcp = document.createElement("path")
        for cp in newcp:
            pe = document.createElement("pathelement")
            pe.setAttribute("path",cp)
            gcp.appendChild(pe)


        # classpath nodes:
        # if no refud:
        #  remove inner elems
        #  add our gentoo classpath node
        # else
        #  rename refid references
        matches = document.getElementsByTagName("classpath")
        handled_refs = set()
        for match in matches:
            if not match.hasAttribute("refid"):
                for node in match.childNodes[:]:
                    match.removeChild(node)
                    node.unlink()

                    match.appendChild(gcp.cloneNode(True))
            else:
                refid = match.getAttribute("refid")
                for ref in document.getElementsByTagName("path"):
                    id = ref.getAttribute("id")
                    if id not in handled_refs and id == refid:
                        for node in ref.childNodes[:]:
                            ref.removeChild(node)
                            node.unlink()

                        for pathnode in (gcp.cloneNode(deep=True)).childNodes:
                            ref.appendChild(pathnode.cloneNode(deep=True))

                        handled_refs.add(id)

        # rewrite javac elements
        matches = document.getElementsByTagName("javac")
        for match in matches:
            classpath = match.getAttribute("classpath")
            if classpath:
                match.removeAttribute("classpath")

            for node in match.childNodes[:]:
                if node.nodeName == "classpath":
                    match.removeChild(node)
                    node.unlink()

            classpath = document.createElement("classpath")
            classpath.appendChild(gcp.cloneNode(True))
            match.appendChild(classpath)


    def process(self,in_stream,callback=None,*args,**kwargs):
        from xml.dom import minidom
        self.document = minidom.parseString(in_stream);

        if callback:
            callback(self.document,*args,**kwargs)


    def write(self,stream):
        from xml.dom.ext import PrettyPrint
        PrettyPrint(self.document,stream)


#set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap 
