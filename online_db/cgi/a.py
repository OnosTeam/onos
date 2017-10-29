#!/usr/bin/env python
import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
print "Content-type: text/html\n"
 
#http://myonos.com/onos/cgi/a.py?a=2&c=5

print "Content-Type: text/html"
print ""

arguments = cgi.FieldStorage()
for i in arguments.keys():
 print arguments[i].value
