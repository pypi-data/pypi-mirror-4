# -*- coding:utf-8; tab-width:4; mode:python -*-

import os

from commodity.type_ import checked_type
from commodity.str_ import Printable

from .tools import Interpolator


class DeferredItem(object):
    def __init__(self):
        self.task = None

    def config(self, task):
        self.task = task


class DeferredAttr(DeferredItem):
    "An object attribute delegated for late binding"

    def __init__(self, obj, name, attr):
        self.obj = obj
        self.name = name
        self.attr = attr

    def get_value(self):
        return getattr(self.obj, self.attr)

    def __str__(self):
        return 'future %s.%s' % (self.obj.__class__.__name__, self.name)


class DeferredContent(DeferredItem):
    def __init__(self, out):
        super(DeferredContent, self).__init__()
        self.out = out

    def get_value(self):
        return self.out.read()

    def __str__(self):
        return "{0} content".format(self.out)


class File(Printable):
    def __init__(self, path, fd=None):
        self.path = Interpolator().apply(checked_type(str, path))
        self.fd = fd

    @classmethod
    def from_fd(cls, fd):
        fd = checked_type(file, fd)
        assert not fd.closed, fd
        return File(fd.name, fd)

    def read(self):
        with file(self.path) as fd:
            return fd.read()

    def readline(self):
        with file(self.path) as fd:
            return fd.readline()

    def write(self, data):
        self._assure_open()
        self.fd.write(data)

    def flush(self):
        self._assure_open()
        self.fd.flush()

    @property
    def closed(self):
        return self.fd.closed

    def close(self):
        assert not self.fd.closed
        self.fd.close()

    def _assure_open(self):
        if self.fd is None:
            self.fd = file(self.path, 'w', 0)

        if self.fd.closed:
            raise ValueError('%s was closed' % self.fd.name)

    def find(self, substring):
        raise TypeError("use 'content' attribute to refer file contest")

#        with file(self.path) as fd:
#            return fd.read().find(substring)

    def exists(self):
        return os.path.exists(self.path)

    def remove(self):
        if self.exists():
            os.remove(self.path)

    @property
    def content(self):
        return DeferredContent(self)

#    def get_value(self):
#        return self.read()

    def __unicode__(self):
        return u"File {0!r}".format(self.path)
