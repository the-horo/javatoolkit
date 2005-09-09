# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/Makefile,v 1.4 2005/01/02 02:30:12 axxo Exp $

include ../../makedefs.mak

all:
	
dist:
	mkdir -p ../../$(distdir)/src/buildparser
	cp Makefile buildparser ../../$(distdir)/src/buildparser

install: all
	install -m 0755 buildparser $(bindir)/

