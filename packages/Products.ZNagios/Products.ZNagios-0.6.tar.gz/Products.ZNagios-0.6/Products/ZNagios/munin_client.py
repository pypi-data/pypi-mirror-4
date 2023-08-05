#!/usr/bin/python
# -*- coding: latin-1 -*-
# Copyright (c) 2008 Zope Foundation and Contributors
# See also LICENSE.txt
# $Id$
"""munin client script for ZNagios.

Reads the Zope server URL from sys.env['MUNIN_ZOPE_HOST_<index>']
where the index is the number appended to the script's name when called.

"""

import os.path
import urllib2
import base64
import sys

if len(sys.argv) == 1:
    cmd = 'fetch'
else:
    cmd = sys.argv[1]

if cmd == '':
    cmd = 'fetch'

script_name = os.path.basename(sys.argv[0])
try:
	_, graph, server_index, dbname = script_name.split('_')
except ValueError:
	_, graph, server_index = script_name.split('_')
	dbname = 'main'

URL = os.environ['MUNIN_ZOPE_HOST_%s' % server_index]
AUTHORIZATION = os.environ.get('MUNIN_ZOPE_AUTHENTICATE_%s' % server_index)

class GraphBase(object):

    def _prepare_fetch(self):

        url = URL + '?db=%s' % dbname
        request = urllib2.Request(url)
        if AUTHORIZATION:
            request.add_header('Authorization', 'Basic %s' %
                               base64.encodestring(AUTHORIZATION))
        result = urllib2.urlopen(request).readlines()
        self.data = {}
        for line in result:
            key, value = line.split(':')
            self.data[key] = float(value)

    def fetch(self):
        self._prepare_fetch()
        self.do_fetch()


class SimpleGraph(GraphBase):

    title = ''
    name = ''
    key = ''
    vlabel = ''  #label for y-axis, use name if vlabel is not specified
    cdef = ''   #rpn-expression used to compute the value (eg `%s,86400,/') to devide the value by 86400


    def do_fetch(self):
        print "%s.value %s" % (self.name, self.data[self.key])

    def config(self):
        print "graph_title %s (Zope %s/%s)" % (self.title, server_index, dbname)
        print "graph_vlabel %s" % (self.vlabel or self.name)
        print "graph_category Zope"
        print "graph_info %s of Zope %s, database %s " % (self.title, server_index, dbname)
        print "%s.label %s" % (self.name, self.name)
        if self.cdef:
            print "%s.cdef " % self.name + self.cdef % self.name


class SimpleMultiGraph(GraphBase):

    title = ''
    vlabel = ''
    keys = []
    names = []

    def do_fetch(self):
        for key, name in zip(self.keys, self.names):
            print "%s.value %s" % (name, self.data[key])

    def config(self):
        print "graph_title %s (Zope %s/%s)" % (self.title, server_index, dbname)
        print "graph_vlabel %s" % (self.vlabel)
        print "graph_category Zope"
        print "graph_info %s of the Zope %s, database %s" % (self.title, server_index, dbname)
        for name in self.names:
            print "%s.label %s" % (name, name)


class uptime(SimpleGraph):
    """uptime in days"""


    key = name = 'uptime'
    title = 'Uptime'
    vlabel = 'days'
    cdef = '%s,86400,/'


class refcount(SimpleGraph):

    key = 'refcount-total'
    name = 'refcount'
    title = 'Reference count'


class errors(SimpleMultiGraph):

    keys = ['errors-total', 'conflicts-total', 'conflicts-unresolved']
    names = ['errors', 'conflicts', 'conflicts_unresolved']
    title = vlabel = 'Errors'

class activity(SimpleMultiGraph):

    keys = ['db-loads', 'db-stores', 'db-connections']
    names = ['loads', 'stores', 'connections']
    title = 'Activity'
    vlabel = 'Operations'

class cachetotals(SimpleGraph):

    key = 'db-cache-total-size'
    name = 'cache_size'
    title = 'Total cache size'

class dbsize(SimpleGraph):
    """Database Size in MB.
    """

    key = 'db-bytes'
    name = 'database_size'
    title = 'Size of Database'
    vlabel = 'MB'
    cdef = '%s,1048576,/'



class cacheconnections(GraphBase):

    def do_fetch(self):
        i = 0
        while True:
            active = self.data.get('db-cache-conn%s-active-objects' % i)
            if active is None:
                break
            total = self.data['db-cache-conn%s-total-objects' % i]
            print "active%s.value %s" % (i, active)
            print "total%s.value %s" % (i, total)
            i += 1

    def config(self):
        self._prepare_fetch()
        print "graph_title Per connection caches (Zope %s/%s)" % (server_index, dbname)
        print "graph_vlabel Connections"
        print "graph_category Zope"
        print "graph_info Per connection caches of Zope %s, database %s" % (server_index, dbname)
        print "active0.label Connection 1: Active objects"
        print "active1.label Connection 2: Active objects"
        print "active2.label Connection 3: Active objects"
        print "active3.label Connection 4: Active objects"
        print "total0.label Connection 1: Total objects"
        print "total1.label Connection 2: Total objects"
        print "total2.label Connection 3: Total objects"
        print "total3.label Connection 4: Total objects"

graph = locals()[graph]()
getattr(graph, cmd)()
