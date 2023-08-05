#!/usr/bin/env python

_home_page = 'http://bitbucket.org/metametrics/django-hotrunner'
_short_description = 'HotRunner is a Django test runner with useful features, like excluding apps and displaying running times of individual tests.'
_long_description = open('README.txt').read()

try:
    from distutils2.core import setup
    additional_options = {
        'home_page': _home_page,
        'summary': _short_description,
        'description': _long_description,
    }
        
except ImportError:
    from distutils.core import setup
    additional_options = {
        'url': _home_page,
        'description': _short_description,
        'long_description': _long_description,
    }

setup(
    name='django-hotrunner',
    version='0.2.0',
    author='MetaMetrics',
    author_email='engineering@lexile.com',
    py_modules=['hotrunner'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    **additional_options
)
