#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Test Units
"""

import unittest
from . import *

class WineDatabaseTests(unittest.TestCase):

  def test01_wine(self):
    self.assertEqual(len(names), 13)
    wdict = data()
    self.assertEqual(len(wdict), 3)
    self.assertEqual(len(wdict['wine1']), 59)
    self.assertEqual(len(wdict['wine2']), 71)
    self.assertEqual(len(wdict['wine3']), 48)

