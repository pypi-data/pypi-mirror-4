#!/usr/bin/env python
import os
from setuptools import setup
README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-europeana',
    version = '0.1.3',
    packages = ['europeana'],
    include_package_data = True,
    license = 'GNU Affero General Public License v3 or later (AGPLv3+)',
    description = 'Application providing Europeana widget integration.',
    long_description = README,
    url = 'http://www.aksprendimai.lt/',
    author = 'Justinas Jaronis, Inga Pliavgo, Ignas Bacius, Mykolas Baranauskas',
    author_email = 'info@aksprendimai.lt',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)