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

from ldap.dn import explode_dn


class Filter(object):
    """ A simple representation for search filter elements
    """

    def __init__(self, attr, comp, value):
        self.attr = attr
        self.comp = comp
        self.value = value.strip()

    def __repr__(self):
        return "Filter('%s', '%s', '%s')" % (self.attr, self.comp, self.value)

    def __cmp__(self, other):
        return cmp((self.attr.lower(), self.comp, self.value),
                   (other.attr.lower(), other.comp, other.value))

    def __eq__(self, other):
        v1 = (self.attr.lower(), self.comp, self.value)
        v2 = (other.attr.lower(), other.comp, other.value)
        return v1 == v2

    def __call__(self, tree_pos, base):
        res = []
        query_value = self.value[:]
        wildcard = False

        if query_value.startswith('*') or query_value.endswith('*'):
            if query_value != '*':
                # Wildcard search
                if query_value.startswith('*') and query_value.endswith('*'):
                    wildcard = 'both'
                    query_value = query_value[1:-1]
                elif query_value.startswith('*'):
                    wildcard = 'start'
                    query_value = query_value[1:]
                elif query_value.endswith('*'):
                    wildcard = 'end'
                    query_value = query_value[:-1]

        for rdn, record in tree_pos.items():
            found = True

            if record.has_key(self.attr):
                if query_value == '*':
                    # Always include if there's a value for it.
                    pass
                elif wildcard:
                    found = False
                    for x in record[self.attr]:
                        if wildcard == 'start':
                            if x.endswith(query_value):
                                found = True
                                break
                        elif wildcard == 'end':
                            if x.startswith(query_value):
                                found = True
                                break
                        else:
                            if query_value in x:
                                found = True
                                break
                elif not query_value in record[self.attr]:
                    found = False

                if found:
                    if base.startswith(rdn):
                        dn = base
                    else:
                        dn = '%s,%s' % (rdn, base)
                    res.append((dn, record))

        return res

