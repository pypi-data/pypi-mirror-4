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

import ldap
from ldap.dn import explode_dn


class DataStore(dict):

    def addTreeItems(self, dn):
        """ Add structure directly to the tree given a DN 
    
        returns the last added tree position for convenience
        """
        elems = explode_dn(dn)
        elems.reverse()
        tree_pos = self
    
        for elem in elems:
            if not tree_pos.has_key(elem):
                tree_pos[elem] = {}
    
            tree_pos = tree_pos[elem]
    
        return tree_pos

    def getElementByDN(self, dn):
        """ Get a tree element by DN

        Returns None if the path cannot be found
        """
        if isinstance(dn, str):
            elems = explode_dn(dn)
        else:
            elems = dn

        elems.reverse()
        tree_pos = self
    
        for elem in elems:
            if not tree_pos.has_key(elem):
                raise ldap.NO_SUCH_OBJECT(elem)
            else:
                tree_pos = tree_pos[elem]

        return tree_pos

