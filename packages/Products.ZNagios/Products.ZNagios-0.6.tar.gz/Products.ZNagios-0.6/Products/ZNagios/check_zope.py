#!/usr/bin/python
# Copyright (c) 2004-2006 Zope Foundation and Contributors
# See also LICENSE.txt
# $Id: check_zope.py 3913 2006-04-05 06:01:15Z ctheune $
#
# check_zope - A plugin for netsaint/nagios to check the status of a Zope server

import os
import sys
import string
import getopt
import urllib2, base64

version = '0.2'

nagiosStateOk = 0
nagiosStateWarning = 1
nagiosStateCritical = 2
nagiosStateUnknown = 3

verbosity = 0
hostName = ''
port = 0
criticalDatabase = 0
criticalReferences = 0
childPid = 0
timeout = 15
authentication = ''
ignoreErrors = 0

def printUsage():
    print 'Usage: check_zope -H <hostname> -p <port> -d <critical database ' \
          'size> -r <critical reference count>'
    print '                 [-a <username>:<password>] [-t <timeout>] [-v ' \
          '<verbosity level>]'

def printHelp():
    printUsage()
    print ''
    print 'Options:'
    print '-H, --hostname=HOST'
    print '   The hostname of the Zope server you want to check'
    print '-p, --port=PORT'
    print '   The port where the Zope server listens'
    print '-d, --database=SIZE'
    print '   Size of the root database to be considered critical'
    print '-r, --references=COUNT'
    print '   Count of references to be considered critical'
    print '-a, --authentication=NAME'
    print '   URL-suitable authentication token like user:password'
    print '-i, --ignore-errors'
    print '   Ignore errors that are in the error log'
    sys.exit(nagiosStateUnknown)

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'iVhH:p:d:r:a:v?',
            ['version', 'help', 'hostname=', 'port=', 'database=', 
            'references=', 'authentication=', 'ignore-errors'])
except getopt.GetoptError, errorStr:
    print errorStr
    printUsage()
    sys.exit(nagiosStateUnknown)

if len(args) != 0:
    printUsage()
    sys.exit(nagiosStateUnknown)

for opt, arg in optlist:
    if opt in ('-V', '--version'):
        print 'check_zope %s' % (version)
        sys.exit(nagiosStateUnknown)
    elif opt in ('-i', '--ignore-errors'):
        ignoreErrors = 1
    elif opt in ('-h', '--help'):
        printHelp()
        sys.exit(nagiosStateUnknown)
    elif opt in ('-H', '--hostname'):
        hostName = arg
    elif opt in ('-a', '--authentication'):
        authentication = arg
    elif opt in ('-p', '--port'):
        port = int(arg or port)
    elif opt in ('-d', '--database'):
        criticalDatabase = int(arg or criticalDatabase)
    elif opt in ('-r', '--references'):
        criticalReferences = int(arg or criticalReferences)
    elif opt in ('-v', '--verbose'):
        # Plugin guidelines require this, but we don't have anything extra to
        # report
        verbosity = int(arg or 0)
    elif opt == '-?':
        printUsage()
        sys.exit(nagiosStateUnknown)

if hostName == '':
    print 'No hostname specified.'
    printUsage()
    sys.exit(nagiosStateUnknown)

url = "http://%s@%s:%s/Control_Panel/nagios"

outputMsg = ''
exitCode = nagiosStateOk

try:
    if port == 80 or not port:
        url = 'http://%s/Control_Panel/nagios' % hostName
    else:
        url = 'http://%s:%s/Control_Panel/nagios' % (hostName, port)
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s' % (authentication))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    htmlFile = urllib2.urlopen(request)
    data = htmlFile.readlines()
except Exception, e:
    print e
    sys.exit(nagiosStateCritical)
    
result = {}
# Blindly convert this to our dict:
for x in data:
    x = x[:-1]
    split = x.split(": ")
    if len(split) == 2:
        key, value = split
        result[key] = value

# Check for database size
if criticalDatabase and not result.has_key('database'):
    print "Zope didn't report database status"
    sys.exit(nagiosStateUnknown)

try:
    database_size = int(result['database'])
except ValueError:
    print "Zope reported weird database status:", result['database']
    sys.exit(nagiosStateUnknown)

if criticalDatabase and database_size > criticalDatabase:
    print "Zope database is too large:", database_size
    sys.exit(nagiosStateCritical)

# Check reference count

if criticalReferences and not result.has_key('references'):
    print "Zope didn't report reference count"
    sys.exit(nagiosStateUnknown)
try:
    references = int(result['references'])
except ValueError:
    print "Zope reported weird reference count:", result['references']
    sys.exit(nagiosStateUnknown)

if criticalReferences and references > criticalReferences:
    print "Zope references are too high:", references
    sys.exit(nagiosStateCritical)

# Check errors
if not ignoreErrors:
    i = 0
    errors = []
    while result.has_key("error%i" % i):
        errors.append(result["error%i" % i])
        i += 1
    if errors:
        print "Error:", errors[0]
        sys.exit(nagiosStateCritical)

# Provide uptime
uptime = result.get('uptime', 'unknown')

print 'Up: %s Refcount: %s ZODB: %s Mb Errors: None' % (uptime, references, database_size/(1024*1024))

sys.exit(nagiosStateOk)
