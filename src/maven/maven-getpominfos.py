#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set ai ts=8 sts=0 sw=8 tw=0 noexpandtab:

# Copyright 2004-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public Licence v2

# Authors:
# kiorky <kiorky@cryptelium.net>:
# Maintainer: Gentoo Java Herd <java@gentoo.org>
# Python based POM navigator

# ChangeLog
# kiorky <kiorky@cryptelium.net>:
# 08/05/2007 initial version


import sys
import StringIO

from optparse import OptionParser, make_option

__version__ = "$Revision: 1.0 $"[11:-2]

class MavenPom:
	def __init__(self,pomfile = ""):
		self.group  = ''
		self.artifact = ''
		self.version = ''
 		self.name = ''
		self.dependencies = []
		self.buffer = StringIO.StringIO()
		self.__write = self.buffer.write

	def getInfos(self,node):
		if node.nodeName == "version":
			self.version = node.childNodes[0].nodeValue
		if node.nodeName == "artifactId":
			self.artifact = node.childNodes[0].nodeValue
		if node.nodeName == "groupId":
			self.group = node.childNodes[0].nodeValue
		if node.nodeName == "name":
			self.name = node.childNodes[0].nodeValue

	def parse(self,in_stream):
		from xml.dom.minidom import parse
		xmldoc = parse(in_stream)

		if xmldoc:
			self.project = xmldoc.getElementsByTagName("project")[0]
			# get our properties
			for node in self.project.childNodes:
				self.getInfos(node)
				if node.nodeName == "dependencies": 
					for dependency_node in node.childNodes: 
						if dependency_node.nodeName == "dependency":  
							dep = MavenPom()
							for child_node in dependency_node.childNodes:  
								dep.getInfos(child_node)
                                                        self.dependencies.append(dep)

			# get inherited properties from parent pom if any
			if self.group == "" or self.version == "" or self.artifact == "":
	 			for node in self.project.childNodes:
	 				if node.nodeName == "parent":
						for child_node in node.childNodes:
							if (
								(child_node.nodeName == "version" and self.version == "" )
								or (child_node.nodeName == "artifactId" and self.artifact == "")
								or (child_node.nodeName == "groupId" and self.group == "")
							):
								self.getInfos(child_node)


if __name__ == '__main__':
	usage = "XML MAVEN POM MODULE " + __version__ + "\n"
	usage += "Copyright 2004,2006,2007 Gentoo Foundation\n"
	usage += "Distributed under the terms of the GNU General Public Lincense v2\n"
	usage += "Please contact the Gentoo Java Team <java@gentoo.org> with problems.\n"
	usage += "\n"
	usage += "Usage:\n"
	usage += "  maven-getpominfos.py [-a] [-v] [-g] [-d] [-f fic.xml]\n"
	usage += "\n"
	usage += "If the -f parameter is not utilized, the script will read and\n"
	usage += "write to stdin and stdout respectively.  The use of quotes on\n"
	usage += "parameters will break the script.\n"

	def error(message):
		print "ERROR: " + message
		sys.exit(1)

	options_list = [
		make_option ("-f", "--file",     action="append",     dest="files",      help="Transform files instead of operating on stdout and stdin"),
		make_option ("-v", "--version" , action="store_true", dest="p_version",  help="get artifact version."),
 		make_option ("-d", "--depependencies" , action="store_true", dest="p_dep",  help="get dependencies infos"), 
		make_option ("-g", "--group"   , action="store_true", dest="p_group",    help="get artifact group."),
		make_option ("-a", "--artifact", action="store_true", dest="p_artifact", help="get artifact name."),
	]


	parser = OptionParser(usage, options_list)
	(options, args) = parser.parse_args()

	# Invalid Arguments Must be smited!
	if not options.p_dep and not options.p_version and not options.p_artifact and not options.p_group:
		print usage
		print
		error("No action was specified.")

		if options.files:
			if options.files.length  > 1:
				error("Please specify only one pom at a time.")
	# End Invalid Arguments Check

	if options.files:
		import os
		for file in options.files:
			# First parse the file into memory
			# Tricks with cwd are needed for relative includes of other xml files to build.xml files
			cwd = os.getcwd()
			dirname = os.path.dirname(file)
			if dirname != '': # for file  comes out as ''
				os.chdir(os.path.dirname(file))

			f = open(os.path.basename(file),"r")
			# parse file
			pom = MavenPom()
			pom.parse(f)
			os.chdir(cwd)
			f.close()
	else:
		# process stdin
		pom = MavenPom()
		pom.parse(sys.stdin)

	if options.p_group:
		print "pom group:%s" % pom.group

	if options.p_artifact:
		print "pom artifact:%s" % pom.artifact

 	if options.p_version:
		print "pom version:%s" % pom.version


  	if options.p_dep:
		i=0
		for dependency in pom.dependencies:
			i=i+1
			print "%d:dep_group:%s" % (i,dependency.group)
 			print "%d:dep_artifact:%s" % (i,dependency.artifact)
 			print "%d:dep_version:%s" % (i,dependency.version)

