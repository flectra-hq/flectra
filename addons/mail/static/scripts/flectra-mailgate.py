#!/usr/bin/env python2
# Part of Flectra. See LICENSE file for full copyright and licensing details.
#
# flectra-mailgate
#
# This program will read an email from stdin and forward it to flectra. Configure
# a pipe alias in your mail server to use it, postfix uses a syntax that looks
# like:
#
# email@address: "|/home/flectra/src/flectra-mail.py"
#
# while exim uses a syntax that looks like:
#
# *: |/home/flectra/src/flectra-mail.py
#
# Note python2 was chosen on purpose for backward compatibility with old mail
# servers.
#
import optparse
import sys
import traceback
import xmlrpclib

def main():
    op = optparse.OptionParser(usage='usage: %prog [options]', version='%prog v1.2')
    op.add_option("-d", "--database", dest="database", help="Flectra database name (default: %default)", default='flectra')
    op.add_option("-u", "--userid", dest="userid", help="Flectra user id to connect with (default: %default)", default=1, type=int)
    op.add_option("-p", "--password", dest="password", help="Flectra user password (default: %default)", default='admin')
    op.add_option("--host", dest="host", help="Flectra host (default: %default)", default='localhost')
    op.add_option("--port", dest="port", help="Flectra port (default: %default)", default=7073, type=int)
    (o, args) = op.parse_args()

    try:
        msg = sys.stdin.read()
        models = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/2/object' % (o.host, o.port), allow_none=True)
        models.execute_kw(o.database, o.userid, o.password, 'mail.thread', 'message_process', [False, xmlrpclib.Binary(msg)], {})
    except xmlrpclib.Fault as e:
        # reformat xmlrpc faults to print a readable traceback
        err = "xmlrpclib.Fault: %s\n%s" % (e.faultCode, e.faultString)
        sys.exit(err)
    except Exception as e:
        traceback.print_exc(None, sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
