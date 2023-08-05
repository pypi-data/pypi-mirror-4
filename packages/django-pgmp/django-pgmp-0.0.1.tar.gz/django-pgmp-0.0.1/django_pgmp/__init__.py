#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === django_pgmp ---------------------------------------------------------===
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

VERSION = (0,0,1, 'final', 0)

def get_version():
  version = '%s.%s' % (VERSION[0], VERSION[1])
  if VERSION[2]:
    version = '%s.%s' % (version, VERSION[2])
  if VERSION[3:] == ('alpha', 0):
    version = '%spre-alpha' % version
  else:
    if VERSION[3] != 'final':
      version = "%s%s" % (version, VERSION[3])
      if VERSION[4] != 0:
        version = '%s%s' % (version, VERSION[4])
  return version

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
