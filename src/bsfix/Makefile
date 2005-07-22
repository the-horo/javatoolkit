# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/Makefile,v 1.4 2005/01/02 02:30:12 axxo Exp $

include ../../makedefs.mak

all:
	javac -source 1.4 -target 1.4 JXSLT.java
	
dist:
	mkdir -p ../../$(distdir)/src/bsfix
	cp Makefile JXSLT.java bsfix build-xml-source-target.xslt xml-rewrite.py class-version-verify.py ../../$(distdir)/src/bsfix

install: all
	install -m 0755 bsfix $(bindir)/
	install -d $(DESTDIR)/usr/share/javatoolkit/lib
	install JXSLT.class $(DESTDIR)/usr/share/javatoolkit/lib/
	install build-xml-source-target.xslt ${DESTDIR}/usr/share/javatoolkit/
	install -m 0755 xml-rewrite.py ${bindir}/
	install -m 0755 class-version-verify.py ${bindir}/

