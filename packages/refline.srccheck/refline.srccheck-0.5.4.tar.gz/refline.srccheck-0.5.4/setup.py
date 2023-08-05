##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
"""Setup for refline.srccheck package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="refline.srccheck",
    version='0.5.4',
    url="http://pypi.python.org/pypi/refline.srccheck/",
    install_requires=[
        'setuptools',
        'pyflakes', 
        'polib',
        'cssutils',
    ],
    extras_require=dict(
        test=[]),
    packages=find_packages('src'),
    package_dir={'': 'src'},

    namespace_packages=['refline'],

    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description="Source checking/linting tool",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords="zope zope3",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    zip_safe=False,
    )
