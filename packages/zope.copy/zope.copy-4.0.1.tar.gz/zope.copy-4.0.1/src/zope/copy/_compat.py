##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import sys

PY3 = sys.version_info[0] >= 3

if PY3: #pragma NO COVER
    from pickle import Pickler
    from pickle import Unpickler

    def _get_pid(pickler, oid):
        return pickler.memo.copy()[oid][0] #stupid proxy

    def _get_obj(unpickler, pid):
        return unpickler.memo.copy()[pid]

else: #pragma NO COVER
    from cPickle import Pickler
    from cPickle import Unpickler

    def _get_pid(pickler, oid):
        return pickler.memo[oid][0]

    def _get_obj(unpickler, pid):
        return unpickler.memo[pid]

def _apply(func, args=(), kw=None): # 'apply' is missing in Py3k
    if kw is None:
        kw = {}
    return func(*args, **kw)
