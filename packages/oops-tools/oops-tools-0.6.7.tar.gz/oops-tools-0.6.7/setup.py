#!/usr/bin/env python
#
# Copyright 2009-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
def generate(*docname_or_string):
    res = []
    for value in docname_or_string:
        if value.endswith('.txt'):
            f = open(value)
            value = f.read()
            f.close()
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)
# end generic helpers

__version__ = open("src/oopstools/version.txt").read().strip()

setup(
    name='oops-tools',
    version=__version__,
    namespace_packages=[],
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='Launchpad Developers',
    maintainer_email="launchpad-dev@lists.launchpad.net",
    description=open('README.txt').readline().strip(),
    long_description=generate(
        'src/oopstools/README.txt',
        'src/oopstools/NEWS.txt'),
    install_requires=[
        'BeautifulSoup',
        'django',
        'fixtures',
        'launchpadlib',
        'lazr.config',
        'oops',
        'oops-amqp',
        'oops-datedir-repo',
        'oops-wsgi',
        'oops-timeline',
        'psycopg2',
        'pytz',
        'setuptools',
        'South',
        'sqlparse',
        'testtools',
        'timeline',
        'timeline_django',
        'zope.cachedescriptors',
        'zope.testbrowser',
        #'Django', - installed through djangorecipe.
        ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python"],
    extras_require=dict(
        docs=['Sphinx',
              'z3c.recipe.sphinxdoc']
    ),
    entry_points=dict(
        console_scripts=[ # `console_scripts` is a magic name to setuptools
            'amqp2disk = oopstools.scripts.amqp2disk:main',
            'analyse_error_reports = oopstools.scripts.analyse_error_reports:main',
            'load_sample_data = oopstools.scripts.load_sample_data:main',
            'prune = oopstools.scripts.prune:main',
            'update_db = oopstools.scripts.update_db:main',
            'dir_finder = oopstools.scripts.dir_finder:main',
            'report = oopstools.scripts.report:main',
            'graph_report = oopstools.scripts.graph_report:main',
        ]
    ),
    )
