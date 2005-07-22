#! /usr/bin/python2
#
# Copyright(c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright(c) 2004, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/javatoolkit/parser/buildproperties.py,v 1.3 2004/11/08 19:31:51 karltk Exp $

from tree import *

def parse(ins):
	""" Parse an input stream containing an ant build.properties file. Return a 
	structured document represented by tree.Node
	
	@param ins - input stream
	@return tree.Node containing the structured representation
	"""
	
	lineno = 0
	continued_line = False
	attrib = None
	value = None
	root = EmptyNode()
	
	for x in ins.readlines():
		lineno += 1
	
		if continued_line:
			continued_line = False
			value += x.strip().strip("\"")
			
			if len(value) and value[-1] == "\\":
				value = value[:-1]
				continued_line = True
				continue
				
			root.add_kid(Node(attrib,value))
			continue
			
		xs = x.split("=")
		
		if len(xs) > 1:
			attrib = xs[0]
			value = ("=".join(xs[1:]).strip("\n")).strip("\"")
			
			if value[-1] == "\\":
				value = value[:-1]
				continued_line = True
				continue
			
			root.add_kid(Node(attrib,value))
		
		elif x.strip() == "":
			root.add_kid(EmptyNode())
		else:
			raise ParseError("Malformed line " + str(lineno))
			
	return root

if __name__ == "__main__":
	print "This is not an executable module"	