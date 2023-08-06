#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup


PROJECT = u'screp'
VERSION = '0.3'
URL = 'https://github.com/darfire/screp'
AUTHOR = u'Doru Arfire'
AUTHOR_EMAIL = u'doruarfire@gmail.com'
DESC = u'Command-line utility for easy scraping of HTML documents'

requires = [
        'pyparsing',
        'lxml',
        ]

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    namespace_packages=[],
    packages=[u'screp'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points = {
        'console_scripts': [
            'screp=screp.main:main',
            ],
    },
    classifiers=[
        # -*- Classifiers -*- 
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        "Programming Language :: Python",
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
