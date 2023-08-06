# -*- coding:utf-8; tab-width:4; mode:python -*-
'''
Debian related assertion
'''

from commodity.type_ import checked_type
from commodity.os_ import SubProcess
from commodity.str_ import Printable

from .assertion import Matcher


class Package(Printable):
    def __init__(self, name):
        self.name = checked_type(str, name)

    def __unicode__(self):
        return unicode(self.name)


class DebPackageInstalled(Matcher):
    def _matches(self, package):
        self.package = package
        sp = SubProcess('dpkg -l %s | grep ^ii' % self.package.name, shell=True)
        return not sp.wait()

    def describe_to(self, description):
        description.append_text('package is installed')


def installed():
    return DebPackageInstalled()
