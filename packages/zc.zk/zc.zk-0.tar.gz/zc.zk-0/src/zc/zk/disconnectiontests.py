##############################################################################
#
# Copyright Zope Foundation and Contributors.
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

# This module has tests that involve zookeeper being disconnected.

# Their in a separate module to avoid testing with a real zookeeper
# server, which we can't control (or at least don't want to work hard
# enough to control).

from pprint import pprint
from zope.testing.wait import wait
import zc.zk
import zookeeper
import zope.testing.loggingsupport

def wait_for_zookeeper():
    """
    Normally, zc.zk.ZooKeeper raises an exception if it can't connect
    to ZooKeeper in a short time [#initial_connection_wait]_.  Some
    applications might want to wait, so zc.zk.ZooKeeper accepts a wait
    parameter that causes it to wait for a connection.

    >>> zk = None
    >>> import zc.thread

    >>> handler = zope.testing.loggingsupport.InstalledHandler('zc.zk')

    >>> @zc.thread.Thread
    ... def connect():
    ...     global zk
    ...     zk = zc.zk.ZooKeeper('Invalid', wait=True)

    We'll wait a while while it tries in vane to connect:

    >>> wait((lambda : zk is not None), 4)
    Traceback (most recent call last):
    ...
    TimeOutWaitingFor: <lambda>

    >>> print handler # doctest: +ELLIPSIS
    zc.zk CRITICAL
      Can't connect to ZooKeeper at 'Invalid'
    zc.zk CRITICAL
      Can't connect to ZooKeeper at 'Invalid'
    ...
    >>> handler.uninstall()

    Now, we'll make the connection possible:

    >>> ZooKeeper._allow_connection('Invalid')
    >>> wait(lambda : zk is not None)

    >>> zk.state == zookeeper.CONNECTED_STATE
    True

    Yay!

    >>> zk.close()

    .. [#initial_connection_wait] The initial wait is configurable,
       mainly for testing, via zc.zk.ZooKeeper.initial_connection_wait
    """

def session_timeout_with_child_and_data_watchers():
    """

Set up a session with some watchers:

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')

    >>> handler = zope.testing.loggingsupport.InstalledHandler('zc.zk')

    >>> properties = zk.properties('/fooservice')
    >>> @properties
    ... def changed(a):
    ...     print 'properties changed', a is properties
    properties changed True

    >>> pprint(dict(properties), width=60)
    {u'database': u'/databases/foomain',
     u'favorite_color': u'red',
     u'threads': 1}

    >>> children = zk.children('/fooservice')
    >>> @children
    ... def changed(a):
    ...     print 'children changed', a is children
    children changed True

    >>> sorted(children)
    ['providers']

Now, we'll expire the session:

    >>> handler.clear()
    >>> ZooKeeper.sessions[zk.handle].disconnect()
    >>> ZooKeeper.sessions[zk.handle].expire()
    children changed True
    properties changed True

(Note that we got the handlers called when we reestablished the new
 session.  This is important as the data may have changed between the
 old and new session.)

Now, if we make changes, they'll be properly reflected:

    >>> _ = zk.set('/fooservice', '{"a": 1}')
    properties changed True

    >>> dict(properties)
    {u'a': 1}

    >>> zk.register_server('/fooservice', 'x')
    children changed True

    >>> sorted(children)
    ['providers', 'x']

    >>> print handler
    zc.zk INFO
      connected 0

    """

def session_events_are_ignored_by_child_and_data_watch_support():
    """Session events are send to child, data and exists watcher.

    This should have no impact on the watch support.

    Nothing should get logged. No errors, no warnings.

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> handler = zope.testing.loggingsupport.InstalledHandler('zc.zk')
    >>> @zk.properties('/fooservice')
    ... def p(data):
    ...     print 'property changed'
    property changed

    >>> @zk.children('/fooservice')
    ... def c(data):
    ...     print 'children changed'
    children changed

    >>> node = ZooKeeper._traverse('/fooservice')
    >>> len(node.watchers), len(node.child_watchers)
    (1, 1)

    >>> for state in (zookeeper.CONNECTING_STATE,
    ...               zookeeper.CONNECTED_STATE,
    ...               zookeeper.EXPIRED_SESSION_STATE,
    ...     ):
    ...     for h, w in (node.watchers + node.child_watchers):
    ...         w(h, zookeeper.SESSION_EVENT, state, '')

    >>> print handler,
    >>> handler.uninstall()

    >>> len(node.watchers), len(node.child_watchers)
    (1, 1)

    >>> zk2 = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> p2 = zk2.properties('/fooservice')
    >>> p2.update(z=1)
    property changed
    >>> _ = zk2.create('/fooservice/xxx', '', zc.zk.OPEN_ACL_UNSAFE)
    children changed

    >>> len(node.watchers), len(node.child_watchers)
    (2, 1)

    >>> zk.close()
    >>> zk2.close()
    """
