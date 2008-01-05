# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/sun-fetch/Makefile,v 1.2 2004/08/10 20:38:58 karltk Exp $

include ../../makedefs.mak

all:

dist:
	mkdir -p ../../$(distdir)/src/sun-fetch
	cp {Makefile,AUTHORS,README,TODO,ChangeLog,sun-fetch.py,sun-fetch.1} ../../$(distdir)/src/sun-fetch

install:
	install -d $(libdir)/bin
	install -m 0755 sun-fetch $(bindir)/
	install -m 0755 sun-fetch.py $(libdir)/bin
	install -d $(docdir)/sun-fetch
	install -m 0644 {README,AUTHORS} $(docdir)/sun-fetch/
	install -m 0644 sun-fetch.1 $(mandir)/
