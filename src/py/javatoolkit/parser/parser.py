# Copyright(c) 2006, James Le Cuirot <chewi@aura-online.co.uk>
#
# Licensed under the GNU General Public License, v2
#
# $Header: $

class Parser:
    def parse(self, ins):
        raise NotImplementedError
    def output(self, tree):
        raise NotImplementedError       

# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
