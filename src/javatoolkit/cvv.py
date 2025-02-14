# Copyright 2005, Thomas Matthijs <axxo@gentoo.org>
# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

import os
import sys
from struct import unpack
from zipfile import ZipFile


class CVVMagic:
    def __init__(self, target):
        # this is a number 8 9 10 11 etc, not including 1.
        if '.' in target:
            self.target = int(target.split(".")[-1])
        else:
            self.target = int(target)
        self.good = []
        self.bad = []
        self.skipped = []

    def add(self, version, jar, file):
        if file == "module-info.class" and self.target < 9:
            self.skipped.append((version, jar, file))
        elif version <= self.target:
            if version < 9:
                self.good.append(("1.%s" % (version), jar, file))
            else:
                self.good.append((version, jar, file))
        else:
            if version < 9:
                self.bad.append(("1.%s" % (version), jar, file))
            else:
                self.bad.append((version, jar, file))

    def do_class(self,filename):
        classFile = open(filename,"rb")
        classFile.seek(4)
        temp = classFile.read(4)
        (version,) = unpack('>xxh',temp)
        version -= 44
        self.add(version, None, filename)

    def do_jar(self, filename):
        zipfile = ZipFile(filename, 'r')

        for file in zipfile.namelist():
            if file.endswith('class'):
                classFile = zipfile.read(file)
                (version,) = unpack('>h',classFile[6:8])
                version -= 44
                self.add(version, filename, file)

    def do_file(self, filename):
        if not os.path.islink(filename):
            if filename.endswith(".class"):
                self.do_class(filename)
            if filename.endswith(".jar"):
                self.do_jar(filename)

# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
