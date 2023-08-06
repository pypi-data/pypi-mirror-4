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
"""ZODB bootstrap helper
"""

# include bootstrap.zcml and off you go

import transaction

import zope.component
from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.app.appsetup.bootstrap import addConfigureUtility
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.session.interfaces import ISessionDataContainer

from cipher.session import interfaces
from cipher.session.session import SessionDataManager


@zope.component.adapter(IDatabaseOpenedWithRoot)
def bootStrapSessionDataManager(event):
    """Subscriber to the IDatabaseOpenedWithRoot

    Constraints: this subscriber must be run after
    zope.app.appsetup.session.bootStrapSubscriber

    Adds/replaces the stock zope ISessionDataManager with our custom one.
    """

    db, connection, root, root_folder = getInformationFromEvent(event)

    try:
        # now first get rid of any ISessionDataContainer
        sm = root_folder.getSiteManager()
        utils = [reg for reg in sm.registeredUtilities()
                 if reg.provided.isOrExtends(ISessionDataContainer)
                    and reg.name == '']
        if utils:
            # check our assumptions: there's only one, registered as a component
            assert len(utils) == 1
            assert utils[0].factory is None
            utility = utils[0].component
            sm.unregisterUtility(utility, ISessionDataContainer)

            try:
                del utility.__parent__[utility.__name__]
            except:
                pass
            transaction.commit()

        utils = [reg for reg in sm.registeredUtilities()
                 if reg.provided.isOrExtends(interfaces.ISessionDataManager)
                    and reg.name == '']
        if utils:
            # check our assumptions: there's only one, registered as a component
            assert len(utils) == 1
            assert utils[0].factory is None
            utility = utils[0].component
            if isinstance(utility, SessionDataManager):
                return  # nothing to do
            sm.unregisterUtility(utility, interfaces.ISessionDataManager)

            try:
                del utility.__parent__[utility.__name__]
            except:
                pass

        addConfigureUtility(
            root_folder,
            interfaces.ISessionDataManager, 'SessionDataManager',
            SessionDataManager,
            )

        transaction.commit()
    except:
        transaction.abort()
        raise
    finally:
        connection.close()
