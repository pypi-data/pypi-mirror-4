# Copyright (c) 2004-2008 Zope Foundation and Contributors
# See also LICENSE.txt
# $Id: __init__.py 5611 2008-02-29 09:43:31Z ctheune $
#
# ZNagios, (C) gocept gmbh & co. kg 2004-2008

import DateTime
import OFS.Application
import Zope2.App.startup
import time
from App.version_txt import getZopeVersion


# Delta used for taking delta measurements and normalization
MUNIN_TIME_DELTA = 60*5


def get_refcount(self):
    """Determine the total amount of object reference counts."""
    all = self.Control_Panel.DebugInfo.refcount()
    size = 0
    for v, n in all:
        size += v
    return size


def get_activity(db, delta=MUNIN_TIME_DELTA):
    now = float(DateTime.DateTime())
    request = dict(chart_start=now-delta,
                   chart_end=now)
    return db.getActivityChartData(200, request)

def get_conflictInfo():
    """from version 2.11 on conflict_errors are not global anymore
    http://svn.zope.org/Zope/tags/2.10.9/lib/python/Zope2/App/startup.py?view=markup
    http://svn.zope.org/Zope/tags/2.11.1/lib/python/Zope2/App/startup.py?view=markup
    """
    major, minor, micro = getZopeVersion()[:3]
    
    # handle zope2.10.11 (shipped with plone3.3.5 that misses the version number
    # see https://bugs.launchpad.net/zope2/+bug/510477
    if major == -1:
        major = 2
        minor = 10
        
    assert major == 2, "ZNagios has been built for Zope2, " \
        "your version seems to be %d" % major

    if minor < 11:
        return Zope2.App.startup
    else:
        #Zope >= 2.11 does not store conflict_errors globally
        return Zope2.App.startup.zpublisher_exception_hook


def uptime(app):
    return app.Control_Panel.process_time().strip()


def dbsize(app):
    size = app.Control_Panel.db_size()
    if size[-1] == "k":
        size = float(size[:-1]) * 1024
    else:
        size = float(size[:-1]) * 1048576
    return size


def nagios(self):
    """A method to allow nagios checks with a bit more information.

    Returns a dictionary line-by-line with the following keys:

    """
    result = ""

    # Uptime
    result += "uptime: %s\n" % uptime(self)

    # Database size
    size = dbsize(self)
    result += "database: %s\n" % int(size)

    # references
    size = get_refcount(self)
    result += "references: %s\n" % size

    # error_log
    errors = self.error_log._getLog()

    i = 0
    for error in errors:
        result += "error%i: %s, %s, %s, %s, %s\n" % (i, error['type'], error['value'],
                    error['username'], error['userid'], error['url'])
        i += 1
    return result


def munin(self, db='main'):
    """Return munin-compatible statistic data."""
    data = {}

    # Uptime
    # ... in seconds since startup
    data['uptime'] = int(time.time())-self.Control_Panel.process_start

    # Reference counts
    # ... total number of objects referenced
    data['refcount-total'] = get_refcount(self)

    db = self.Control_Panel.Database[db]
    # Database size
    # ... in bytes
    data['db-bytes'] = db._getDB()._storage.getSize()
    # ... in number of objects
    data['db-objects'] = db.database_size()

    # Cache information (whole process)
    # ... total number of objects in all caches
    data['db-cache-total-size'] = db.cache_length()

    # Cache information (per connection/thread)
    # ... target size
    data['db-cache-target-size'] = db.cache_size()
    for i, connection in enumerate(db.cache_detail_length()):
        # ... active objects for the connect
        data['db-cache-conn%s-active-objects' % i] = connection['ngsize']
        # ... total objects (active and inactive) for the connection
        data['db-cache-conn%s-total-objects' % i] = connection['size']

    # Activity information
    # measured for the last 5 minutes, normalized per second
    activity = get_activity(db)
    # ... loads per second in the last 5 minutes
    data['db-loads'] = activity['total_load_count'] / MUNIN_TIME_DELTA
    # ... stores per second in the last 5 minutes
    data['db-stores'] = activity['total_store_count'] / MUNIN_TIME_DELTA
    # ... number of connections to the DB per second in the last 5 minutes
    data['db-connections'] = activity['total_connections'] / MUNIN_TIME_DELTA

    # Error information
    # ... number of errors in the log
    data['errors-total'] = len(self.error_log._getLog())
    # ... number of all conflict errors since startup
    data['conflicts-total'] = get_conflictInfo().conflict_errors
    # ... number of all unresolved conflict errors since startup
    data['conflicts-unresolved'] = get_conflictInfo().unresolved_conflict_errors

    # RRDTool: everything's a float
    for key, value in data.items():
        data[key] = float(value)

    self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
    return "\n".join("%s: %s"  % (k, v) for k, v in data.items())


OFS.Application.Application.nagios = nagios
OFS.Application.Application.nagios__roles__ = None


OFS.Application.Application.munin = munin
OFS.Application.Application.munin__roles = None
