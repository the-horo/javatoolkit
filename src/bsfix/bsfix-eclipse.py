#! /usr/bin/python2
#
# Copyright(c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright(c) 2004, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/bsfix-eclipse.py,v 1.1 2004/12/20 19:13:05 karltk Exp $

#
# Usage:
#
# bsfix-eclipse --prefix /usr/lib/eclipse-3 --versions 3.0.0,3.0.1 --varnames eclipse_classpath build.properties
#

import os
import re
import sys
import optparse	

import javatoolkit.parser as parser
from javatoolkit.classpath import Classpath

from javatoolkit import die
	
__author__ = "Karl Trygve Kalleberg <karltk@gentoo.org>"
__version__ = "0.1.0"
__productname__ = "bsfix-eclipse"
__description__ = "Gentoo Eclipse Build Script Fixer"
	   
def find_best_version(path, vers):
	for ver in vers:
		x = re.sub("[0-9].[0-9].[0-9]", ver, path)
		if os.path.exists(x):
			return ver
	return None

def resolve_version(doc, var, versions, prefix):

	node = doc.find_node(var)
	oldcp = Classpath(parser.expand(doc, node.value))
	newcp = Classpath()
							
	for i in range(len(oldcp)):
		entry = oldcp[i]
		if entry.startswith(prefix):
			ver = find_best_version(entry, versions)
			if ver is None:
				die(2, "Failed to resolve " + entry)
				
			substed_entry = re.sub("[0-9].[0-9].[0-9]", ver, entry)
			newcp.append(substed_entry)
		else:
			newcp.append(entry)
			
	node.value = str(newcp)
	return node

"""
Print program version to stdout.
"""
def print_version():
	print __productname__ + "(" + __version__ + ") - " + \
		__description__
	print "Author(s): " + __author__

"""
Parse command line arguments
"""
def parse_args():
	
	parser = optparse.OptionParser(version="%prog " + __version__ )

	parser.add_option("-p", "--prefix-path", dest="prefix_path", 
			default="", help="path of Eclipse installation")

	parser.add_option("-a", "--allowed-versions", dest="versions", 
			default=".", help="versions to check for (comma separated)")

	parser.add_option("-n", "--varnames", dest="varnames", 
			default=".", help="attribute names to be considered as classpaths (comma separated)")
	
	(opts, args) = parser.parse_args()		
	opts.varnames = opts.varnames.split(",")
	opts.versions = opts.versions.split(",")
	
	return (opts, args)
	
def main():

	(options, args) = parse_args()

	for arg in args:
		
		doc = parser.buildproperties.parse(open(arg))
		if doc == None:
			raise "File not readable, '" + arg + "'"
		
		for var in options.varnames:
			resolve_version(doc, var, options.versions, options.prefix_path)
				
		doc.dump()

if __name__ == "__main__":
	main()
