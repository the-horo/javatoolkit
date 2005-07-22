#! /usr/bin/env python
#
# Copyright (c) 2004, Karl Trygve Kalleberg <karltk@boblycat.org>

import re
import sys
import time
import codecs
import string
import pprint
import urllib
import httplib
import htmllib
import urlparse
import formatter

ShopURL_pfx = "http://javashoplm.sun.com/ECom/docs/Welcome.jsp?StoreId=22&PartDetailId="
ShopURL_sfx = "&SiteId=JSC&TransactionId=noreg"
InitialURL = "http://java.sun.com/products/archive/"

verbosity = 2

class SnarfHTMLParser(htmllib.HTMLParser):
	def __init__(self, formatter):
		htmllib.HTMLParser.__init__(self, formatter)
		self._urls = []
		self._forms = []
		self._curform = None

	def get_forms(self):
		return self._forms
		
	def get_urls(self):
		return self._urls
		
	def unknown_starttag(self, tag, attributes):
		self._handle_starttag(tag, attributes)

	def unknown_endtag(self, tag):
	    self._handle_endtag(tag)

	def handle_data(self, data):
		pass

	def get_attrib(self, needle, haystack):
		for x in haystack:
			if x[0] == needle:
				return x[1]
		return None
				    
	def _handle_starttag(self, tag, attributes):
		if tag == "a":
			val = self.get_attrib("href", attributes)
			if val:
				self._urls.append(val)
		elif tag == "form":
			action = self.get_attrib("action", attributes)
			self._curform = { "action" : action, "inputs" : {} }
			self._forms.append(self._curform)
		elif tag == "input":
			name = self.get_attrib("name", attributes)
			val = self.get_attrib("value", attributes)
			self._curform["inputs"][name] = val
				
	def _handle_endtag(self, tag):
		if tag == "form":
			self._curform = "None"

	def handle_starttag(self, tag, method, attrs):
	    self._handle_starttag(tag, attrs)

	def handle_endtag(self, tag, method):
	    self._handle_endtag(tag)

def fetchPageOverHTTP(url):
	if verbosity > 1:
	    print "GET " + url

	connector = httplib.HTTPConnection
	protocol = "http://"
	if url.find("https://") == 0:
		protocol = "https://"
		connector = httplib.HTTPSConnection
		
	urlTokens = url.replace(protocol,"").split('/')
	conn = connector(urlTokens[0])
	if verbosity > 2:
	    print urlTokens[0]
	foo = string.join(urlTokens[1:],"/")
	if verbosity > 2:
	    print foo
	conn.request("GET", "/" + foo)
	r1 = conn.getresponse()
	if r1.status == 302:
		url = r1.getheader("Location")
		return fetchPageOverHTTP(url)
	return r1.read()

def fetchTableFromFile(url):
	if verbosity > 1:
	    print "Loading from " + url
	ins = open(url)
	return ins.read()

def stripPreproc(doc):
	rx = re.compile("(<![^>]+>)")
	x = rx.subn("",doc)
	return x[0]


def stripAndParse(parser, doc):
	if verbosity > 1:
	    print "Stripping..."
	doc = stripPreproc(doc)

	if verbosity > 1:
	    print "Parsing..."
	parser.feed(doc)
	return parser
	
def freshParser():
	return SnarfHTMLParser(formatter.NullFormatter(formatter.NullWriter()))

def postForm(url, field_dict):
	urltup = urlparse.urlsplit(url)
	if verbosity > 3:	
		print urltup
	connector = httplib.HTTPConnection
	if urltup[0] == "https":
		connector = httplib.HTTPSConnection
	conn = connector(urltup[1])
	conn.putrequest("POST", urltup[2])
#	conn.putheader('User-Agent',useragent)
#	if cookie <> None: conn.putheader('Cookie',cookie)
	postdata = urllib.urlencode(field_dict)
	conn.putheader('Content-type', 'application/x-www-form-urlencoded')
	conn.putheader('Content-length', '%d' % len(postdata))
	conn.endheaders()
	conn.send(postdata)
	resp = conn.getresponse()
	if resp.status == 200:
		return resp.read()
	else:
		raise "Status %d" % ( resp.status, )

def fetchProduct(productid):
	url = ShopURL_pfx + productid + ShopURL_sfx

	#
	# Get license page 
	#
	if url.find("http://") != 0:
		url = urltup[0] + "://" + urltup[1] + url
		
	doc = fetchPageOverHTTP(url)
	p = stripAndParse(freshParser(), doc)
	forms = p.get_forms()
	license_form = None
	for x in forms:
		if x["action"].find("sdlc") >= 0:
			license_form = x
	license_form["inputs"]["legalAcceptance_5"] = "Yes"
	doc = postForm(license_form["action"], license_form["inputs"])
	p = stripAndParse(freshParser(), doc)
	urls = p.get_urls()
	
	#
	# Get final url list 
	#
	
	rx = re.compile("j2sdk")
	urls = filter(lambda x: rx.search(x), urls)
	rx = re.compile("linux")
	urls = filter(lambda x: rx.search(x), urls)
	rx = re.compile("rpm")
	urls = filter(lambda x: not rx.search(x), urls)
	
	for x in urls:
		print "URL: " + x

def fetchJ2SDK(url):

	urltup = urlparse.urlparse(url)

	#
	# Get initial page
	#
	if len(url) > 4 and url[0:5] == "http:":
		doc = fetchPageOverHTTP(url)
		
	else:
		doc = fetchPageFromFile(url)	    

	p = stripAndParse(freshParser(), doc)
	urls = p.get_urls()
	rx = re.compile("j2sdk|j2se")
	urls = filter(lambda x: rx.search(x), urls)
	rx = re.compile("javashop")
	urls = filter(lambda x: rx.search(x), urls)

	rx = re.compile(".*PartDetailId=(.*)&SiteId.*")
	x = rx.match(urls[0])
	product = x.group(1)

	fetchProduct(product)

def j2sdkFilter(urls):
	rx = re.compile("j2sdk|j2se")
	return filter(lambda x: rx.search(x), urls)

def fetchJ2SDKURL(ver):
	urls = fetchAllVersions()
	rx = re.compile(ver)
	urls = filter(lambda x: rx.search(x), urls)
	if len(urls) > 1:
		sys.stderr.write("Ambiguous version, following found:\n")
		for x in urls:
			sys.stderr.write(x + "\n")
		sys.exit(3)
	if len(urls) == 0:
		print "No version '" + ver + "' found"
		sys.exit(4)
	return urls[0]

def fetchAllVersions():		
	doc = fetchPageOverHTTP(InitialURL)
	p = stripAndParse(freshParser(), doc)
	tok = urlparse.urlsplit(InitialURL)
	urls = j2sdkFilter(p.get_urls())
	return map(lambda x: tok[0] + "://" + tok[1] + x, urls)

def listVersions():
	urls = fetchAllVersions()
	for x in urls:
		print x

def printUsage():
	print "sun-fetch.py --mode [cpv|list|id|url] arg"
					
def downloadByVersion(version):
	url = fetchJ2SDKURL(version)
	downloadByURL(url)
	
def downloadByID(id):
	fetchProduct(id)

def downloadByCPV(cpv):
	pass

def downloadByURL(url):
	fetchJ2SDK(url)

def main():
	global verbosity
	mode = "cpv"
	arg = ""
	skip = 0
	for i in range(1,len(sys.argv)):
		if skip:
			skip -= 1
			continue
		x = sys.argv[i]
		if x in ["-V","--verbose"]:
			verbosity = 10
		elif x in ["-q", "--quiet"]:
			verbosity = 0
		elif x in ["-u", "--url"]:
			url = sys.argv[i + 1]
			skip = 1
		elif x in ["-m", "--mode"]:
			mode = sys.argv[i + 1]
			skip = 1
		else:
			arg = x

	if mode == "cpv":
		downloadByCPV(arg)
	elif mode == "list":
		listVersions()
	elif mode == "url":
		downloadByURL(arg)
	elif mode =="id":
		downloadByID(arg)
	elif mode == "version":
		downloadByVersion(arg)
	else:
		printUsage()
	
if __name__ == "__main__":
	main()
