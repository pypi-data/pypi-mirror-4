import time

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

# use django's bundled copy of unittest2 if necessary
from django.utils.unittest.runner import TextTestResult, TextTestRunner

__all__ = ['HotRunner']

class HotRunner(DjangoTestSuiteRunner):
    """This rolls in functionality from several other test runners,
    to make tests slightly awesomer.  In particular:
    
    * Apps can be excluded from the test runner by adding them
      to ``settings.EXCLUDED_TEST_APPS``.  To run all tests in spite
      of this setting, set ``TEST_ALL_APPS`` to a True value.  This
      these settings are overridden by specifying apps on the command
      line.
    * If tests are run with --verbosity=2 or higher, the time taken to
      run each test will be displayed in microseconds.
      """
    
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """ Test runner that only runs tests for the apps
        not listed in ``settings.EXCLUDED_TEST_APPS`` unless ``TEST_ALL_APPS``
        is set or apps are specified on the command line.  This also
        automatically ignores all ``django.contrib`` apps, regardless of
        the state of ``TEST_ALL_APPS``."""

        if not test_labels :
            excluded_apps = getattr(settings, 'EXCLUDED_TEST_APPS', []) 
            if getattr(settings, 'TEST_ALL_APPS', False):
                excluded_apps = []
            test_labels = [x for x in settings.INSTALLED_APPS 
                                 if x not in excluded_apps 
                                 and not x.startswith('django.contrib.')]
        
        return super(HotRunner, self).run_tests(test_labels, extra_tests, **kwargs)

    def run_suite(self, suite, **kwargs):
        if self.verbosity > 1:
            Runner = _TimeLoggingTestRunner
        else:
            Runner = TextTestRunner
        return Runner(
            verbosity=self.verbosity, 
            failfast=self.failfast
        ).run(suite)


class _TimeLoggingTestResult(TextTestResult):
    def startTest(self, test):
        if self.showAll:
            self.latest_test_start_time = time.time()
        return super(_TimeLoggingTestResult, self).startTest(test)

    def addSuccess(self, test):
        if self.showAll:
            if hasattr(self, 'latest_test_start_time'):
                latest_test_run_time = time.time() - self.latest_test_start_time
                self.stream.write("(%0.6fs) " % latest_test_run_time)
                del self.latest_test_start_time
        return super(_TimeLoggingTestResult, self).addSuccess(test)


class _TimeLoggingTestRunner(TextTestRunner):
    resultclass=_TimeLoggingTestResult


