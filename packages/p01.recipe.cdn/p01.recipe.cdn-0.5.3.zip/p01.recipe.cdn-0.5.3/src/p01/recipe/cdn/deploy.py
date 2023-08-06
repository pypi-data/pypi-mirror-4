###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import optparse
import os
import sys
import ftplib

EXCLUDED_NAMES = ('.svn',)


def listCallback(names):
    def appendName(name):
        names.append(name)
    return appendName


def deployResources(host, dir, current='/', added=[], updated=[]):
    host.cwd(current)
    # list items
    names = []
    cb = listCallback(names)
    host.retrlines('LIST', cb)
    names = [line.rsplit(None, 1)[1] for line in names]
    for name in os.listdir(dir):
        host.cwd(current)
        exist = False
        if name in names:
            exist = True
        path = os.path.join(dir, name)
        if name.startswith('.'):
            # don't deploy privat files
            continue
        elif os.path.isfile(path):
            # remove if exist
            if exist:
                host.delete(name)
                updated.append(path)
            else:
                # append path
                added.append(path)
            # store file on FTP server
            f = open(path, 'rb')
            host.storbinary('STOR %s' % name, f)
            f.close()
        else:
            # add new directory on FTP server
            if not exist:
                host.mkd(name)
                added.append(path)
            else:
                updated.append(path)
            base = current
            if not base.endswith('/'):
                base += '/'
            p = base + name
            host.cwd(p)
            # collect sub items
            added, updated = deployResources(host, path, p, added, updated)
    return added, updated


def deploy(options):
    # check conditions
    if not os.path.exists(options.source):
        raise KeyError('Source path %s does not exist' % options.source)

    server = options.server
    username = options.username
    password = options.password
    host = ftplib.FTP(server, username, password)

    # collect resources including deploy them via FTP
    current = '/'
    added, updated = deployResources(host, options.source, current)

    host.quit()

    print 'Deploy to: "%s"' % server
    if added:
        print "Added:"
        print '\n'.join(added)
    else:
        print "Added: none"
        
    if updated:
        print "Updated:"
        print '\n'.join(updated)
    else:
        print "Updated: none"
    
    return


###############################################################################
# Command-line UI

def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser("%prog SOURCE SERVER USERNAME PASSWORD")
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    if not positional or len(positional) < 4:
        parser.error("No SOURCE, SERVER, USERNAME and/or PASSWORD defined.")
    options.source = positional[0]
    options.server = positional[1]
    options.username = positional[2]
    options.password = positional[3]

    return options

def main(args=None):
    options = get_options(args)
    try:
        deploy(options)
    except Exception, err:
        print err
        sys.exit(1)
    sys.exit(0)
