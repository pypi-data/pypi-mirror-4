from logbook.compat import LoggingHandler
import platform
import forge
import shakedown
from shakedown.conf import config
if platform.python_version() < "2.7":
    import unittest2 as unittest
else:
    import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self._handler = LoggingHandler()
        self._handler.push_application()
        self.override_config("hooks.swallow_exceptions", False)
        self.override_config("log.console_level", 10000) # silence console in tests
    def override_config(self, path, value):
        self.addCleanup(config.assign_path, path, config.get_path(path))
        config.assign_path(path, value)
    _forge = None
    @property
    def forge(self):
        if self._forge is None:
            self._forge = forge.Forge()
        return self._forge
    _events = None
    @property
    def events(self):
        if self._events is None:
            self._events = self.forge.create_wildcard_mock()
        return self._events
    def tearDown(self):
        if self._forge is not None:
            self._forge.restore_all_replacements()
            self._forge.verify()
        self._handler.pop_application()
        super(TestCase, self).tearDown()

class NullFile(object):
    def write(self, s):
        pass

class CustomException(Exception):
    pass

def no_op(*args, **kwargs):
    pass

def run_tests_assert_success(test_class):
    with shakedown.session.Session() as session:
        with shakedown.suite.Suite():
            shakedown.runner.run_tests(test_class.generate_tests())
    assert session.result.is_success(), "Run did not succeed"
    return session
run_tests_assert_success.__test__ = False
