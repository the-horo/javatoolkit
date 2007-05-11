# Copyright 2004-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: $

include ../../makedefs.mak

all:

dist:
	mkdir -p ../../$(distdir)/src/maven
	cp Makefile maven-getpominfos.py ../../$(distdir)/src/maven

install: all
	install -m 0755 maven-getpominfos.py $(bindir)/

testdir:=tests

test:
	echo "nothing atm"

