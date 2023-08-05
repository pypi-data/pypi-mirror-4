#!/usr/bin/python
# -*- coding: latin-1 -*-
# Copyright (c) 2008 Zope Foundation and Contributors
# See also LICENSE.txt
# $Id$
"""Munin client script for ZEO monitor servers.

Reads the ZEO server host and port from sys.env['MUNIN_ZEO_(HOST|PORT)_<index>']
where the index is the number appended to the script's name when called.

"""

import os.path
import telnetlib
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
	_, graph, server_index, storage = script_name.split('_')
except ValueError:
	#bbb default storage 1
	_, graph, server_index = script_name.split('_')
	storage = '1'

HOST = os.environ['MUNIN_ZEO_HOST_%s' % server_index]
PORT = os.environ['MUNIN_ZEO_PORT_%s' % server_index]


class GraphBase(object):

    def _prepare_fetch(self):
        tn = telnetlib.Telnet(HOST, PORT)
        result = tn.read_all()
        result = result.splitlines()
        self.data = {}

        # First line is a server signature
        line = result.pop(0)
        assert line.startswith('ZEO monitor server version 3.')
        # Second line is a date
        line = result.pop(0)
        # Third line is empty
        line = result.pop(0)
        assert line == ''
        # now different storage signatures follow
        # skip all of them until we reach the one we're interested in
        while result and line != 'Storage: %s' % storage:
        	line = result.pop(0)
       
      	if not result:
      		#the storage has not been found
      		return
      	
        for line in result:
            if line.startswith('Server started'):
                continue
            if line == '':
                continue
            if line.startswith('Storage:'):
            	#skip other storages
            	break
            key, value = line.split(':')
            self.data[key.lower()] = float(value)

    def fetch(self):
        self._prepare_fetch()
        self.do_fetch()


class SimpleGraph(GraphBase):

    title = ''
    name = ''
    key = ''

    def do_fetch(self):
        print "%s.value %s" % (self.name, self.data[self.key])

    def config(self):
        print "graph_title %s (Zope %s %s)" % (self.title, server_index, storage)
        print "graph_vlabel %s" % (self.name)
        print "graph_category Zope"
        print "graph_info %s of Zope %s " % (self.title, server_index)
        print "%s.label %s" % (self.name, self.name)


class SimpleMultiGraph(GraphBase):

    title = ''
    vlabel = ''
    keys = []
    names = []

    def do_fetch(self):
        for key, name in zip(self.keys, self.names):
            print "%s.value %s" % (name, self.data[key])

    def config(self):
        print "graph_title %s (Zope %s)" % (self.title, server_index)
        print "graph_vlabel %s" % (self.vlabel)
        print "graph_category Zope"
        print "graph_info %s of the Zope %s " % (self.title, server_index)
        for name in self.names:
            print "%s.label %s" % (name, name)



class clients(SimpleGraph):

    key = 'clients'
    name = 'clients'
    title = 'Connected clients'

class verifying(SimpleGraph):

    key = 'clients verifying'
    name = 'verifying'
    title = 'Clients verifying'

class loadstores(SimpleMultiGraph):

    title = 'Loads Stores'
    vlabel = 'num objects'
    keys = ['loads',
            'stores']
    names = ['object_loads',
             'object_stores']


graph = locals()[graph]()
getattr(graph, cmd)()
