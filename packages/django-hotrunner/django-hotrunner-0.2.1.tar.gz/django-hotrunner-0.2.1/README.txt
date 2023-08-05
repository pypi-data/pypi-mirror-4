#########
HotRunner
#########

HotRunner is an improved django test runner.

To install HotRunner, ``pip install django-hotrunner``.

To use HotRunner, set ``TEST_RUNNER = 'hotrunner.HotRunner'`` in your django 
settings file.  This enables three useful features:

* **Test exclusion:** None of the ``django.contrib`` tests will be run when 
  you run your test suite.  Neither will any apps you specify in the
  ``EXCLUDED_TEST_APPS`` setting.  You can override this without deleting
  your ``EXCLUDED_TEST_APPS``, by setting ``TEST_ALL_APPS`` to a true value.
  ``django.contrib`` apps will still not be run.  To run them, specify them
  by name on the manage.py command line:
  ``python manage.py test django.contrib.auth``
* **Test timing:** Find out how long each test is running simply by setting
  your verbosity to 2 or higher.  The time it takes to run each successful 
  test will be reported at microsecond granularity::
 
      $ python manage.py test --verbosity=2
      test_absolute_url (news.tests.NewsModelAbsoluteURLTestCase) ... (0.106085s) ok
      test_empty_body_returns_empty_html (news.tests.NewsModelMarkdownTestCase) ... (0.000119s) ok
      test_markdown_saved_to_html (news.tests.NewsModelMarkdownTestCase) ... (0.009840s) ok
      test_unicode_markdown_converted_appropriately (news.tests.NewsModelMarkdownTestCase) ... (0.000501s) ok
      test_unicode_strings_must_be_decoded (news.tests.NewsModelMarkdownTestCase) ... (0.000384s) ok
      test_basic_slug_creation (news.tests.NewsModelSlugificationTestCase) ... (0.000609s) ok
      test_existing_slugs_do_not_get_overridden (news.tests.NewsModelSlugificationTestCase) ... (0.000254s) ok
      test_getting_conflicting_slugs (news.tests.NewsModelSlugificationTestCase) ... (0.001476s) ok
      test_slugifying_disambiguates_slugs (news.tests.NewsModelSlugificationTestCase) ... (0.000204s) ERROR


  Tests that get skipped will not report time, as the information is not 
  relevant.
  
* XUnit style XML output.  If you set ``HOTRUNNER_XUNIT_FILENAME`` to the path
  to a writeable file, HotRunner will write an XML document of test results to
  that file.  This makes it easy to integrate your project with, for instance,
  a Jenkins continuous integration job. For example, the test suite above 
  would look like this (minus the pretty formatting)::

      <testsuite errors="1" failures="0" name="Django Project Tests" skips="0" tests="9" time="0.121">
        <testcase classname="news.tests.NewsModelAbsoluteURLTestCase" name="test_absolute_url" time="0.106085" />
        <testcase classname="news.tests.NewsModelMarkdownTestCase" name="test_empty_body_returns_empty_html" time="0.000119" />
        <testcase classname="news.tests.NewsModelMarkdownTestCase" name="test_markdown_saved_to_html" time="0.009840" />
        <testcase classname="news.tests.NewsModelMarkdownTestCase" name="test_unicode_markdown_converted_appropriately" time="0.000501" />
        <testcase classname="news.tests.NewsModelMarkdownTestCase" name="test_unicode_strings_must_be_decoded" time="0.000384" />
        <testcase classname="news.tests.NewsModelSlugificationTestCase" name="test_basic_slug_creation" time="0.000609" />
        <testcase classname="news.tests.NewsModelSlugificationTestCase" name="test_existing_slugs_do_not_get_overridden" time="0.000254" />
        <testcase classname="news.tests.NewsModelSlugificationTestCase" name="test_getting_conflicting_slugs" time="0.001476" />
        <testcase classname="news.tests.NewsModelSlugificationTestCase" name="test_slugifying_disambiguates_slugs" time="0.000204">
          <error message="list index out of range" type="exceptions.IndexError">Traceback (most recent call last):
              File "/home/jcdyer/.virtualenvs/q2/local/lib/python2.7/site-packages/mock.py", line 1190, in patched
                return func(*args, **keywargs)
              File "/home/jcdyer/projects/q2/quantile2/news/tests.py", line 69, in test_slugifying_disambiguates_slugs
                news = news_items[n]
            IndexError: list index out of range
          </error>
        </testcase>
      </testsuite>

  This functionality was previously available via the ``django-jux`` project.  
  If you are upgrading from ``django-jux``, you can still use the old setting
  name of ``JUXD_FILENAME``, though this is now deprecated, and may disappear
  at some point in the future.


Dependencies
============

HotRunner is built for integration with Django as a replacement for its custom 
test runner.  It builds on functionality in unittest2, so it only works with
Django 1.3 or higher.


Changelog
=========

0.2.1
-----

Fixed issue running tests for apps specified as 'package.app' in ``INSTALLED_APPS``.

0.2.0
-----

Added XUnit-style output, as previously implemented in django-jux.

0.1.1
-----

Fixed problem that prevented graceful test abort using ^C on certain python versions.

0.1.0
-----

Initial release.  Features app exclusion and individual test timing.
