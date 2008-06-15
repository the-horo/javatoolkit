# Copyright 2008 James Le Cuirot <chewi@aura-online.co.uk>
# Copyright 2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: $

include ../../makedefs.mak

all:
	
dist:
	mkdir -p ../../$(distdir)/src/jarjarclean
	cp Makefile jarjarclean ../../$(distdir)/src/jarjarclean

install: all
	install -m 0755 jarjarclean $(bindir)/

