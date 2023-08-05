##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import unittest


class OpTests(unittest.TestCase):

    def _getTargetClass(self):
        from dataflake.fakeldap.op import Op
        return Op

    def _makeOne(self, operator_repr):
        klass = self._getTargetClass()
        return klass(operator_repr)

    def test_repr(self):
        op = self._makeOne('!')
        self.assertEqual(repr(op), "Op('!')")

