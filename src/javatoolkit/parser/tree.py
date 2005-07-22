#! /usr/bin/python2
#
# Copyright(c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright(c) 2004, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/javatoolkit/parser/tree.py,v 1.1 2004/11/08 19:21:52 karltk Exp $

import sys

class ParseError:
    def __init__(self, error):
        self.error = error

class NodeIter:
    def __init__(self, node):
        self._node = node
        self._index = 0
    def next(self):
        self._index += 1
        if self._index >= len(self._node._kids):
            raise StopIteration
        return self._node._kids[self._index]
        
class Node:
	def __init__(self, name, value):
	    self.name = name
	    self.value = value
	    self._kids = []
	
	def __iter__(self):
	    return NodeIter(self)
	
	def add_kid(self, kid):
	    self._kids.append(kid)
	
	def _dump_kids(self, indent, ous):
	    for x in self._kids:
	        x.dump(indent + 1)
	
	"""
	Dump self as text to stream.
	"""
	def dump(self, indent = 0, ous = sys.stdout,):
	    ous.write((" " * indent) + self.name + " = " + self.value + "\n")
	
	    self._dump_kids(indent, ous)

	"""
	Find a given node name in a tree.
	
	@param tree - the tree to search in
	@param nodename - the name of the node to search for
	
	@return reference to the found node, if any
	"""
	def find_node(self, nodename):
	    for x in self:
	        if x.name == nodename:
	            return x

"""
Node not containing any name=value pair.
"""
class EmptyNode(Node):
	
    def __init__(self):
        Node.__init__(self, "","")

    def dump(self, indent = 0, ous = sys.stdout):
        ous.write("\n")
        self._dump_kids(indent, ous)

	def find_node(self, name):
		return Node.find_node(self, name) 
		
if __name__ == "__main__":
	print "This is not an executable module"		