#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import moma_django


version = moma_django.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='moma-django',
    version='0.1.0',
    description='MoMa-Django provides native Django ORM and admin support for Mongo DB.',
    long_description=readme + '\n\n' + history,
    author='Gadi Oren',
    author_email='gadi.oren.1@gmail.com',
    url='https://github.com/gadio/moma-django',
    packages=[
        'moma_django', 'moma_example',
    ],
    package_dir={'moma_django': 'moma_django', 'moma_example': 'moma_example'},
    include_package_data=True,
    install_requires=[
       'pymongo>=2.1.1', 'djangotoolbox>=0.9.2'
    ],
    license="GPL",
    zip_safe=False,
    keywords='moma-django,mongodb,django',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='tests',
)
