#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === setup.py ------------------------------------------------------------===
# This file is part of django-pgpm. django-pgpm is copyright © 2012, RokuSigma
# Inc. and contributors. See AUTHORS and LICENSE for more details.
#
# django-pgpm is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# django-pgpm is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-pgpm. If not, see <http://www.gnu.org/licenses/>.
# ===----------------------------------------------------------------------===

import os

from distutils.core import setup

from django_pgmp import get_version

# Compile the list of packages available, because distutils doesn't have an
# easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('django_pgmp'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        # Strip “django_patterns/” or “django_patterns\”:
        prefix = dirpath[len('django_pgmp')+1:]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='django-pgmp',
    version=get_version().replace(' ', '-'),
    description='Django ORM types for PostgreSQL multi-precision numeric types.',
    author='Mark Friedenbach',
    author_email='mark@monetize.io',
    url='http://www.github.com/monetizeio/django-pgmp/',
    download_url='http://github.com/monetizeio/django-pgmp/tarball/master',
    package_dir={'django_pgmp': 'django_pgmp'},
    packages=packages,
    package_data={'django_pgmp': data_files},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
