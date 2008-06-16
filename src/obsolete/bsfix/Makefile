# Copyright 2004 Karl Trygve Kalleberg <karltk@gentoo.org>
# Copyright 2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#
# $Header: /var/cvsroot/gentoo-src/javatoolkit/src/bsfix/Makefile,v 1.4 2005/01/02 02:30:12 axxo Exp $

include ../../makedefs.mak

all:

dist:
	mkdir -p ../../$(distdir)/src/bsfix
	cp Makefile bsfix build-xml-source-target.xslt xml-rewrite.py xml-rewrite-2.py xml-rewrite-3.py class-version-verify.py ../../$(distdir)/src/bsfix

install: all
	install -m 0755 bsfix $(bindir)/
	install -d $(DESTDIR)/usr/share/javatoolkit/lib
	install build-xml-source-target.xslt ${DESTDIR}/usr/share/javatoolkit/
	install -m 0755 xml-rewrite.py ${bindir}/
	install -m 0755 xml-rewrite-2.py ${bindir}/
	install -m 0755 xml-rewrite-3.py ${xmlrewritedir}/
	install -m 0755 class-version-verify.py ${bindir}/

testdir:=tests

test:
	# Dom based stuff
	cat $(testdir)/build.xml | ./xml-rewrite-2.py -g > /dev/null
	# Sax based stuff
	cat $(testdir)/build.xml | ./xml-rewrite-2.py \
		--change -e javac -e xjavac -a classpath -v '$${gentoo.classpath}' | grep gentoo.classpath > /dev/null
	cp $(testdir)/build.xml $(testdir)/test.xml
	./xml-rewrite-2.py -f $(testdir)/test.xml \
		--change -e javac -e xjavac -a classpath -v '$${gentoo.classpath}'
	grep gentoo.classpath $(testdir)/test.xml > /dev/null
	rm $(testdir)/test.xml
