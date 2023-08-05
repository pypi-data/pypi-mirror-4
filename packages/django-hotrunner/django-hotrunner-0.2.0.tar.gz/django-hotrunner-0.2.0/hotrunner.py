import time
from xml.etree import ElementTree as ET

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

# use django's bundled copy of unittest2 if necessary
from django.utils.unittest import TextTestResult, TextTestRunner


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
        return _TimeLoggingTestRunner(
            verbosity=self.verbosity, 
            failfast=self.failfast
        ).run(suite)



class HotRunnerTestResult(TextTestResult):

    @property
    def xunit_filename(self):
        hxf = getattr(settings, 'HOTRUNNER_XUNIT_FILENAME', None)
        juxf = getattr(settings, 'JUXD_FILENAME', None)
        return hxf or juxf

    def startTest(self, test):
        self.case_start_time = time.time()
        super(HotRunnerTestResult, self).startTest(test)

    def addSuccess(self, test):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            self._make_testcase_element(test)
        if self.showAll:
            self.stream.write("(%0.6fs) " % self.case_time_taken)
        super(HotRunnerTestResult, self).addSuccess(test)

    def addFailure(self, test, err):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            testcase = self._make_testcase_element(test)
            test_result = ET.SubElement(testcase, 'failure')
            self._add_tb_to_test(test, test_result, err)
        if self.showAll:
            self.stream.write("(%0.6fs) " % self.case_time_taken)
        super(HotRunnerTestResult, self).addFailure(test, err)

    def addError(self, test, err):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            testcase = self._make_testcase_element(test)
            test_result = ET.SubElement(testcase, 'error')
            self._add_tb_to_test(test, test_result, err)
        if self.showAll:
            self.stream.write("(%0.6fs) " % self.case_time_taken)
        super(HotRunnerTestResult, self).addError(test, err)

    def addUnexpectedSuccess(self, test):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            testcase = self._make_testcase_element(test)
            test_result = ET.SubElement(testcase, 'skipped')
            test_result.set('message', 'Test Skipped: Unexpected Success')
        if self.showAll:
            self.stream.write("(%0.6fs) " % self.case_time_taken)
        super(HotRunnerTestResult, self).addUnexpectedSuccess(test)

    def addSkip(self, test, reason):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            testcase = self._make_testcase_element(test)
            test_result = ET.SubElement(testcase, 'skipped')
            test_result.set('message', 'Test Skipped: %s' % reason)
        super(HotRunnerTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.case_time_taken = time.time() - self.case_start_time
        if self.xunit_filename:
            testcase = self._make_testcase_element(test)
            test_result = ET.SubElement(testcase, 'skipped')
            self._add_tb_to_test(test, test_result, err)
        if self.showAll:
            self.stream.write("(%0.6fs) " % self.case_time_taken)
        super(HotRunnerTestResult, self).addExpectedFailure(test, err)

    def startTestRun(self):
        if self.xunit_filename:
            self.juxtree = ET.Element('testsuite')
        self.run_start_time = time.time()
        super(HotRunnerTestResult, self).startTestRun()

    def stopTestRun(self):
        run_time_taken = time.time() - self.run_start_time
        if self.xunit_filename:
            self.juxtree.set('name', 'Django Project Tests')
            self.juxtree.set('errors', str(len(self.errors)))
            self.juxtree.set('failures' , str(len(self.failures)))
            self.juxtree.set('skips', str(len(self.skipped)))
            self.juxtree.set('tests', str(self.testsRun))
            self.juxtree.set('time', "%.3f" % run_time_taken)

            output = ET.ElementTree(self.juxtree)
            output.write(self.xunit_filename, encoding="utf-8")
        super(HotRunnerTestResult, self).stopTestRun()

    def _make_testcase_element(self, test):
        #time_taken = time.time() - self.case_start_time
        classname = ('%s.%s' % (test.__module__, test.__class__.__name__)).split('.')
        testcase = ET.SubElement(self.juxtree, 'testcase')
        testcase.set('time', "%.6f" % self.case_time_taken)
        testcase.set('classname', '.'.join(classname))
        testcase.set('name', test._testMethodName)
        return testcase

    def _add_tb_to_test(self, test, test_result, err):
        '''Add a traceback to the test result element'''
        exc_class, exc_value, tb = err
        tb_str = self._exc_info_to_string(err, test)
        test_result.set('type', '%s.%s' % (exc_class.__module__, exc_class.__name__))
        test_result.set('message', str(exc_value))
        test_result.text = tb_str


class _TimeLoggingTestRunner(TextTestRunner):
    resultclass = HotRunnerTestResult


