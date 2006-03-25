# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: $

include ../../makedefs.mak

all:
	python -c "import compileall; compileall.compile_dir('.')"
	
dist:
	mkdir -p ../../$(distdir)/src/javatoolkit/parser
	cp Makefile *.py ../../$(distdir)/src/javatoolkit/
	cp parser/*.py ../../$(distdir)/src/javatoolkit/parser/

install: all
	install -d $(DESTDIR)/usr/share/javatoolkit/pym/parser
	install -m 0644 *.py *.pyc $(DESTDIR)/usr/share/javatoolkit/pym/
	install -m 0644 parser/*.py parser/*.pyc $(DESTDIR)/usr/share/javatoolkit/pym/parser/
