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


class FilterTests(unittest.TestCase):

    def _getTargetClass(self):
        from dataflake.fakeldap.queryfilter import Filter
        return Filter

    def _makeOne(self, attribute, comparison, value):
        klass = self._getTargetClass()
        return klass(attribute, comparison, value)

    def test_repr(self):
        fltr = self._makeOne('cn', '=', 'joe')
        self.assertEqual(repr(fltr), "Filter('cn', '=', 'joe')")

    def test_comparison(self):
        fltr = self._makeOne('cn', '=', 'joe')
        
        compare_1 = self._makeOne('cn', '=', 'joe')
        self.assertTrue(fltr == compare_1)

        compare_2 = self._makeOne('CN', '=', 'joe')
        self.assertTrue(fltr == compare_2)

        # Leading or trailing spaces for the value are stripped
        # by real LDAP servers
        compare_3 = self._makeOne('cn', '=', ' joe')
        self.assertTrue(fltr == compare_3)

        compare_4 = self._makeOne('cn', '=', 'joe ')
        self.assertTrue(fltr == compare_4)

        compare_5 = self._makeOne('cn', '=', ' joe ')
        self.assertTrue(fltr == compare_5)

        compare_6 = self._makeOne('cn', '=', 'Joe')
        self.assertFalse(fltr == compare_6)

    def test_sorting(self):
        fltr_1 = self._makeOne('CN', '=', 'Zack')
        fltr_2 = self._makeOne('cn', '=', 'Fred')
        filter_list = [fltr_1, fltr_2]

        filter_list.sort()
        self.assertEqual(filter_list, [fltr_2, fltr_1])

