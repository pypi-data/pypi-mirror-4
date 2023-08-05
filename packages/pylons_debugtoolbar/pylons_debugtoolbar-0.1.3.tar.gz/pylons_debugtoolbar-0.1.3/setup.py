##############################################################################
#
# Copyright (c) 2012 Vitalii Ponomar and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license.
# A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'pylons>=0.9.6',
    'Pygments',
]


setup(
    name='pylons_debugtoolbar',
    version='0.1.3',
    description=(
        'A package which provides an interactive HTML debugger '
        'for Pylons application development'
    ),
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
    ],
    keywords='wsgi pylons debug transaction',
    author="Vitalii Ponomar",
    author_email="vitalii.ponomar@gmail.com",
    url="https://bitbucket.org/ponomar/pylons_debugtoolbar",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points='',
)
