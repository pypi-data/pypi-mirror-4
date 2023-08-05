##############################################################################
#
# Copyright (c) 2008-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" unit tests base classes
"""

import unittest

class FakeLDAPTests(unittest.TestCase):

    def setUp(self):
        from dataflake.fakeldap import TREE
        self.db = TREE
        self.db.addTreeItems('ou=users,dc=localhost')
        self.db.addTreeItems('ou=groups,dc=localhost')

    def tearDown(self):
        self.db.clear()

    def _getTargetClass(self):
        from dataflake.fakeldap import FakeLDAPConnection
        return FakeLDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _addUser(self, name, mail=None):
        from dataflake.fakeldap.utils import hash_pwd
        conn = self._makeOne()
        user_dn = 'cn=%s,ou=users,dc=localhost' % name
        user_pwd = '%s_secret' % name

        if conn.hash_password:
            pwd = hash_pwd(user_pwd)
        else:
            pwd = user_pwd

        user = [ ('cn', [name])
               , ('userPassword', [pwd])
               , ('objectClass', ['top', 'person'])
               ]
        if mail is not None:
            user.append(('mail', [mail]))

        conn.add_s(user_dn, user)
        return (user_dn, user_pwd)

    def _addGroup(self, name, members=None):
        conn = self._makeOne()
        group_dn = 'cn=%s,ou=groups,dc=localhost' % name

        group = [ ('cn', [name])
                , ('objectClass', ['top', 'group'])
                ]
        if members is not None:
            members = ['cn=%s,ou=users,dc=localhost' % x for x in members]
            group.append((conn.member_attr, members))

        conn.add_s(group_dn, group)
        return group_dn

