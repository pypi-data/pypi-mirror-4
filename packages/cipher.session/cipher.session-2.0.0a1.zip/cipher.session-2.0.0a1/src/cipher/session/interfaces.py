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

import zope.schema

import repoze.session.interfaces


class ISessionDataManager(repoze.session.interfaces.ISessionDataManager):
    timeout = zope.schema.Int(
        title=u"Timeout (seconds)",
        description=u"Number of seconds before data becomes stale and may "
                    u"be removed.",
        default=1 * 60 * 60,
        required=True,
        min=1)
    period = zope.schema.Int(
        title=u"Timeout resolution (in seconds)",
        default=10 * 60,
        required=True,
        min=0)

    def clear():
        """Clear all session data"""
