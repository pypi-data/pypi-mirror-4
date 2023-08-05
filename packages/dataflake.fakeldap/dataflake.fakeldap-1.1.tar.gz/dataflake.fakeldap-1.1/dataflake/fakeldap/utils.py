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

import base64
try:
    from hashlib import sha1 as sha_new
except ImportError: #pragma NO COVER
    from sha import new as sha_new #pragma NO COVER


def hash_pwd(string):
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    sha_digest = sha_new(string).digest()
    return '{SHA}%s' % base64.encodestring(sha_digest).strip()

