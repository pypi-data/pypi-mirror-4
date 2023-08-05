# -*- coding: utf-8 -*-
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


class HashPwdTests(unittest.TestCase):

    def test_hash_pwd(self):
        from dataflake.fakeldap.utils import hash_pwd
        pwd = hash_pwd('secret')
        self.assertTrue(isinstance(pwd, str))
        self.assertTrue(pwd.startswith('{SHA}'))

    def test_hash_unicode_pwd(self):
        from dataflake.fakeldap.utils import hash_pwd
        pwd = hash_pwd(u'bjørn')
        self.assertTrue(isinstance(pwd, str))
        self.assertTrue(pwd.startswith('{SHA}'))

