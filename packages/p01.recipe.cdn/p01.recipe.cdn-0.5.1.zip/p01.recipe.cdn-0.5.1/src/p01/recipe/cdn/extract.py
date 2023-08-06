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
import traceback
import zope.interface
import zope.component
import zope.component.interfaces
from zope.security.proxy import removeSecurityProxy
from zope.configuration import xmlconfig
from zope.publisher.interfaces.http import IResult
from zope.publisher.browser import TestRequest
from p01.cdn import interfaces
from p01.cdn.resource import I18nCDNResource
from p01.cdn.resource import ZRTCDNResource
from p01.cdn.resource import CDNResourceDirectory

EXCLUDED_NAMES = ('.svn',)

def removeExcludedNames(list):
    for name in EXCLUDED_NAMES:
        if name in list:
            list.remove(name)


def saveFile(path, output, name):
    if not os.path.exists(output):
        os.makedirs(output)
    target = os.path.join(output, name)
    if os.path.exists(target):
        os.remove(target)
    inFile = open(path, 'rb')
    outFile = open(target, 'wb')
    outFile.write(inFile.read())
    inFile.close()
    outFile.close()


def saveData(data, output, name):
    if not os.path.exists(output):
        os.makedirs(output)
    target = os.path.join(output, name)
    if os.path.exists(target):
        os.remove(target)
    # get body from DirectResult or keep data as data
    if IResult.providedBy(data):
        data = ''.join(data)
    outFile = open(target, 'wb')
    outFile.write(data)
    outFile.close()


def getResources(layerPaths, url='http://localhost/'):
    resources = ()
    for layerPath in layerPaths:
        # get the layer interface
        moduleName, layerName = layerPath.rsplit('.', 1)
        module = __import__(moduleName, {}, {}, ['None'])
        layer = getattr(module, layerName)
        # now we create a test request with that layer and our custom base URL.
        request = TestRequest(environ={'SERVER_URL': url})
        zope.interface.alsoProvides(request, layer)
        # next we look up all the resources
        resources += tuple(
            zope.component.getAdapters((request,), interfaces.ICDNResource))
    return resources


def storeResource(name, resource, output=None):
    if output is None:
        output = resource.manager.output
    if '%(version)s' in output:
        output = output % {'version': resource.manager.version}
    if not os.path.exists(output):
        os.makedirs(output)
    if isinstance(resource, I18nCDNResource):
        # we collect all files for each language
        for path in resource.getPaths():
            name = os.path.basename(path)
            saveFile(path, output, name)
    elif isinstance(resource, CDNResourceDirectory):
        # we create the directory and walk through the children.
        output = os.path.join(output, name)
        if not os.path.exists(output):
            os.makedirs(output)
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name) 
                storeResource(name, subResource, output)
    elif isinstance(resource, ZRTCDNResource):
        data = resource.GET()
        saveData(data, output, name)
    else:
        # simply store the file
        saveFile(resource.path, output, name)


def getResourceURIs(uris, resource):
    if isinstance(resource, I18nCDNResource):
        # we collect all uris for each language
        for uris in resource.getURIs():
            if uri not in uris:
                uris.append(uri)
    elif isinstance(resource, CDNResourceDirectory):
        # get recursive resources and call this method again
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name) 
                getResourceURIs(uris, subResource)
    else:
        # simply get the uri
        if resource.uri not in uris:
            uris.append(resource.uri)


def getSourcePaths(paths, resource):
    if isinstance(resource, I18nCDNResource):
        # we collect all path for each language
        for path in resource.getPaths():
            if path not in paths:
                paths.append(path)
    elif isinstance(resource, CDNResourceDirectory):
        # get recursive resources and call this method again
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name) 
                getSourcePaths(paths, subResource)
    else:
        # simply get the path
        if resource.path not in paths:
            paths.append(resource.path)


def getSourceOutputPaths(paths, name, resource, output=None):
    if output is None:
        output = resource.manager.output
    if '%(version)s' in output:
        output = output % {'version': resource.manager.version}
    if isinstance(resource, I18nCDNResource):
        # we collect all files for each language
        for path in resource.getPaths():
            name = os.path.basename(path)
            target = os.path.join(output, name)
            paths.append(target)
    elif isinstance(resource, CDNResourceDirectory):
        output = os.path.join(output, name)
        for name in resource.data.keys():
            if name not in resource.excludeNames and name not in EXCLUDED_NAMES:
                subResource = resource.get(name) 
                getSourceOutputPaths(paths, name, subResource, output)
    elif isinstance(resource, ZRTCDNResource):
        data = resource.GET()
        target = os.path.join(output, name)
        paths.append(target)
    else:
        target = os.path.join(output, name)
        paths.append(target)


def process(options):
    # run the configuration
    xmlconfig.file(options.zcml)
    if options.registry is not None:
        # apply base ``registry`` name if given
        sm = zope.component.getSiteManager()
        sm = removeSecurityProxy(sm)
        base = zope.component.queryUtility(
            zope.component.interfaces.IComponents, name=options.registry)
        bases = (removeSecurityProxy(base),)
        sm.__bases__ = bases + sm.__bases__

    # extract the resources
    resources = getResources(options.layers)
    # get resource list
    if options.command == 'extract':
        # now we can dump our resources to the ouput location given from the
        # recipe or if None, to the resource manager output location
        output = options.output
        for name, resource in resources:
            storeResource(name, resource, output)
    elif options.command == 'uris':
        # if we only want to list the paths
        uris = []
        for name, resource in resources:
            getResourceURIs(uris, resource)
        print '\n'.join(uris)
    elif options.command == 'paths':
        # if we only want to list the source paths
        paths = []
        for name, resource in resources:
            getSourcePaths(paths, resource)
        print '\n'.join(paths)
        return
    elif options.command == 'output':
        # if we only want to list the ouput paths
        paths = []
        output = options.output
        for name, resource in resources:
            getSourceOutputPaths(paths, name, resource, output)
        print '\n'.join(paths)
        return

###############################################################################
# Command-line UI

def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser("%prog [options] LAYER ROOT-ZCML-FILE")
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    if not positional or len(positional) < 2:
        parser.error("No COMMAND, LAYERS and/or ROOT_ZCML_FILE defined.")
    options.command = positional[0]
    options.layers = positional[1].split()
    options.zcml = positional[2]
    options.output = positional[3] or None
    options.registry = positional[4] or None

    return options

# Command-line UI
###############################################################################

def main(args=None):
    options = get_options(args)
    try:
        process(options)
    except Exception:
        sys.stderr.write("command: %s\n" % options.command)
        sys.stderr.write("layers: %s\n" % options.layers)
        sys.stderr.write("zcml: %s\n" % options.zcml)
        sys.stderr.write("output: %s\n" % options.output)
        sys.stderr.write("registry: %s\n" % options.registry)
        sys.stderr.write("args: %s\n" % sys.argv)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)
