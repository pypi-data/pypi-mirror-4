#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === django_pgmp.db.fields.mpq_test.tests --------------------------------===
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

import math
import django.test

try: from cdecimal import Decimal
except: from decimal import Decimal
from fractions import Fraction

from .models import MultiPrecisionFractionModel

class MultiPrecisionFractionModelTests(django.test.TestCase):
    def __init__(self, *args, **kwargs):
        super(MultiPrecisionFractionModelTests, self).__init__(*args, **kwargs)
        self._model = MultiPrecisionFractionModel

    def test_objects_create_successfully(self):
        a = self._model(); a.value = 123; a.save()
        b = self._model(); b.value = 456; b.save()
        self.assertEqual(a.value, 123)
        self.assertEqual(b.value, 456)
        c = self._model(); c.value = 12345678901234567890L; c.save()
        d = self._model(); d.value = 123**456; d.save()
        self.assertEqual(c.value, 12345678901234567890L)
        self.assertEqual(d.value, 99250068772098856700831462057469632637295940819886900519816298881382867104749399077921128661426144638055424236936271872492800352741649902118143819672601569998100120790496759517636465445895625741609866209900500198407153244604778968016963028050310261417615914468729918240685487878617645976939063464357986165711730976399478507649228686341466967167910126653342134942744851463899927487092486610977146112763567101672645953132196481439339873017088140414661271198500333255713096142335151414630651683065518784081203678487703002802082091236603519026256880624499681781387227574035484831271515683123742149095569260463609655977700938844580611931246495166208695540313698140011638027322566252689780838136351828795314272162111222231170901715612355701347552371530013693855379834865667060014643302459100429783653966913783002290784283455628283355470529932956051484477129333881159930212758687602795088579230431661696010232187390436601614145603241902386663442520160735566561L)
        e = self._model(); e.value = '1.34'; e.save()
        f = self._model(); f.value = Decimal('1.34'); f.save()
        g = self._model(); g.value = Fraction(134, 100); g.save()
        self.assertEqual(e.value, Fraction(67, 50))
        self.assertEqual(f.value, Fraction(67, 50))
        self.assertEqual(g.value, Fraction(67, 50))
        h = self._model(); h.value = '123/456'; h.save()
        i = self._model(); i.value = '1/1'+'0'*100; i.save()
        self.assertEqual(h.value, Fraction(123, 456))
        self.assertEqual(i.value, Fraction(1, 10**100))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
