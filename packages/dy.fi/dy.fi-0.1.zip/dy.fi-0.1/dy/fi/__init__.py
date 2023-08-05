"""Dynamic IP address updating for dy.fi.

Usage: dyfi -u USERACCOUNT -p PASSWORD HOSTNAMES

Update dy.fi dynamic IP address with USERACCOUNT and PASSWORD and HOSTNAMES:

    -u
    For USERACCOUNT

    -p
    For PASSWORD

    You can provide multiple HOSTNAMES separated with a space.
"""

from datetime import datetime

import getopt
import logging
import os
import sys
import urllib2


stream_log = logging.StreamHandler()
logging.getLogger().addHandler(stream_log)


ip_path = '{}/ip.txt'.format('/'.join(__file__.split('/')[:-1]))


def last_updated():
    mtime = os.path.getmtime(ip_path)
    timestamp = datetime.fromtimestamp(mtime)
    print 'Last updated: {}'.format(timestamp)
    return timestamp


def usage(code, msg=''):
    print >> sys.stderr, __doc__ % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)


def update_ip():
    try:
        optlist, hostnames = getopt.getopt(sys.argv[1:], 'p:u:')
    except getopt.error, msg:
        usage(1, msg)

    ip = urllib2.urlopen('http://ipcheck.ieserver.net').read().strip()

    items = dict(optlist)
    try:
        useraccount = items['-u']
        password = items['-p']

        if (datetime.now() - last_updated()).days >= 6 or ip != open(ip_path).read().strip():

            for hostname in hostnames:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                URL = "https://www.dy.fi/nic/update?hostname={}".format(hostname)
                password_mgr.add_password(None, URL, useraccount, password)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                opener.open(URL)
                urllib2.install_opener(opener)
                request = urllib2.Request(URL)
                urllib2.urlopen(request)

            ip_text = open(ip_path, 'w')
            ip_text.write(ip)
            ip_text.close()

            mtime = os.path.getmtime(ip_path)
            timestamp = datetime.fromtimestamp(mtime)
            message = 'IP address successfully updated: {}'.format(timestamp)
            print message

        else:
            message = 'IP address was not updated since it was not necessary.'
            print message

    except KeyError:
        logging.warning('Missing -u: useraccount or -p: password.')
