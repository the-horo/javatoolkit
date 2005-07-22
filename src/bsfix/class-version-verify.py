#!/bin/env python
#
# Copyright(c) 2005, Thomas Matthijs <axxo@gentoo.org>
# Copyright(c) 2005, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/class-version-verify.py,v 1.2 2005/07/19 10:35:18 axxo Exp $

import os,sys
from os.path import join, getsize
from struct import unpack
from optparse import OptionParser, make_option
from zipfile import ZipFile

class cvv:
	def __init__(self, target):
		self.target = target
		self.good = []
		self.bad = []

	def add(self, version, filename):
		if version <= self.target:
			self.good.append(("1."+str(version), filename))
		else:
			self.bad.append(("1."+str(version), filename))

	def do_class(self,filename):
		classFile = file(filename,"rb")
		classFile.seek(4)
		
		temp = classFile.read(4)
		#(version,) = unpack('>i',temp)
		(version,) = unpack('>xxh',temp)
		version-=44

		self.add(version, filename)
	
	def do_jar(self, filename):
		zipfile = ZipFile(filename, 'r')
	
		for file in zipfile.namelist():
			if file.endswith('class'):
				classFile = zipfile.read(file)
				
				(version,) = unpack('>h',classFile[6:8])
				version-=44

				self.add(version, "%s:(%s)" % (filename, file))
	
	def do_file(self, filename):
		if filename.endswith(".class"):
			self.do_class(filename)
		if filename.endswith(".jar"):
			self.do_jar(filename)
	
if __name__ == '__main__':
	
	options_list = [
		make_option ("-r", "--recurse", action="store_true", dest="deep", default=False, help="go into dirs"),
		make_option ("-t", "--target", type="string", dest="version", help="target version that is valid"),

		make_option ("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Print version of every calss"),
		make_option ("-s", "--silent", action="store_true", dest="silent", default=False, help="No output"),
	]

	parser = OptionParser("%prog -t version [-r] [-v] [-s] <class/jar files or dir>", options_list)
	(options, args) = parser.parse_args()

	if not options.version:
		print "-t is mandatory"
		sys.exit(2)

	options.version = int(options.version.split(".")[-1])
	
	cvv = cvv(options.version)

	for arg in args:
		if os.path.isfile(arg):
			cvv.do_file(arg)
			
		if options.deep and os.path.isdir(arg):
			for root, dirs, files in os.walk(arg):
				for filename in files:
					cvv.do_file("%s/%s" % (root, filename))

	if options.verbose:
		for set in cvv.good:
			print "Good: %s %s" % set
		
	if not options.silent:
		for set in cvv.bad:
			print "Bad: %s %s" % set

		print "CVV: %s\nChecked: %i Good: %i Bad: %i" % (options.version, len(cvv.good)+len(cvv.bad) , len(cvv.good), len(cvv.bad))

	if len(cvv.bad) > 0:
		sys.exit(1)
	else:
		sys.exit(0)
