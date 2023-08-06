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
"""A SessionCredentials class that is comparable
"""

from zope.pluggableauth.plugins import session


class SessionCredentials(session.SessionCredentials):
    # this is for session.SessionData._p_resolveConflict
    def __cmp__(self, other):
        if isinstance(other, SessionCredentials):
            if self.login == other.login and self.password == other.password:
                return 0
        return 1

    # I want to be able to see in zodbbrowser the login+password
    def __repr__(self):
        return '%s (%s, %s)' % (self.__class__.__name__,
                                self.login, self.password)
