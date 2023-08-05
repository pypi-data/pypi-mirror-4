#!/usr/bin/env python

# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.restful
#
# lazr.restful is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.restful is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.restful.  If not, see <http://www.gnu.org/licenses/>.

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
def generate(*docname_or_string):
    res = []
    for value in docname_or_string:
        if value.endswith('.txt'):
            f = open(value)
            value = f.read().split('..\n    end-pypi', 1)[0]
            f.close()
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)
# end generic helpers

__version__ = open("src/lazr/restful/version.txt").read().strip()

setup(
    name='lazr.restful',
    version=__version__,
    namespace_packages=['lazr'],
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description=open('README.txt').readline().strip(),
    long_description=generate(
        'src/lazr/restful/README.txt',
        'src/lazr/restful/NEWS.txt'),
    license='LGPL v3',
    install_requires=[
        'docutils',
        'epydoc', # used by wadl generation
        'grokcore.component==1.6',
        'lazr.batchnavigator>=1.2.0-dev',
        'lazr.delegates',
        'lazr.enum',
        'lazr.lifecycle',
        'lazr.uri',
        'martian==0.11',
        'pytz',
        'setuptools',
        'simplejson>=2.1.0',
        'testtools',
        'van.testing',
        'wsgiref',
        'zope.app.pagetemplate',
        'zope.component [zcml]',
        'zope.configuration',
        'zope.event',
        'zope.interface',
        'zope.pagetemplate',
        'zope.processlifetime',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
    url='https://launchpad.net/lazr.restful',
    download_url= 'https://launchpad.net/lazr.restful/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python"],
    extras_require=dict(
        docs=['Sphinx',
              'z3c.recipe.sphinxdoc'],
        xml=['lxml',] # requiring this of normal users is too much
    ),
    test_suite='lazr.restful.tests',
    )
