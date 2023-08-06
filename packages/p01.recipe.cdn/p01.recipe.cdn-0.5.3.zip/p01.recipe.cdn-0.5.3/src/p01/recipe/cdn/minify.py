###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: minify.py 3664 2013-03-12 08:16:15Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import gzip
import optparse
import os
import os.path
import sys
import traceback
from cStringIO import StringIO


TRUE_VALUES = ['1', 'true', 'True', 'ok', 'yes', True]

def isTrue(value):
    return value in TRUE_VALUES


def minifySource(source, options):
    """Minify source file with given library"""
    lib = options.lib
    if lib == 'jsmin':
        import jsmin
        return jsmin.jsmin(source)
    elif lib == 'lpjsmin':
        import lpjsmin.jsmin
        return lpjsmin.jsmin.jsmin(source)
    elif lib == 'slimit':
        mangle = False
        mangle_toplevel = False
        if isTrue(options.slimit_mangle):
            mangle = True
        if isTrue(options.slimit_mangle_toplevel):
            mangle_toplevel = True
        import slimit.minifier
        return slimit.minifier.minify(source, mangle, mangle_toplevel)
    elif lib == 'cssmin':
        wrap = False
        if isTrue(options.cssmin_wrap):
            # wrap_css_lines
            wrap = True
        import cssmin
        return cssmin.cssmin(source, wrap)
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
            minified.append((libName, minifySource(source, options)))
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
    # calculate gzip size
    sio = StringIO()
    gzipFile = gzip.GzipFile(options.output, mode='wb', fileobj=sio)
    gzipFile.writelines(source)
    gzipFile.close()
    gzs = sio.getvalue()
    sio.close()
    gzip_size = len(gzs)
    print "Minified file generated at %s with %sKB" % (options.output,
        os.path.getsize(options.output)/1024)
    print "Serving this file with gzip compresion will have a size of %sKB" % (
        gzip_size/1024)


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
    # slimit options
    options.slimit_mangle = positional[6]
    options.slimit_mangle_toplevel = positional[7]
    # cssmin options
    options.cssmin_wrap = positional[8]
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
        # slimit options
        sys.stderr.write("slimit_mangle: %s\n" % options.slimit_mangle)
        sys.stderr.write("slimit_mangle_toplevel: %s\n" % options.slimit_mangle_toplevel)
        # cssmin options
        sys.stderr.write("cssmin_wrap: %s\n" % options.cssmin_wrap)
        # args
        sys.stderr.write("args: %s\n" % sys.argv)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)