#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from prego import TestCase, Task
from prego.mail import IMAP, meets_imap_query


class imap(TestCase):
    def test_imap_from_config(self):
        task = Task()
        mailbox = IMAP('default')
        task.assert_that(mailbox, meets_imap_query('(SUBJECT X2)'))
