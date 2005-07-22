# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/findclass/Makefile,v 1.1 2004/08/10 20:06:19 karltk Exp $

include ../../makedefs.mak

all:

dist:
	mkdir -p ../../$(distdir)/src/findclass
	cp {Makefile,AUTHORS,README,TODO,ChangeLog,findclass,findclass.1} ../../$(distdir)/src/findclass

install:
	install -m 0755 findclass $(bindir)/
	install -d $(docdir)/findclass
	install -m 0644 {README,AUTHORS} $(docdir)/findclass/
	install -m 0644 findclass.1 $(mandir)/
