# -*- coding:utf-8; tab-width:4; mode:python -*-
'''
mail related subjects and assertions
'''

from commodity.type_ import checked_type
from commodity.os_ import SubProcess
from commodity.str_ import Printable
import commodity.mail as mail
from commodity.matchers import meets_imap_query

from . import config
from .assertion import Matcher
from .exc import ConfigError


class IMAP(mail.IMAP):
    def __init__(self, key):
        try:
            account = config.imap[key]
        except KeyError:
            raise ConfigError(
                "Your config file must contain an [imap][%s] section" % key)

        super(IMAP, self).__init__(account)
