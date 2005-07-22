#! /usr/bin/python2
#
# Copyright(c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright(c) 2004, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/bsfix.py,v 1.1 2004/12/20 19:13:05 karltk Exp $

import os
import re
import sys
import optparse

import javatoolkit.parser as parser
from javatoolkit.classpath import Classpath
       
def find_best_version(path, vers):
    for ver in vers:
        x = re.sub("[0-9].[0-9].[0-9]", ver, path)
        if os.path.exists(x):
            return ver
    return None

"""
Parse command line arguments.
"""
def parse_args(args):

	basedir = os.getcwd()

	parser = optparse.OptionParser(version="%prog " + __version__ )

	parser.add_option("-a", "--attribute", dest="attribute", 
			default="", help="select this attribute")

	parser.add_option("-r", "--replace", dest="replace", 
			default=".", help="where to store the generated files")

	parser.add_option("-c", "--cache-file", dest="cachefile",
			default=basedir + "/cache3.db", help="where to store the cache")

	parser.add_option("-m", "--manifest-file", dest="manifestfile",
			default=basedir + "/manifest.synctool", help="where to store the manifest file")

	parser.add_option("-u", "--update-mode", dest="update_mode",
			default="quick", help="update mode, either 'generate' or 'quick'")

	parser.add_option("-v", "--verbose", dest="verbosity",
			default=3, help="verbosity")

	return parser.parse_args()

		        
if __name__ == "__main__":

    infile = sys.argv[1]
    r = parser.buildproperties.parse(open(infile))

    alt_versions = sys.argv[2:]
    
    n = parser.find_node(r, "eclipse_classpath")
    cp = Classpath(n.value)

    for i in range(len(cp)):
        x = cp[i]
        t = parser.expand(r, x)
        if t.startswith("/usr/lib/eclipse-3"):
            ver = find_best_version(t, alt_versions)
            if ver is None:
                print "Failed to resolve " + x
                sys.exit(2)
                
            y = re.sub("[0-9].[0-9].[0-9]", ver, x)
            cp[i] = y

    n.value = str(cp)
    
    r.dump()

