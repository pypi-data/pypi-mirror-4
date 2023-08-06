# -*- mode: python; coding: utf-8 -*-

import time

from hamcrest.core.base_matcher import BaseMatcher

from commodity.str_ import Printable
from commodity.log import UniqueFilter
from commodity.pattern import memoizedproperty

from .const import Status, term, INDENTST
from .exc import PregoAssertionFailed, PregoAssertionError, log_traceback
from .item import DeferredItem
from .assert_that import assert_that
from .tools import create_logger, StatusFilter


#-- assertions
class Assertion(Printable):
    def __init__(self, task, client_reason=''):
        self.task = task
        self._client_reason = client_reason

        self.name = "%s.%s" % (task.name, task.gen_assertion_index())
        task.assertions.append(self)

        self.status = Status.NOEXEC
        self._reason = '<no reason>'

    # FIXME: set private
    @memoizedproperty
    def log(self):
        retval = create_logger(self.name)
        retval.addFilter(StatusFilter(self))
        retval.addFilter(UniqueFilter())
        return retval

    def log_status(self, msg=''):
        if msg:
            msg = ': %s' % term().red_bold(msg)

        self.status.log(self.log, "$status   $name %s %s" % (str(self), msg))

    def eval(self):
        self.status = Status.UNKNOWN
        try:
            retval = self.do_eval()
        except PregoAssertionError:
            raise
        except Exception as e:
            self.status = Status.ERROR
            self.log_status()
            log_traceback(prefix='%s| ' % INDENTST)
#            self._reason = e
            raise PregoAssertionError(self)

        if not retval:
            self.status = Status.SOFTFAIL
            raise PregoAssertionFailed(self)

        self.status = Status.SOFTOK

    def terminate(self):
        pass

    def __unicode__(self):
        return self.__class__.__name__


class FailAssertion(Assertion):
    def do_eval(self):
        return False


class DeferredAssertion(Assertion):
    def __init__(self, task, actual, matcher, client_reason=''):
        self._reason = None
        Assertion.__init__(self, task, client_reason)
        self.actual = self.config_actual(actual)
        self.matcher = matcher
        self.evaluated = False
        self.caller = None

        self._reason = "%s %s" % (self.describe_actual(), matcher)

    def config_actual(self, actual):
        if isinstance(actual, DeferredItem):
            actual.config(self.task)

        return actual

    def resolve_actual(self, actual):
        if isinstance(actual, DeferredItem):
            return actual.get_value()

        return actual

    def describe_actual(self):
        try:
            return self.actual.brief()
        except AttributeError:
            return str(self.actual)

    def do_eval(self):
        actual = self.resolve_actual(self.actual)
        try:
            self.evaluated = True
            assert_that(actual, self.matcher, self._client_reason)

        except AssertionError as e:
            self._reason = self.describe_actual() + ' ' + str(e)
            return False

        return True

    def __unicode__(self):
        return u"assert that %s" % self._reason


class PollDeferredAssertion(DeferredAssertion):
    def __init__(self, task, actual, matcher, reason, delta, timeout):
        DeferredAssertion.__init__(self, task, actual, matcher, reason)
        self.timeout = timeout
        self.delta = delta

    def do_eval(self):
        tini = time.time()
        while 1:
            try:
                if time.time() - tini > self.timeout:
                    return False

                assert_that(self.resolve_actual(self.actual),
                            self.matcher, self._client_reason)

                self.log_status()
                return True

            except AssertionError:
                self.status = Status.SOFTFAIL
                time.sleep(self.delta)

    def __unicode__(self):
        return u"wait that %s" % self._reason


class Delay(Assertion):
    def __init__(self, task, n):
        Assertion.__init__(self, task)
        self.n = n

    def do_eval(self):
        time.sleep(self.n)
        return True

    def __unicode__(self):
        return u"Delay %ss" % (self.n)


#-- matchers
class Matcher(BaseMatcher):
#    def brief(self):
#        return u'<matcher>'

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text('it is not')


class Exists(Matcher):
    def _matches(self, item):
        return item.exists()

    def describe_to(self, description):
        description.append_text('exists ')


def exists():
    return Exists()
