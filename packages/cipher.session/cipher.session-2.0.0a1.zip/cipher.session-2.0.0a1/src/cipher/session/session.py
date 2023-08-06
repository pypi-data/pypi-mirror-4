##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
"""Session handling
"""
import pprint

import zope.interface
import zope.component
from persistent import Persistent
from persistent.mapping import PersistentMapping
from ZODB.POSException import ConflictError
from zope.location.location import Location
from zope.publisher.interfaces import IRequest
from zope.session.interfaces import ISession
from zope.session.interfaces import IClientId

from repoze.session import data
from repoze.session import manager

from cipher.session import interfaces
from cipher.session._compat import PY3


class AppendOnlyDict(PersistentMapping):
    # taken from Products.faster.appendict by Tres Seaver
    def __setitem__(self, key, value):
        if key in self.data:
            raise TypeError("Can't update key in AppendOnlyDict!")
        if isinstance(value, (dict, list)):
            raise TypeError("Can't add non-persistent mutable subobjects!")
        if not PY3:
            from types import InstanceType
            if type(value) is InstanceType:
                if not isinstance(value, Persistent):
                    raise TypeError(
                        "Can't add non-persistent mutable subobjects!")
        PersistentMapping.__setitem__(self, key, value)

    def __delitem__(self, key):
        if key in self.data:
            raise TypeError("Can't delete from AppendOnlyDict!")
        PersistentMapping.__delitem__(self, key)

    def _p_resolveConflict(self, old, committed, new):
        """ Resolve competing inserts.

        o Return the resolved state.

        o Raise ConflictError if deltas from old to old->committed collide
          with those from old->new.
        """
        if not committed or not new:
            raise ConflictError("Can't resolve 'clear'")

        result = old.copy()
        c_new = {}

        for k, v in committed.items():
            if k not in result:
                c_new[k] = 1
                result[k] = v

        for k, v in new.items():
            if k in old:
                continue
            if k in c_new:
                raise ConflictError("Conflicting insert")
            result[k] = v

        return result


class SessionData(data.SessionData):

    # ZODB conflict resolution (to prevent write conflicts)
    # parts/inspiration taken from repoze.session

    def _getData(self, state):
        # happens that PersistentMapping was refactored to 'data' instead
        # of '_container', be forgiving about which item we use
        try:
            return state['_container']
        except KeyError:
            return state['data']

    def _p_resolveConflict(self, old, committed, new):
        # dict modifiers set '_lm'.
        if committed['_lm'] != new['_lm']:
            # we are operating against the PersistentMapping.__getstate__
            # representation, which aliases '_container' to self.data.

            # for this to work perfectly, you better put comparable items
            # into the session
            # if they don't compare naturally, add a __cmp__ method
            cd = self._getData(committed)
            nd = self._getData(new)

            try:
                neq = (cd != nd)
            except ValueError:
                neq = True
            if neq:
                msg = "Competing writes to session data: \n%s\n----\n%s" % (
                        pprint.pformat(cd),
                        pprint.pformat(nd))
                raise ConflictError(msg)

        resolved = dict(new)
        invalid = committed.get('_iv') or new.get('_iv')
        if invalid:
            resolved['_iv'] = True
        resolved['_lm'] = max(committed['_lm'], new['_lm'])
        return resolved


@zope.interface.implementer(interfaces.ISessionDataManager)
class SessionDataManager(manager.SessionDataManager, Location):

    # We have the option of using an OOBTree as a bucket type or an
    # AppendOnlyDict as a bucket type.  With an AppendDict in place,
    # zero conflicts are generated when bucket nodes are mutated
    # because we can resolve all conflicts.  With an OOBTree in place,

    _BUCKET_TYPE = AppendOnlyDict

    # Make the data type replaceable for unit tests.
    _DATA_TYPE = SessionData

    def __init__(self):
        # some init values from zope.session
        super(SessionDataManager, self).__init__(1 * 60 * 60, 10 * 60)
        # houston, we got a problem with ftests
        self.nonlazy = True

    def clear(self):
        self.head = self.new_head(None)

    def __getitem__(self, key):
        return self.get(key)


@zope.interface.implementer(ISession)
class Session(object):
    """See zope.session.interfaces.ISession"""
    zope.component.adapts(IRequest)

    def __init__(self, request):
        self.client_id = str(IClientId(request))

    def _sdc(self, pkg_id):
        return zope.component.getUtility(interfaces.ISessionDataManager)

    def get(self, pkg_id, default=None):
        sdc = self._sdc(pkg_id)

        # flat SessionDataManager/SessionData structure
        # still have a feeling that updating leaf objects won't update
        # last_modified time
        ident = (self.client_id, pkg_id)

        return sdc.query(ident, default)

    def __getitem__(self, pkg_id):
        sdc = self._sdc(pkg_id)
        ident = (self.client_id, pkg_id)
        return sdc.get(ident)


class TransientSession(object):
    """Session data stored on the request
    """

    # handy if you do not want to store any session data at all
    # for e.g. zope.Public views

    def __init__(self, request):
        self.client_id = str(IClientId(request))
        self.request = request

    def get(self, pkg_id, default=None):
        sdc = self.request.annotations.get(pkg_id)
        if sdc is None:
            return default
        ident = (self.client_id, pkg_id)
        return sdc.get(ident, default)

    def __getitem__(self, pkg_id):
        sdc = self.request.annotations.setdefault(pkg_id, {})
        ident = (self.client_id, pkg_id)
        return sdc.setdefault(ident, {})
