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
# 31/05/2007 Add rewrite feature
#
# kiorky <kiorky@cryptelium.net>:
# 08/05/2007 initial version


import sys
import StringIO
from optparse import OptionParser, make_option



__version__ = "$Revision: 1.1 $"[11:-2]



# either a very simplified representation of a maven pom
# or a fully xml rewritten pom
class MavenPom:
	def __init__(self,cli_options = None):
		self.group  = ''
		self.artifact = ''
		self.version = ''
		self.name = ''
		self.is_child = "false"
		self.dependencies = []
		self.buffer = StringIO.StringIO()
		self.__write = self.buffer.write
		self.mydoc = None
		self.cli_options = cli_options


	def getInfos(self,node):
		for child_node in node.childNodes:
			if child_node.nodeType == child_node.ELEMENT_NODE:
				if child_node.childNodes[0].nodeValue != "":
					if child_node.nodeName == "version":
						self.version = child_node.childNodes[0].nodeValue

					if child_node.nodeName == "artifactId":
						self.artifact = child_node.childNodes[0].nodeValue

					if child_node.nodeName == "groupId":
						self.group = child_node.childNodes[0].nodeValue

					if child_node.nodeName == "name":
						self.name = child_node.childNodes[0].nodeValue


	def getDescription(self,mydoc,**kwargs):
		if mydoc:
			self.project = mydoc.getElementsByTagName("project")[0]
			# get inherited properties from parent pom if any
			if self.group == "" or self.version == "" or self.artifact == "":
				for node in self.project.childNodes:
					if node.nodeName == "parent":
						self.is_child = "true"
						self.getInfos(node)

			self.getInfos(self.project)

 			# get our deps
			for node in self.project.childNodes:
				if node.nodeName == "dependencies":
					for dependency_node in node.childNodes:
						if dependency_node.nodeName == "dependency":
							dep = MavenPom()
							for child_node in dependency_node.childNodes:
								if child_node.nodeType == child_node.ELEMENT_NODE:
									dep.getInfos(child_node)

							self.dependencies.append(dep)

			if self.cli_options.p_group:
				self.__write("pom group:%s\n" % self.group )

			if self.cli_options.p_ischild:
				self.__write("pom ischild:%s\n" % self.is_child )

			if self.cli_options.p_artifact:
				self.__write("pom artifact:%s\n" % self.artifact )

			if self.cli_options.p_version:
				self.__write("pom version:%s\n" % self.version )

			if self.cli_options.p_dep:
				i=0
				for dependency in self.dependencies:
					i=i+1
					self.__write("%d:dep_group:%s\n" % (i,dependency.group) )
					self.__write("%d:dep_artifact:%s\n" % (i,dependency.artifact) )
					self.__write("%d:dep_version:%s\n" % (i,dependency.version) )


	def read(self):
		return self.buffer.getvalue()


	def rewrite(self,xmldoc,**kwargs):
		# desactivate all dependencies
		dependencies_root = ( xmldoc.getElementsByTagName("dependencies") or [] )
		for node in dependencies_root:
			copylist_child_Nodes =list(node.childNodes)
			for child_node in copylist_child_Nodes:
				node.removeChild(child_node)
				child_node.unlink()

		# add our classpath using system scope
		if self.cli_options.classpath:
			i=0
			dependencies_root = ( xmldoc.getElementsByTagName("dependencies") or [] )
			if dependencies_root:
				for node in dependencies_root:
					for classpath_element in self.cli_options.classpath[0].split(':'):
						dependency_elem = xmldoc.createElement("dependency")
						dependency_elem.appendChild( self.create_element(xmldoc, "groupId", "sexy"))
						dependency_elem.appendChild( self.create_element(xmldoc, "artifactId", "gentoo%d" % (i)))
						dependency_elem.appendChild( self.create_element(xmldoc, "version", "666"))
						dependency_elem.appendChild( self.create_element(xmldoc, "scope", "system"))
						dependency_elem.appendChild( self.create_element(xmldoc, "systemPath", classpath_element))
						node.appendChild(dependency_elem)
						i += 1

		# overwrite source/target options if any
		# remove version node for all plugins
		if self.cli_options.p_source or self.cli_options.p_target:
			dependencies_root = ( xmldoc.getElementsByTagName("plugin") or [] )
			# remove part
			if len(dependencies_root) > 0:
				for node in dependencies_root:
					for child_node in node.childNodes:
						if child_node.nodeName == "version":
							node.removeChild(child_node)
							child_node.unlink()

						if child_node.nodeName == "artifactId":
							if "maven-compiler-plugin" ==  child_node.childNodes[0].data:
								node.parentNode.removeChild(node)
								node.unlink()

			# creation/overwrite part
			plugin_node = self.create_element(xmldoc,"plugin")
			group_node = self.create_element(xmldoc,"groupId","org.apache.maven.plugins")
			artifact_node = self.create_element(xmldoc,"artifactId","maven-compiler-plugin")
			configuration_node = self.create_element(xmldoc,"configuration")
			plugin_node.appendChild(group_node)
			plugin_node.appendChild(artifact_node)
			plugin_node.appendChild(configuration_node)
			if self.cli_options.p_target:
				target_node = self.create_element(xmldoc,"target",self.cli_options.p_target[0])
				configuration_node.appendChild(target_node)

			if self.cli_options.p_source:
				source_node = self.create_element(xmldoc,"source",self.cli_options.p_source[0])
				configuration_node.appendChild(source_node)

 			dependencies_root = ( xmldoc.getElementsByTagName("plugins") or [] )
			for node in dependencies_root:
				node.appendChild(plugin_node)

		from xml.dom.ext import PrettyPrint
		self.write = self.__write
		PrettyPrint(xmldoc,self)
		self.write = None


	def create_element(self,xmldoc,element_name,text_value=None):
		element = None
		if element_name:
			element = xmldoc.createElement(element_name)
			if text_value:
				text_node = xmldoc.createTextNode(text_value)
				element.appendChild(text_node)

		return element


	def parse(self,in_stream,callback=None,**kwargs):
		from xml.dom.minidom import parseString
		self.mydoc = parseString(in_stream)

		if callback:
			callback(self.mydoc,**kwargs)



if __name__ == '__main__':
	usage = "XML MAVEN POM MODULE " + __version__ + "\n"
	usage += "Copyright 2004,2006,2007 Gentoo Foundation\n"
	usage += "Distributed under the terms of the GNU General Public Lincense v2\n"
	usage += "Please contact the Gentoo Java Team <java@gentoo.org> with problems.\n"
	usage += "\n"
	usage += "Usage:\n"
	usage += "  %s [-a] [-v] [-g] [-d] [-f fic.xml]\n" % sys.argv[0]
	usage += "Or:\n"
	usage += "  %s --rewrite [--classpath some.jar:class.jar:path.jar] [--source JVM_VER ] |--target JVM_VER]\n" % sys.argv[0]
	usage += "    JVM_VER ::= 1.4 || 1.5 "
	usage += "\n"
	usage += "If the -f parameter is not utilized, the script will read and\n"
	usage += "write to stdin and stdout respectively.  The use of quotes on\n"
	usage += "parameters will break the script.\n"


	def error(message):
		print "ERROR: " + message
		sys.exit(1)


	def doAction(stream,options):
		pom = MavenPom(options)
		if options.p_rewrite:
			pom.parse(stream, pom.rewrite)
		elif options.p_ischild or options.p_group or options.p_dep or options.p_artifact or options.p_version:
			pom.parse(stream, pom.getDescription)

		return pom


	def run():
		if options.files:
			import os
			for file in options.files:
				# First parse the file into memory
				cwd = os.getcwd()
				dirname = os.path.dirname(file)
				if dirname != '': # for file  comes out as ''
					os.chdir(os.path.dirname(file))

				f = open(os.path.basename(file),"r")
				fs = f.read()
				f.close()
				# parse file and return approtiate pom object
				pom = doAction(fs,options)
				if options.p_rewrite:
					f = open(os.path.basename(file),"w")
					f.write(pom.read())
					f.close()
				else:
					print "%s" % pom.read()

				os.chdir(cwd)

		else:
			# process stdin
			pom = doAction(sys.stdin.read(),options)
			print pom.read()



############### MAIN ###############



	options_list = [
		make_option ("-a", "--artifact", action="store_true", dest="p_artifact", help="get artifact name."),
		make_option ("-c", "--classpath", action="append", dest="classpath", help="set classpath to use with maven."),
		make_option ("-s", "--source", action="append", dest="p_source", help="Java source version."),
		make_option ("-t", "--target", action="append", dest="p_target", help="Java target version."),
		make_option ("-d", "--depependencies" , action="store_true", dest="p_dep",  help="get dependencies infos"),
		make_option ("-f", "--file",     action="append",     dest="files",      help="Transform files instead of operating on stdout and stdin"),
		make_option ("-g", "--group"   , action="store_true", dest="p_group",    help="get artifact group."),
		make_option ("-r", "--rewrite",  action="store_true", dest="p_rewrite", help="rewrite poms to use our classpath"),
		make_option ("-p", "--ischild",  action="store_true", dest="p_ischild", help="return true if this is a child pom"),
		make_option ("-v", "--version" , action="store_true", dest="p_version",  help="get artifact version."),
	]

	parser = OptionParser(usage, options_list)
	(options, args) = parser.parse_args()

	# Invalid Arguments Must be smited!
	if not options.p_ischild and not options.p_rewrite and not options.p_dep and not options.p_version and not options.p_artifact and not options.p_group:
		print usage
		print
		error("No action was specified.")

	if options.files:
		if len(options.files) > 1:
			error("Please specify only one pom at a time.")

	if options.p_rewrite:
		valid_sources = ["1.4","1.5"]
		for source in valid_sources:
			if options.p_source:
				if len(options.p_source) != 1:
					error("Please specify one and only one source.")

				if options.p_source[0] not in valid_sources:
					error("Source %s is not valid" % options.p_source[0])

			if options.p_target:
				if len(options.p_target) != 1:
					error("Please specify one and only one target.")

				if options.p_target[0] not in valid_sources:
					error("Target %s is not valid" % options.p_target[0])

		# join any classpathes if any
		if options.classpath:
			if len(options.classpath) > 1:
				start =[]
				start.append(options.classpath[0])
				for item in options.classpath[1:]:
					start[0] += ":%s" % (item)

				options.classpath = start

	# End Invalid Arguments Check
	# main loop
	run()

