##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup"""
import os

from setuptools import Extension, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = (open(os.path.join(here, 'README.rst')).read()
          + '\n\n' +
          open(os.path.join(here, 'CHANGES.rst')).read())

setup(
    name='zodbpickle',
    version='0.1.0',
    description='Fork of Python 3 pickle module.',
    author='Python and Zope Foundation',
    author_email='zodb-dev@zope.org',
    url='http://pypi.python.org/pypi/zodbpickle',
    license='PSFL 2 and ZPL 2.1',
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Zope Public License',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: ZODB',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        ],
    platforms=['any'],
    packages=find_packages('src'),
    package_dir = {'':'src'},
    ext_modules = [
        Extension(name='zodbpickle._pickle',
                  sources=['src/zodbpickle/_pickle.c'])
        ],
    extras_require = {
        'test': (),
        'testing': ['nose', 'coverage'],
        },
    test_suite='zodbpickle.tests',
    install_requires=[
        'setuptools',
        ],
    include_package_data=True,
    zip_safe=False
    )
