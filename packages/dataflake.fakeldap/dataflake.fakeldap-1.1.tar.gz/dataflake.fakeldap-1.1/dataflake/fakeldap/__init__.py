##############################################################################
#
# Copyright (c) 2000-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" A fake LDAP module for unit tests
"""

from copy import deepcopy
import ldap
from ldap.dn import explode_dn

from dataflake.fakeldap.db import DataStore
from dataflake.fakeldap.op import Op
from dataflake.fakeldap.queryfilter import Filter
from dataflake.fakeldap.queryparser import Parser
from dataflake.fakeldap.utils import hash_pwd

PARSER = Parser()
ANY = PARSER.parse_query('(objectClass=*)')
TREE = DataStore()


class FakeLDAPConnection:

    hash_password = True
    maintain_memberof = False
    member_attr = 'member'
    memberof_attr = 'memberOf'

    def __init__(self, *args, **kw):
        self.args = args
        self.kwargs = kw
        self.options = {}
        self._last_bind = None
        self.start_tls_called = False
        self.parser = Parser()

    def set_option(self, option, value):
        self.options[option] = value

    def simple_bind_s(self, binduid, bindpwd):
        self._last_bind = (self.simple_bind_s, (binduid, bindpwd), {})

        if 'Manager' in binduid:
            return 1

        if bindpwd == '':
            # Emulate LDAP mis-behavior
            return 1

        if self.hash_password:
            bindpwd = hash_pwd(bindpwd)

        rec = self.search_s( binduid
                           , scope=ldap.SCOPE_BASE
                           , attrs=('userPassword',)
                           )

        rec_pwd = rec[0][1].get('userPassword')

        if not rec_pwd:
            raise ldap.INVALID_CREDENTIALS

        if bindpwd == rec_pwd[0]:
            return 1
        else:
            raise ldap.INVALID_CREDENTIALS

    def _filter_attrs(self, entry, attrs):
        if not attrs:
            return entry
        return dict((k, v) for k, v in entry.items() if k in attrs)

    def search_s(self, base, scope=ldap.SCOPE_SUBTREE,
                 query='(objectClass=*)', attrs=()):

        parsed_query = self.parser.parse_query(query)
        tree_pos = TREE.getElementByDN(base)

        if self.parser.cmp_query(parsed_query, ANY, strict=True):
            # Return all objects, no matter what class
            if scope == ldap.SCOPE_BASE:
                # Only if dn matches 'base'
                return [(base, deepcopy(self._filter_attrs(tree_pos, attrs)))]
            else:
                return [(k, deepcopy(self._filter_attrs(v, attrs))) 
                                                for k, v in tree_pos.items()]

        if scope == ldap.SCOPE_BASE:
            # At this stage tree_pos will be a leaf record. We need to 
            # "re-wrap" it.
            rdn = explode_dn(base)[0]
            tree_pos = {rdn: tree_pos}

        by_level = {}
        enumerated = enumerate(self.parser.explode_query(parsed_query))
        for idx, (operation, filters) in enumerated:
            lvl = by_level[idx] = []
            by_filter = {}
            for fltr in filters:
                sub = fltr(tree_pos, base)
                by_filter[fltr] = sub
                # Optimization: If it's an AND query bail out on
                # the first empty value, but still set the empty
                # value on by_filter so it gets caught in the
                # operations below.
                if not sub and operation.op in ('&',):
                    break

            if filters:
                values = by_filter.values()
            else:
                # If there are no filters, it's an operation on
                # all the previous levels.
                values = by_level.values()

            if operation.op in ('|',):
                # Do an union
                lvl_vals = dict(lvl)
                lvl_keys = set(lvl_vals.keys())
                for sub in values:
                    sub_vals = dict(sub)
                    sub_keys = set(sub_vals.keys())
                    for k in sub_keys - lvl_keys:
                        lvl.append((k, sub_vals[k]))
                    lvl_keys = sub_keys | lvl_keys
            elif operation.op in ('&',):
                # Do an intersection
                for sub in values:
                    # Optimization: If it's an AND query bail out on
                    # the first empty value.
                    if not sub:
                        lvl[:] = []
                        break
                    if not lvl:
                        lvl[:] = sub
                    else:
                        new_lvl = []
                        lvl_vals = dict(lvl)
                        sub_vals = dict(sub)
                        lvl_keys = set(lvl_vals.keys())
                        sub_keys = set(sub_vals.keys())
                        for k in sub_keys & lvl_keys:
                            new_lvl.append((k, lvl_vals[k]))
                        lvl[:] = new_lvl
        if by_level:
            # Return the last one.
            return [(k, deepcopy(self._filter_attrs(v, attrs))) 
                                                    for k, v in by_level[idx]]

        return []

    def add_s(self, dn, attr_list):
        elems = explode_dn(dn)
        rdn = elems[0]
        tree_pos = TREE.getElementByDN(elems[1:])

        if tree_pos.has_key(rdn):
            raise ldap.ALREADY_EXISTS(rdn)

        # Add rdn to attributes as well.
        rdn_key, rdn_value = rdn.split('=')
        tree_pos[rdn] = {rdn_key: [rdn_value]}
        record = tree_pos[rdn]

        for key, value in attr_list:
            record[key] = value

            # Maintain memberOf
            if self.maintain_memberof:
                if key == self.member_attr:
                    for v in value:
                        self.modify_s( v
                                     , [(ldap.MOD_ADD, self.memberof_attr, [dn])]
                                     )

    def delete_s(self, dn):
        elems = explode_dn(dn)
        rdn = elems[0]
        tree_pos = TREE.getElementByDN(elems[1:])

        if not tree_pos.has_key(rdn):
            raise ldap.NO_SUCH_OBJECT(rdn)

        # Maintain memberOf
        if self.maintain_memberof:
            record = tree_pos[rdn]
            if self.member_attr in record:
                for value in record[self.member_attr]:
                    self.modify_s( value
                                 , [(ldap.MOD_DELETE, self.memberof_attr, [dn])]
                                 )
            if self.memberof_attr in record:
                for value in record[self.memberof_attr]:
                    self.modify_s( value
                                 , [(ldap.MOD_DELETE, self.member_attr, [dn])]
                                 )

        del tree_pos[rdn]

    def modify_s(self, dn, mod_list):
        elems = explode_dn(dn)
        rdn = elems[0]
        tree_pos = TREE.getElementByDN(elems[1:])

        if not tree_pos.has_key(rdn):
            raise ldap.NO_SUCH_OBJECT(rdn)

        rec = deepcopy(tree_pos.get(rdn))

        for mod in mod_list:
            if mod[0] == ldap.MOD_REPLACE:
                rec[mod[1]] = mod[2]
            elif mod[0] == ldap.MOD_ADD:
                cur_val = rec.get(mod[1], [])
                cur_val.extend(mod[2])
                rec[mod[1]] = cur_val
            else:
                if rec.has_key(mod[1]):
                    if mod[2] is None:
                        del rec[mod[1]]
                    else:
                        cur_vals = rec[mod[1]]
                        for removed in mod[2]:
                            if removed in cur_vals:
                                cur_vals.remove(removed)

                        rec[mod[1]] = cur_vals

        tree_pos[rdn] = rec

        # Maintain memberOf
        if self.maintain_memberof:
            for mod in mod_list:
                if mod[1] == self.member_attr:
                    if mod[0] == ldap.MOD_ADD:
                        for v in mod[2]:
                            self.modify_s(v, [(ldap.MOD_ADD, self.memberof_attr, [dn])])
                    elif mod[0] == ldap.MOD_DELETE:
                        for v in mod[2]:
                            self.modify_s(v, [(ldap.MOD_DELETE, self.memberof_attr, [dn])])

    def modrdn_s(self, dn, new_rdn, *ign):
        elems = explode_dn(dn)
        rdn = elems[0]
        tree_pos = TREE.getElementByDN(elems[1:])

        if not tree_pos.has_key(rdn):
            raise ldap.NO_SUCH_OBJECT(rdn)

        if tree_pos.has_key(new_rdn):
            raise ldap.ALREADY_EXISTS(new_rdn)

        rec = tree_pos.get(rdn)

        del tree_pos[rdn]
        tree_pos[new_rdn] = rec

    def start_tls_s(self):
        self.start_tls_called = True

    def result(self, msgid=ldap.RES_ANY, all=1, timeout=-1):
        return ('partial', [('partial result', {'dn': 'partial result'})])

    def unbind(self):
        self.unbind_s()

    def unbind_s(self):
        self._last_bind = None


class RaisingFakeLDAPConnection(FakeLDAPConnection):

    def setExceptionAndMethod(self, raise_on, exc_class, exc_arg=None):
        if isinstance(exc_class, (list, tuple)):
            self.exception_list = list(exc_class)
            self.exception_list.reverse()
        else:
            self.exception_list = [exc_class]

        hideaway = '%s_old' % raise_on
        setattr(self, hideaway, getattr(self, raise_on))
        def func(*args, **kw):
            if len(self.exception_list) <= 1:
                setattr(self, raise_on, getattr(self, hideaway))
            setattr(self, 'args', args)
            setattr(self, 'kwargs', kw)

            exc_class = self.exception_list.pop()
            if exc_arg:
                raise exc_class(exc_arg)
            else:
                raise exc_class
        setattr(self, raise_on, func)


class FixedResultFakeLDAPConnection(FakeLDAPConnection):
    search_results = []

    def search_s( self, base, scope=ldap.SCOPE_SUBTREE,
                  query='(objectClass=*)', attrs=() ):
        return self.search_results


class ldapobject:
    class ReconnectLDAPObject(FakeLDAPConnection):
        pass

