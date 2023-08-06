# -*- mode: python; coding: utf-8 -*-

from commodity.str_ import Printable
from commodity.type_ import checked_type
from commodity.net import is_port_open, is_host_reachable

from .assertion import Matcher


#-- subjects
class Host(Printable):
    def __init__(self, name):
        self.name = checked_type(str, name)

    def __unicode__(self):
        return unicode(self.name)

localhost = Host('localhost')


#-- matchers
class ListenPort(Matcher):
    def __init__(self, port, proto='tcp'):
        self.port = checked_type(int, port)
        assert 0 < port < 65536
        self.proto = proto

    def _matches(self, item):
        self.host = checked_type(Host, item)
        return is_port_open(self.port, self.proto, self.host.name)

    def describe_to(self, description):
        description.append_text('port {0}/{1} to be open'.format(
                self.port, self.proto))

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text('it is closed')


def listen_port(port):
    return ListenPort(port)


class Reachable(Matcher):
    def _matches(self, host):
        self.host = checked_type(Host, host)
        return is_host_reachable(str(host))

    def describe_to(self, description):
        description.append_text("host is reachable")


def reachable():
    return Reachable()
