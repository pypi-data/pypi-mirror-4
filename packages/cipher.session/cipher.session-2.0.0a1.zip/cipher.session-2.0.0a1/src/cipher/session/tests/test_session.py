"""`session` module tests"""

from pprint import pprint
import doctest
import zope.component
import zope.component.testing
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IRequest
from zope.session.http import CookieClientIdManager
from zope.session.interfaces import IClientId, IClientIdManager
from zope.session.session import ClientId

from cipher.session import interfaces
from cipher.session import session


@zope.interface.implementer(IClientId)
class ClientIdStub(object):
    zope.component.adapts(IRequest)

    def __init__(self, request):
        pass

    def __str__(self):
        return 'foobar'


class SessionDataStub(dict):
    pass


@zope.interface.implementer(interfaces.ISessionDataManager)
class SessionDataManagerStub(object):

    def __init__(self):
        self._data = {}

    def query(self, key, default=None):
        return self._data.get(key, default)

    def get(self, key):
        if key in self._data:
            return self._data[key]
        else:
            new = SessionDataStub()
            self._data[key] = new
            return new

    def __getitem__(self, key):
        self.get(key)


def doctest_TransientSession():
    """class TransientSession: A session that stores data in the request
    annotations.

      >>> req = TestRequest()
      >>> ses = session.TransientSession(req)

      >>> ses.get('foo', 'DEFAULT')
      'DEFAULT'
      >>> req.annotations
      {}

      >>> foo_data = ses['foo']
      >>> foo_data['one'] = 1
      >>> req.annotations
      {'foo': {('...', 'foo'): {'one': 1}}}
    """


def doctest_Session():
    r"""Test for utils.Session

        >>> sdm = SessionDataManagerStub()
        >>> zope.component.provideUtility(sdm)

        >>> request = TestRequest()
        >>> session = session.Session(request)

        >>> data = session.get('a-package')
        >>> data is None
        True

        >>> data = session['a-package']

        >>> data['foo'] = 'bar'

        >>> data2 = session.get('b-package')
        >>> data2 is None
        True

        >>> session['a-package']
        {'foo': 'bar'}

        >>> pprint(sdm._data)
        {('foobar', 'a-package'): {'foo': 'bar'}}

    """


def doctest_SessionDataManager():
    r"""Test for utils.SessionDataManager

        >>> sdc = session.SessionDataManager()

        >>> sdc.timeout
        3600

        >>> sdc.period
        600

        >>> sdc.nonlazy
        True

        >>> sdc.head
        <ListNode object at ... for ob (..., {}) with next None>

        >>> data = sdc.get('foobar')
        >>> data
        {}

        >>> data['foo'] = 'bar'

        >>> sdc['foobar']
        {'foo': 'bar'}

        >>> sdc.head
        <ListNode object at ... for ob (..., {'foobar': {'foo': 'bar'}}) with next None>

        >>> sdc.clear()

        >>> sdc.head
        <ListNode object at ... for ob (..., {}) with next None>

    """


def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(ClientIdStub)
    zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)


def tearDown(test):
    zope.component.testing.tearDown(test)


def test_suite():
    return doctest.DocTestSuite(
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|
                        doctest.ELLIPSIS|
                        doctest.REPORT_ONLY_FIRST_FAILURE
                        #|doctest.REPORT_NDIFF
                        )
