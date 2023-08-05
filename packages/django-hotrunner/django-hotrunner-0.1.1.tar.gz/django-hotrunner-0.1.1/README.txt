#########
HotRunner
#########

HotRunner is an improved django test runner.

To install HotRunner, ``pip install django-hotrunner``.

To use HotRunner, set ``TEST_RUNNER = 'hotrunner.HotRunner'`` in your django 
settings file.  This enables two useful features:

* **Test exclusion:** None of the ``django.contrib`` tests will be run when 
  you run your test suite.  Neither will any apps you specify in the
  ``EXCLUDED_TEST_APPS`` setting.  You can override this without deleting
  your ``EXLUDED_TEST_APPS``, by setting ``TEST_ALL_APPS`` to a true value.
  ``django.contrib`` apps will still not be run.  To run them, specify them
  by name on the manage.py command line:
  ``python manage.py test django.contrib.auth``
* **Test timing:** Find out how long each test is running simply by setting
  your verbosity to 2 or higher.  The time it takes to run each successful 
  test will be reported at microsecond granularity::
 
      $ python manage.py test --verbosity
      test_absolute_url (news.tests.NewsModelAbsoluteURLTestCase) ... (1.103603s) ok
      test_empty_body_returns_empty_html (news.tests.NewsModelMarkdownTestCase) ... (0.000215s) ok
      test_markdown_saved_to_html (news.tests.NewsModelMarkdownTestCase) ... (0.014008s) ok
      test_unicode_markdown_converted_appropriately (news.tests.NewsModelMarkdownTestCase) ... (0.000803s) ok
      test_unicode_strings_must_be_decoded (news.tests.NewsModelMarkdownTestCase) ... (0.000683s) ok
      test_basic_slug_creation (news.tests.NewsModelSlugificationTestCase) ... (0.001656s) ok
      test_existing_slugs_do_not_get_overridden (news.tests.NewsModelSlugificationTestCase) ... (0.000307s) ok
      test_slugifying_disambiguates_slugs (news.tests.NewsModelSlugificationTestCase) ... ERROR

  Tests that fail or error will not report time, as the information is not 
  necessarily relevant if the test is not behaving properly.


Dependencies
============

HotRunner is built for integration with Django as a replacement for its custom 
test runner.  It builds on functionality in unittest2, so it only works with
Django 1.3 or higher.

Changelog
=========

0.1.1
-----

Fixed problem that prevented graceful test abort using ^C on certain python versions.

0.1.0
-----

Initial release.  Features app exclusion and individual test timing.
