###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: minify.py 3640 2013-01-28 08:07:35Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import optparse
import os
import os.path
import sys
import traceback


def minifySource(source, lib):
    """Minify source file with given library"""
    if lib == 'jsmin':
        import jsmin
        return jsmin.jsmin(source)
    elif lib == 'lpjsmin':
        import lpjsmin.jsmin
        return lpjsmin.jsmin.jsmin(source)
    elif lib == 'slimit':
        import slimit.minifier
        return slimit.minifier.minify(source)
    elif lib == 'cssmin':
        import cssmin
        return cssmin.cssmin(source)
    else:
        raise Exception('minify library "%s" is unknown' % lib)


def minify(options):
    # minify each file in given order
    minified = []
    for libName, fName in options.sources:
        f = open(fName, 'r')
        source = f.read()
        f.close()
        if fName not in options.skip:
            # get an explicit defined lib or the default lib option
            lib = options.libs.get(fName, options.lib)
            minified.append((libName, minifySource(source, options.lib)))
        else:
            minified.append((libName, source))

    if os.path.exists(options.output):
        os.remove(options.output)
    out = open(options.output, 'wb')
    # add header if given and an additonal space
    first = True
    header = options.header.replace('$$', '$').strip()
    if header:
        out.write(header)
        first = False
    # bundle minified source
    for libName, source in minified:
        if not first:
            # an additional space
            out.write('\n')
        # and write library name as comment
        out.write('/* %s */' % libName)
        # write source
        if not source.startswith('\n'):
            out.write('\n')
        out.write(source)
        first = False
    out.close()
    print "Minified file generated at %s with %sKB" % (options.output,
        os.path.getsize(options.output)/1024)


def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser("%prog [options] output")
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    if not positional or len(positional) < 2:
        parser.error("No output defined")
    options.lib = positional[0]
    options.header = positional[1]
    options.output = positional[2]
    options.sources = positional[3]
    # setup libs as a dict for simpler access
    options.libs = {}
    for fName, lib in positional[4]:
        options.libs[fName] = lib
    options.skip = positional[5]
    return options


def main(args=None):
    options = get_options(args)
    try:
        minify(options)
    except Exception, e:
        libs = ['%s %s' % (lib, fName) for fName, lib in options.libs.items()]
        libs = '\n'.join(libs)
        sys.stderr.write("lib: %s\n" % options.lib)
        sys.stderr.write("header: %s\n" % options.header)
        sys.stderr.write("output: %s\n" % options.output)
        sys.stderr.write("sources: %s\n" % options.sources)
        sys.stderr.write("lib: %s\n" % options.lib)
        if libs:
            sys.stderr.write("libs: %s\n" % options.libs)
        sys.stderr.write("skip: %s\n" % options.skip)
        sys.stderr.write("args: %s\n" % sys.argv)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)