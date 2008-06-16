#!/usr/bin/env python

# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

from distutils.core import setup

setup (
    name = 'javatoolkit',
    version = '0.2.1',
    description = 'Collection of Gentoo-specific tools for Java.',
    maintainer = 'Gentoo Java Team',
    maintainer_email = 'java@gentoo.org',
    url = 'html://www.gentoo.org',
    packages = ["javatoolkit", "javatoolkit.maven", "javatoolkit.xml", "javatoolkit.parser"],
    package_dir = { 'javatoolkit' : 'src/py/javatoolkit' },
    scripts = [
        "src/py/maven-helper.py", 
        "src/py/xml-rewrite-3.py",
        "src/py/findclass",
        "src/py/xml-rewrite.py",
        "src/py/xml-rewrite-2.py",
        "src/py/buildparser",
        "src/py/class-version-verify.py",
        "src/py/build-xml-rewrite",
        "src/py/jarjarclean"
    ],
    data_files = [ ( '/usr/share/man/man1', ['src/man/findclass.1'] ) ]
)

#set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap 
