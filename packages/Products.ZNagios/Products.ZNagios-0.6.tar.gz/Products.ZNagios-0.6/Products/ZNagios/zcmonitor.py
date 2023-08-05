# -*- coding: utf-8 -*-
import time
import zope.component
import ZODB.interfaces
from Zope2 import app as App

from Products.ZNagios import get_refcount, get_conflictInfo, get_activity


def zc_uptime(connection, database='main'):
    """uptime of the zope instance in seconds"""
    app = App()
    elapsed = time.time() - app.Control_Panel.process_start
    print >> connection, elapsed
    app._p_jar.close()


def zc_dbsize(connection, database='main'):
    """size of the database (default=main) in bytes"""
    db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)
    print >> connection, db.getSize()


def zc_objectcount(connection, database='main'):
    """number of object in the database (default=main)"""
    db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)
    print >> connection, db.objectCount()


def zc_refcount(connection):
    """the total amount of object reference counts"""
    app = App()
    print >> connection, get_refcount(app)
    app._p_jar.close()


def zc_errorcount(connection, objectId=None):
    """number of error present in error_log (default in the root).

    You can also provide the objectId of the object that contains another error_log
    """
    app = App()
    if objectId is not None:
        app = getattr(app, objectId)
    print >> connection, len(app.error_log._getLog())
    app._p_jar.close()


def zc_conflictcount(connection):
    """number of all conflict errors since startup"""
    print >> connection, get_conflictInfo().conflict_errors


def zc_unresolved_conflictcount(connection):
    """number of all unresolved conflict errors since startup"""
    print >> connection, get_conflictInfo().unresolved_conflict_errors


def zc_dbactivity(connection, database='main', last_minutes=60 * 5):
    """number of load, store and connections on database (default=main) for the last x minutes (default=5)"""
    app = App()
    db = app.Control_Panel.Database[database]
    activity = get_activity(db)
    print >> connection, activity['total_load_count'], " ", activity['total_store_count'], " ", activity['total_connections']
    app._p_jar.close()


def zc_requestqueue_size(connection):
    """number of requests waiting in the queue to be handled by zope threads"""
    from ZServer.PubCore import _handle
    queue_size = 0
    if _handle is not None:  # no request yet
        zrendevous = _handle.im_self
        queue_size = len(zrendevous._lists[1])
    print >> connection, queue_size
