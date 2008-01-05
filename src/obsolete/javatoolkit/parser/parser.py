#! /usr/bin/python
#
# Copyright(c) 2006, James Le Cuirot <chewi@aura-online.co.uk>
#
# Licensed under the GNU General Public License, v2
#
# $Header: $

class Parser:
	def parse(self, ins):
		raise NotImplementedError
	def output(self, tree):
		raise NotImplementedError		

if __name__ == "__main__":
	print "This is not an executable module"	
