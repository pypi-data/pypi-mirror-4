#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === django_pgmp.db.fields.mpz -------------------------------------------===
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

try:
    from gmpy2 import mpz
except ImportError:
    from gmpy import mpz
from django.db import models

class MultiPrecisionIntegerField(models.IntegerField):
    description = "An arbitrary precision integer type."
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'mpz'

    def get_internal_type(self):
        return "MultiPrecisionIntegerField"

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return mpz(value)
        except (TypeError, ValueError):
            msg = self.error_messages['invalid'] % str(value)
            raise exceptions.ValidationError(msg)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
