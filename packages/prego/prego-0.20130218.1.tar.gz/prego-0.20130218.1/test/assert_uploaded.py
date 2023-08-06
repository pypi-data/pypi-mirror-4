# -*- mode:python; coding:utf-8; tab-width:4 -*-

from hamcrest import contains_string
from prego import TestCase, Task


class Uploaded_checks(TestCase):
    def test_pypi(self):
        URL = 'https://pypi.python.org/pypi/prego'
        task = Task()
        curl = task.command('curl ' + URL)

#        expected = '<title>prego 0.20130116</title>'  # FIXME:unicode error
        expected = '<title>prego 0.20130218'
        task.assert_that(curl.stdout.content, contains_string(expected))
