# Copyright 2012 django-registration-withemail authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from setuptools import setup, find_packages
from compresshtml import __version__

README = open('README.md').read()

setup(
    name = 'django-registration-withemail',
  	version=__version__,
  	packages=find_packages(),
    include_package_data = True,
    license = 'BSD License',
    description = 'This is a simple user-registration application for Django, designed to make allowing user signups as painless as possible.',
    long_description = README,
    author = 'Kamagatos',
    author_email = 'kamagatos@gmail.com',
    install_requires=['django',],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)