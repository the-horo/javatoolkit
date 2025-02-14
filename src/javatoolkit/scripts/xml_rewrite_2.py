#!/usr/bin/env python3
# Copyright 2004-2020 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2


import io
import sys

from optparse import OptionParser, make_option

import xml.sax.handler
from xml.sax.saxutils import XMLGenerator, escape, quoteattr

from ..xml import sax


def add_gentoo_classpath(document):
    matches = document.getElementsByTagName("classpath")
    gcp = document.createElement("location")
    gcp.setAttribute("path", "${gentoo.classpath}")

    handled_refs = set()
    for match in matches:
        if match.hasAttribute("refid"):
            refid = match.getAttribute("refid")
            for ref in document.getElementsByTagName("path"):
                id = ref.getAttribute("id")
                if id not in handled_refs and id == refid:
                    gcp = document.createElement("pathelement")
                    gcp.setAttribute("path", "${gentoo.classpath}")
                    ref.appendChild(gcp)
                    handled_refs.add(id)
                else:
                    match.appendChild(gcp)


class DomRewriter:
    """
    The old DOM rewriter is still around for index based stuff. It can
    be used for all the complex stuff but portage needed features should
    be in StreamRewriterBase subclasses as they are much faster.
    """
    from xml.dom import NotFoundErr

    def __init__(self, modifyElems, attributes, values=None, index=None):
        self.modify = modifyElems
        self.attributes = attributes
        self.values = values
        self.index = index

    def change_elem(self, elem):
        for i, attr in enumerate(self.attributes):
            if self.values:
                elem.setAttribute(attr, self.values[i])
            else:
                try:
                    elem.removeAttribute(attr)
                except DomRewriter.NotFoundErr:
                    continue

    def process(self, in_stream, callback=None):
        from xml.dom.minidom import parse

        self.document = parse(in_stream)

        if callback:
            callback(self.document)

        if not self.modify:
            return

        for tag in self.modify:
            matches = self.document.getElementsByTagName(tag)
            if matches:
                if self.index is None:
                    for match in matches:
                        self.change_elem(match)
                else:
                    self.change_elem(matches[self.index])

    def write(self, stream):
        stream.write(self.document.toxml())


class StreamRewriterBase:
    def __init__(self, elems, attributes, values, index,
                 sourceElems=[], sourceAttributes=[], sourceValues=[],
                 targetElems=[], targetAttributes=[], targetValues=[]):
        self.buffer = io.StringIO()
        self.__write = self.buffer.write
        self.elems = elems
        self.attributes = attributes
        self.values = values
        self.sourceElems = sourceElems
        self.sourceAttributes = sourceAttributes
        self.sourceValues = sourceValues
        self.targetElems = targetElems
        self.targetAttributes = targetAttributes
        self.targetValues = targetValues

    def p(self, str):
        self.__write(str)

    def write(self, out_stream):
        value = self.buffer.getvalue()
        out_stream.write(value)
        self.buffer.truncate(0)

    def write_attr(self, a, v):
        self.p('%s=%s ' % (a, quoteattr(v, {'©': '&#169;'})))

    def start_element(self, name, attrs):
        self.p('<%s ' % name)

        match = (name in self.elems)
        matchSource = (name in self.sourceElems)
        matchTarget = (name in self.targetElems)

        for a, v in attrs:
            if not (
                    (match and a in self.attributes)
                    or (matchSource and a in self.sourceAttributes)
                    or (matchTarget and a in self.targetAttributes)
            ):
                self.write_attr(a, v)

        if matchSource:
            for i, attr in enumerate(self.sourceAttributes):
                self.write_attr(attr, self.sourceValues[i])

        if matchTarget:
            for i, attr in enumerate(self.targetAttributes):
                self.write_attr(attr, self.targetValues[i])

        if match:
            for i, attr in enumerate(self.attributes):
                self.write_attr(attr, self.values[i])

        self.p('>')


class ExpatRewriter(StreamRewriterBase):
    """
    The only problem with this Expat based implementation is that it does not
    handle entities doctypes etc properly so for example dev-java/skinlf fails.
    """

    def process(self, in_stream):
        from xml.parsers.expat import ParserCreate
        parser = ParserCreate()

        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.CharacterDataHandler = self.char_data
        parser.ParseFile(in_stream)
        self.p('\n')

    def start_element(self, name, attrs):
        StreamRewriterBase(self, name, iter(attrs.items()))

    def end_element(self, name):
        self.p('</%s>' % name)

    def char_data(self, data):
        self.p(escape(data))


class SaxRewriter(XMLGenerator, StreamRewriterBase):
    """
    Using Sax gives us the support for writing back doctypes and all easily
    and is only marginally slower than expat as it is just a tight layer over it
    """

    def __init__(self, elems, attributes, values, index,
                 sourceElems=[], sourceAttributes=[], sourceValues=[],
                 targetElems=[], targetAttributes=[], targetValues=[]):
        if not sourceElems:
            sourceElems = []
        if not sourceAttributes:
            sourceAttributes = []
        if not sourceValues:
            sourceValues = []
        if not targetElems:
            targetElems = []
        if not targetAttributes:
            targetAttributes = []
        if not targetValues:
            targetValues = []
        if not index:
            index = 0
        StreamRewriterBase.__init__(self, elems, attributes, values, index,
                                    sourceElems, sourceAttributes, sourceValues,
                                    targetElems, targetAttributes, targetValues)
        XMLGenerator.__init__(self, self.buffer, 'UTF-8')

    def process(self, in_stream):
        sax.parse(in_stream, content_handler=self, features={xml.sax.handler.feature_external_ges: 1})
        self.p('\n')

    def startElement(self, name, attrs):
        self.start_element(name, list(attrs.items()))


def main():
    usage = """Copyright 2004, 2006, 2007, 2017 Gentoo Foundation
Distributed under the terms of the GNU General Public Licence v2

Reach out to the Gentoo Java Team <java@gentoo.org> for questions/problems.

Usage:
    xml-rewrite-2.py [-f file] --delete [-g] -e tag [-e tag] -a attribute [-a attribute] [-i index]
    xml-rewrite-2.py [-f file] --change [-g] -e tag [-e tag] -a attribute -v value [-a attribute -v value]
    xml-rewrite-2.py [-f file] -g

Additional parameters:
    [--source-element tag] [--source-attribute attribute --source-value value]
    [--target-element tag] [--target-attribute attribute --target-value value] [-i index]

If the -f parameter is not used, the script will read and
write to stdin and stdout respectively. The use of quotes on
parameters will break the script."""

    def error(message):
        print("ERROR: " + message)
        sys.exit(1)

    options_list = [
        make_option(
            "-f",
            "--file",
            action="append",
            dest="files",
            help="Transform files instead of operating on stdout and stdin"),
        make_option(
            "-g",
            "--gentoo-classpath",
            action="store_true",
            dest="gentoo_classpath",
            help="Rewrite build.xml to use gentoo.classpath where applicable."),
        make_option(
            "-c",
            "--change",
            action="store_true",
            dest="doAdd",
            default=False,
            help="Change the value of an attribute.  If it does not exist, it will be created."),
        make_option(
            "-d",
            "--delete",
            action="store_true",
            dest="doDelete",
            default=False,
            help="Delete an attribute from matching elements."),
        make_option(
            "-e",
            "--element",
            action="append",
            dest="elements",
            help="Tag of the element of which the attributes to be changed.  These can be chained for multiple elements."),
        make_option(
            "-a",
            "--attribute",
            action="append",
            dest="attributes",
            help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs"),
        make_option(
            "-v",
            "--value",
            action="append",
            dest="values",
            help="Value to set the attribute to."),
        make_option(
            "-r",
            "--source-element",
            action="append",
            dest="source_elements",
            help="Tag of the element of which the attributes to be changed just in source scope.  These can be chained for multiple elements."),
        make_option(
            "-t",
            "--source-attribute",
            action="append",
            dest="source_attributes",
            help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs (for source only)"),
        make_option(
            "-y",
            "--source-value",
            action="append",
            dest="source_values",
            help="Value to set the attribute to. (sourceonly)"),
        make_option(
            "-j",
            "--target-element",
            action="append",
            dest="target_elements",
            help="Tag of the element of which the attributes to be changed just in target scope.  These can be chained for multiple elements."),
        make_option(
            "-k",
            "--target-attribute",
            action="append",
            dest="target_attributes",
            help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs (for targetonly)"),
        make_option(
            "-l",
            "--target-value",
            action="append",
            dest="target_values",
            help="Value to set the attribute to (targeronly)."),
        make_option(
            "-i",
            "--index",
            type="int",
            dest="index",
            help="Index of the match.  If none is specified, the changes will be applied to all matches within the document. Starts from zero.")
    ]

    parser = OptionParser(usage, options_list)
    (options, args) = parser.parse_args()
    # Invalid Arguments Must be smited!
    if not options.doAdd and not options.doDelete and not options.gentoo_classpath:
        print(usage)
        print()
        error("No action was specified.")

    if not options.gentoo_classpath:
        if options.doAdd and options.doDelete:
            error("Unable to perform multiple actions simultaneously.")
        if not options.elements and not options.target_elements and not options.source_elements:
            error(
                "At least one element (global, source only or target only) and attribute must be specified.")
        for elem in (options.source_attributes or []):
            if elem in (options.attributes or []):
                error(
                    "You can't set an attribute in global and source scope at the same time")
        for elem in (options.target_attributes or []):
            if elem in (options.attributes or []):
                error(
                    "You can't set an attribute in global and target scope at the same time")
            if options.doAdd and (len(options.values or []) != len(options.attributes or [])
                                  or len(options.source_values or []) != len(options.source_attributes or [])
                                  or len(options.target_values or []) != len(options.target_attributes or [])):
                error("You must give attribute(s)/value(s) for every element you are changing.")

        # End Invalid Arguments Check

    def get_rewriter(options):
        if options.index or options.doDelete or options.gentoo_classpath:
            # java-ant-2.eclass does not use these options so we can optimize the ExpatWriter
            # and let the DomRewriter do these. Also keeps the index option
            # compatible for sure.
            rewriter = DomRewriter(
                options.elements,
                options.attributes,
                options.values,
                options.index)
        else:
            rewriter = SaxRewriter(options.elements, options.attributes, options.values, options.index,
                                   options.source_elements, options.source_attributes, options.source_values,
                                   options.target_elements, options.target_attributes, options.target_values)
        return rewriter

    rewriter = get_rewriter(options)

    if options.files:
        import os
        for file in options.files:
            print("Rewriting %s" % file)
            # First parse the file into memory
            # Tricks with cwd are needed for relative includes of other xml
            # files to build.xml files
            cwd = os.getcwd()
            dirname = os.path.dirname(file)
            if dirname != '':  # for file = build.xml comes out as ''
                os.chdir(os.path.dirname(file))

            with open(os.path.basename(file), 'r') as f:
                if options.gentoo_classpath:
                    rewriter.process(f, add_gentoo_classpath)
                else:
                    rewriter.process(f)

            os.chdir(cwd)

            # Then write it back out to the file
            with open(file, 'w') as f:
                rewriter.write(f)

    else:
        if options.gentoo_classpath:
            rewriter.process(sys.stdin, add_gentoo_classpath)
        else:
            rewriter.process(sys.stdin)
        rewriter.write(sys.stdout)


if __name__ == '__main__':
    main()
