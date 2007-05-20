#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set ai ts=8 sts=0 sw=8 tw=0 noexpandtab:

# Copyright 2004-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public Licence v2

# Authors:
#	Saleem Abdulrasool <compnerd@compnerd.org>
#	Petteri Räty <betelgeuse@gentoo.org>
#	kiorky <kiorky@cryptelium.net>
# Maintainer: Gentoo Java Herd <java@gentoo.org>
# Python based XML modifier

# ChangeLog
# kiorky  <kiorky@cryptelium.net>
#	   May 2007 - Now, all things can be done in one pass, saving us some times :)
#                   - javadoc target generation added
#                   - Rewritten to be more logical
# Petteri Räty <betelgeuse@gentoo.org
#	   December 06, 2006 - Changed to use xml.parsers.expat and basically rewrote the whole file
#	   December 29, 2006 - Added a SAX based implementation to handle entities etc ( test on dev-java/skinlf )
# Saleem A. <compnerd@compnerd.org>
#	   December 23, 2004 - Initial Write
#	   December 24, 2004 - Added usage information

import os
import sys
import StringIO
from xml.sax.saxutils import quoteattr,escape
from optparse import OptionParser, make_option

__version__ = "$Revision: 1.7 $"[11:-2]



class DomRewriter:
	"""
	The old DOM rewriter is still around for index based stuff. It can
	be used for all the complex stuff but portage needed features should
	be in StreamRewriterBase subclasses as they are much faster.
	"""
	from xml.dom import NotFoundErr
	def __init__(self, modifyElems, attributes, values=None, index=None):
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
		matches = document.getElementsByTagName("classpath")
		gcp = document.createElement("location")
		gcp.setAttribute("path","${gentoo.classpath}")

		handled_refs = set()
		for match in matches:
			if match.hasAttribute("refid"):
				refid = match.getAttribute("refid")
				for ref in document.getElementsByTagName("path"):
					id = ref.getAttribute("id")
					if id not in handled_refs and id == refid:
						gcp = document.createElement("pathelement")
						gcp.setAttribute("path","${gentoo.classpath}")
						ref.appendChild(gcp)
						handled_refs.add(id)
					else:
						match.appendChild(gcp)


	def process(self,in_stream,callback=None,*args,**kwargs):
		from xml.dom import minidom
		self.document = minidom.parseString(in_stream);

		if callback:
			callback(self.document,*args,**kwargs)


	def write(self,stream):
		stream.write(self.document.toxml())



#class ExpatRewriter(StreamRewriterBase):
#	"""
#	The only problem with this Expat based implementation is that it does not
#	handle entities doctypes etc properly so for example dev-java/skinlf fails.
#	"""
#	def process(self, in_stream):
#		from xml.parsers.expat import ParserCreate
#		parser = ParserCreate()
#
#		parser.StartElementHandler = self.start_element
#		parser.EndElementHandler = self.end_element
#		parser.CharacterDataHandler = self.char_data
#		parser.ParseFile(in_stream)
#		self.p(u'\n')
#
#
#	def start_element(self, name, attrs):
#		StreamRewriterBase(self, name, attrs.iteritems())
#
#
#	def end_element(self,name):
#		self.p(u'</%s>' % name)



from xml.sax.saxutils import XMLGenerator
class SaxRewriter(XMLGenerator):
	"""
	Using Sax gives us the support for writing back doctypes and all easily
	and is only marginally slower than expat as it is just a tight layer over it
	"""
	def __init__(self, **kwds):
		self.elems = kwds.has_key('elems') and kwds['elems'] or []
		self.attributes = kwds.has_key('attributes') and kwds['attributes'] or []
		self.values = kwds.has_key('values') and kwds['values'] or []
		self.sourceElems = kwds.has_key('sourceElems') and kwds['sourceElems'] or []
		self.sourceAttributes = kwds.has_key('sourceAttributes') and kwds['sourceAttributes'] or []
		self.sourceValues = kwds.has_key('sourceValues') and kwds['sourceValues'] or []
		self.targetElems = kwds.has_key('targetElems') and kwds['targetElems'] or []
		self.targetAttributes = kwds.has_key('targetAttributes') and kwds['targetAttributes'] or []
		self.targetValues = kwds.has_key('targetValues') and kwds['targetValues'] or []

		self.deleteElems = kwds.has_key('deleteElems') and kwds['deleteElems'] or [] 
 		self.deleteAttributes = kwds.has_key('deleteAttributes') and kwds['deleteAttributes'] or []

 		self.src_dirs = kwds.has_key('src_dirs') and kwds['src_dirs'] or []
		self.output_dir = kwds.has_key('output_dir') and kwds['output_dir'] or None

		self.buffer = StringIO.StringIO()

		XMLGenerator.__init__(self, self.buffer, 'UTF-8')


	def add_gentoo_javadoc(self, name, attrs):
		self.p(u'<%s ' % name)
		for a,v in attrs.items():
			self.write_attr(a,v)

		self.p(u'>')

		if name == "project":
			javadoc_str = """
			<target name=\"gentoojavadoc\" >
			<mkdir dir=\"""" + self.output_dir + """\" />
			<javadoc
			destdir=\"""" + self.output_dir + """\"
			author="true"
			version="true"
			use="true"
			windowtitle="javadoc">
			"""

			for src_dir in self.src_dirs:
				javadoc_str += """
				<fileset dir=\"""" + src_dir + """\"    defaultexcludes="yes">
				<include name="**/*.java"/>
				</fileset>
				"""

			javadoc_str += """
			</javadoc>
			</target>
			"""

			self.p(u'%s' % javadoc_str)


	# write as they are or delete if wanted attributes first
	# next, add / update
 	def modify_elements(self, name, attrs):
		self.p(u'<%s ' % name)

		match = ( name in self.elems )
		matchSource = ( name in self.sourceElems )
		matchTarget = ( name in self.targetElems )
		matchDelete = ( name in self.deleteElems )

		for a,v in attrs.items():
			if not (
				(match and a in self.attributes)
				or (matchSource and a in self.sourceAttributes)
				or (matchTarget and a in self.targetAttributes)
				or (matchDelete and a in self.deleteAttributes)
			):
				self.write_attr(a,v)

		if matchSource:
			for i, attr in enumerate(self.sourceAttributes):
				self.write_attr(attr, self.sourceValues[i])

		if matchTarget:
			for i, attr in enumerate(self.targetAttributes):
				self.write_attr(attr, self.targetValues[i])

		if match:
			for i, attr in enumerate(self.attributes):
				self.write_attr(attr, self.values[i])

		self.p(u'>')


	def char_data(self, data):
		self.p(escape(data))


 	def write(self, out_stream):
		value = self.buffer.getvalue()
		out_stream.write(value)
		self.buffer.truncate(0)


	def p(self,str):
		self.buffer.write(str.encode('utf8'))


  	def write_attr(self,a,v):
		self.p(u'%s=%s ' % (a,quoteattr(v, {u'©':'&#169;'})))


	def process(self, in_stream, callback):
		self.startElement = callback
		from xml.sax import parseString
		parseString(in_stream, self)
		self.p(u'\n')


if __name__ == '__main__':
	usage = "XML Rewrite Python Module Version " + __version__ + "\n"
	usage += "Copyright 2004,2006,2007 Gentoo Foundation\n"
	usage += "Distributed under the terms of the GNU General Public Lincense v2\n"
	usage += "Please contact the Gentoo Java Team <java@gentoo.org> with problems.\n"
	usage += "\n"
	usage += "Usage:\n"
	usage += "	" + sys.argv[0] + " [-f file] --delete [-g] -n tag [-n tag] -m attribute [-m attribute] [-i index]\n"
	usage += "	" + sys.argv[0] + " [-f file] --change [-g] -e tag [-e tag] -a attribute -v value [-a attribute -v value] \\\n"
	usage += "			[--source-element tag] [--source-attribute attribute --source-value value] \\\n"
	usage += "			[--target-element tag] [--target-attribute attribute --target-value value] [-i index]\n"
	usage += "Or:\n"
	usage += "	" + sys.argv[0] + " [-f file] --javadoc --source-directory dir [--source-directory dir2] --output-directory dir3 \n"
	usage += "Or:\n"
	usage += "	" + sys.argv[0] + " [-f file] -g\n"
	usage += "\n"
	usage += "Multiple actions can be done simultaneously\n"
	usage += "\n"
	usage += "If the -f parameter is not utilized, the script will read and\n"
	usage += "write to stdin and stdout respectively.  The use of quotes on\n"
	usage += "parameters will break the script.\n"


	def error(message):
		print "ERROR: " + message
		sys.exit(1)


	# instream is a string
	def doRewrite(rewriter, in_stream, callback=None):
		if callback:
			rewriter.process(in_stream, callback)
		else:
			rewriter.process(in_stream)

		out = StringIO.StringIO()
		rewriter.write(out)
		return out.getvalue()


	def processActions(options, f):
		out_stream = f.read()
		if options.gentoo_classpath:
			rewriter = DomRewriter(options.elements, options.attributes, options.values, options.index)
			out_stream = doRewrite(rewriter, out_stream, rewriter.add_gentoo_classpath)

		if options.doJavadoc:
			rewriter = SaxRewriter(src_dirs = options.src_dirs, output_dir = options.javadoc_dir[0])
			out_stream = doRewrite(rewriter, out_stream, rewriter.add_gentoo_javadoc)


		if options.doAdd or options.doDelete:
        		# java-ant-2.eclass does not use these options so we can optimize the ExpatWriter
			# and let the DomRewriter do these. Also keeps the index option compatible for sure. 
 			if options.index:
				rewriter = DomRewriter(options.delete_elements, options.delete_attributes, options.values, options.index)
	 			out_stream = doRewrite(rewriter, out_stream, rewriter.delete_elements) 
			else:
				rewriter = SaxRewriter( elems = options.elements,
						attributes = options.attributes,
						values = options.values,
						sourceElems = options.source_elements,
						sourceAttributes = options.source_attributes,
						sourceValues = options.source_values,
						targetElems = options.target_elements,
						targetAttributes = options.target_attributes,
						targetValues = options.target_values,
 						deleteElems = options.delete_elements,
						deleteAttributes = options.delete_attributes 
						)
 				out_stream = doRewrite(rewriter, out_stream, rewriter.modify_elements) 

		return out_stream


	options_list = [
		make_option ("-a", "--attribute", action="append", dest="attributes", help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs"),
		make_option ("-b", "--target-element", action="append", dest="target_elements", help="Tag of the element of which the attributes to be changed just in target scope.  These can be chained for multiple elements."),
		make_option ("-c", "--change", action="store_true", dest="doAdd", default=False, help="Change the value of an attribute.  If it does not exist, it will be created."),
		make_option ("-d", "--delete", action="store_true", dest="doDelete", default=False, help="Delete an attribute from matching elements."),
		make_option ("-e", "--element", action="append", dest="elements", help="Tag of the element of which the attributes to be changed.  These can be chained for multiple elements."),
		make_option ("-f", "--file", action="append", dest="files", help="Transform files instead of operating on stdout and stdin"),
		make_option ("-g", "--gentoo-classpath", action="store_true", dest="gentoo_classpath", help="Rewrite build.xml to use gentoo.classpath where applicable."),
		make_option ("-i", "--index", type="int", dest="index", help="Index of the match.  If none is specified, the changes will be applied to all matches within the document. Starts from zero."),
		make_option ("-j", "--javadoc", action="store_true", dest="doJavadoc", default=False, help="add a basic javadoc target. Sources must be placed in ${WORKDIR}/javadoc_src."),
		make_option ("-k", "--target-attribute", action="append", dest="target_attributes", help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs (for targetonly)"),
		make_option ("-l", "--target-value", action="append", dest="target_values", help="Value to set the attribute to (targeronly)."),
		make_option ("-m", "--delete-attribute", action="append", dest="delete_attributes", help="Attribute of the matching elements to delete. These can be chained for multiple value-attribute pairs"),
		make_option ("-n", "--delete-element", action="append", dest="delete_elements", help="Tag of the element of which the attributes to be deleted.  These can be chained for multiple elements."),
		make_option ("-o", "--output-directory", action="append", dest="javadoc_dir", help="javadoc output directory. Must be an existing directory"),
		make_option ("-p", "--source-directory", action="append", dest="src_dirs", help="source directory for javadoc generation. Must be an existing directory"),
		make_option ("-r", "--source-element", action="append", dest="source_elements", help="Tag of the element of which the attributes to be changed just in source scope.  These can be chained for multiple elements."),
		make_option ("-t", "--source-attribute", action="append", dest="source_attributes", help="Attribute of the matching elements to change. These can be chained for multiple value-attribute pairs (for source only)"),
		make_option ("-v", "--value", action="append", dest="values", help="Value to set the attribute to."),
		make_option ("-y", "--source-value", action="append", dest="source_values", help="Value to set the attribute to. (sourceonly)")
	]
	parser = OptionParser(usage, options_list)
	(options, args) = parser.parse_args()

	# Invalid Arguments Must be smited!
	if not options.doAdd and not options.doDelete and not options.gentoo_classpath and not options.doJavadoc:
		print usage
		print
		error("No action was specified.")

	if options.doAdd:
		if not options.elements and not options.target_elements and not options.source_elements:
			error("At least one element (global, source only or target only) and attribute must be specified.")

		for elem in ( options.source_attributes or [] ):
			if elem in ( options.attributes or [] ):
				error("You can't set an attribute in global and source scope at the same time")

		for elem in ( options.target_attributes or [] ):
			if elem in ( options.attributes or [] ):
				error("You can't set an attribute in global and target scope at the same time")

		if options.doAdd and (len(options.values or []) != len(options.attributes or [])
			or len(options.source_values or [] ) != len(options.source_attributes or [])
			or len(options.target_values or [] ) != len(options.target_attributes or [])):
			error("You must give attribute(s)/value(s) for every element you are changing.")

	if options.doJavadoc:
		if len(options.src_dirs or []) < 1:
			error("You must specify as least one src directory.")

		for dir in options.src_dirs:
			if not os.path.isdir(dir):
				error("You must specify  existing directory for src output")

		if len(options.javadoc_dir or []) != 1:
			error("You must specify one and only one javadoc output directory.")

		if not os.path.isdir(options.javadoc_dir[0]):
			error("You must specify an existing directory for javadoc output")

	if options.doDelete:
		if not options.delete_elements:
			error("At least one element to delete must be specified.")

		if options.doDelete and ( len(options.attributes or []) < 0):
			error("You must give attribute(s) to delete for every element you are changing.")
			# End Invalid Arguments Check


	# main loop
	if options.files:
		for file in options.files:
			print "Rewriting %s" % file
			# First parse the file into memory
			# Tricks with cwd are needed for relative includes of other xml files to build.xml files
			cwd = os.getcwd()
			dirname = os.path.dirname(file)
			if dirname != '': # for file = build.xml comes out as ''
				os.chdir(os.path.dirname(file))

			f = open(os.path.basename(file), "r")
			outxml = processActions(options, f)
			os.chdir(cwd)
			f.close()
			# Then write it back to the file
			f = open(file, "w")
			f.write(outxml)
			f.close()

	else:
		outxml = processActions(options, sys.stdin)
		sys.stdout.write(outxml)
