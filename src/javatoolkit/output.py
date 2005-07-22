#! /usr/bin/python2
#
# Copyright(c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright(c) 2004, Gentoo Foundation
#
# Licensed under the GNU General Public License, v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/javatoolkit/output.py,v 1.1 2004/11/08 19:21:52 karltk Exp $

import sys

# FIXME: Use gentoolkit stuff instead

def eerror(s):
	sys.stderr.write("!!! " + s + "\n")

def ewarn(s):
	sys.stdout.write("* " + s + "\n")

def einfo(s):
	sys.stdout.write("* " + s + "\n")

def die(err, s):
	eerror(s)
	sys.exit(err)
	
if __name__ == "__main__":
	print "This is not an executable module"