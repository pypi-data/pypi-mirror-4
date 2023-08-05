##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Z3c development recipes

$Id:$
"""

import os
import os.path
import zc.buildout
import zc.recipe.egg


zcml_template = """<configure
    xmlns='http://namespaces.zope.org/zope'
    xmlns:meta="http://namespaces.zope.org/meta">
  %s
</configure>
"""


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


def getRealPath(ws, dPath):
    """Get real path supporting [pkg]/relative/path"""
    dPath = dPath.strip()
    if dPath.startswith('#') or dPath.startswith(';'):
        # skip comments
        return None
    if dPath.startswith('['):
        # get path for externals packages and eggs
        # [pkg.name] relative/path or
        # [pkg.name]/relative/path or 
        # [pkg.name]relative/path
        pkgName, relPath = dPath.split(']')
        # remove leading [ from package name
        pkgName = pkgName[1:]
        # strip empty spaces from relative path
        relPath = relPath.strip()
        # remove leading slash
        if relPath.startswith('/'):
            relPath = relPath[1:]

        # get egg base path
        eggPath = ws.by_key[pkgName].location
        dPath = os.path.join(eggPath, relPath)

    return os.path.abspath(dPath)


# cdn setup
class CDNRecipe:
    """Content delivery resource extractor recipe.
    
    This recipe installes scripts for extract resources from a project based
    on a ZCML configuration file which contains the cdn configuration or
    includes cdn configuration files. See the package p01.cdn for more
    information about cdn resources.
    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup zcml configuration file
        zcml = self.options.get('zcml', None)
        if zcml is None:
            raise zc.buildout.UserError('No zcml configuration defined.')
        zcml = zcml_template % zcml
        zcmlFilename = os.path.join(location, 'configure.zcml')
        file(zcmlFilename, 'w').write(zcml)
        # append file to dest which will remove it on update
        dest.append(zcmlFilename)

        layer = self.options.get('layer', None)
        registry = self.options.get('registry', None)
        if registry is None:
            # None could not get parsed by OptionParser
            registry = ''

        # get output path
        output = self.options.get('output', None)
        if output is not None:
            # get absolut output path
            output = os.path.abspath(output)
        else:
            # None could not get parsed by OptionParser
            output = ''

        # get (optional) FTP config
        server = self.options.get('server', None)
        username = self.options.get('username', None)
        password = self.options.get('password', None)

        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # uri option 1
        # allows to setup an uri and use them in ResourceManager during
        # extraction. This will override the P01_CDN_URI environment variable.
        # NOTE: it's up to you if you use this option. But if so, you need to
        # implement a custom ResourceManger which is able to use the
        # P01_CDN_URI environment variable.
        uri = self.options.get('uri')
        if uri is not None:
            initialization += env_template % ('P01_CDN_URI', uri)

        # uri(s) option 2
        # allows to setup additional uris. Useable if you setup more then one
        # ResourceManager. This will override the P01_CDN_URI_* environment
        # variable.
        # NOTE: it's up to you if you use this option. But if so, you need to
        # implement a custom ResourceManger which is able to use the different
        # P01_CDN_URI_* environment variable.
        urisStr = self.options.get('uris')
        if urisStr is not None:
            uriLines = urisStr.split('\n')
            for line in uriLines:
                name, uri = line.strip().split(' ')
                key = 'P01_CDN_URI_%s' % name
                initialization += env_template % (key, uri)

        # generate extract script and return locations
        arguments = ['extract', layer, zcmlFilename, output, registry]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%sextract' % self.name, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate uri listing script and return locations
        arguments = ['uris', layer, zcmlFilename, output, registry]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%suris' % self.name, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate source path listing script and return locations
        arguments = ['paths', layer, zcmlFilename, output, registry]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%spaths' % self.name, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # generate ouput path listing script and return locations
        arguments = ['output', layer, zcmlFilename, output, registry]
        dest.extend(zc.buildout.easy_install.scripts(
            [('%soutput' % self.name, 'p01.recipe.cdn.extract', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # currently we can't use the ftp server setup without an output.
        # TODO: implement explicit ftp server ``source`` argument where we can
        # find the extracted resources`. This is just an issue if you use
        # a custom ResourceManager and define a custom ResourceManager.output
        # concept
        if output is not None and server is not None:
            # generate deploy script and return locations
            # setup script arguments and generate extract script
            arguments = [output, server, username, password]
            dest.extend(zc.buildout.easy_install.scripts(
                [('%sdeploy' % self.name, 'p01.recipe.cdn.deploy', 'main')],
                ws, self.buildout['buildout']['executable'],
                self.buildout['buildout']['bin-directory'],
                extra_paths = extra_paths,
                arguments = arguments,
                initialization = initialization,
                ))

## XXX: should we offer additional ftp deploy accounts?
##
##ftp
##  An additional list of ftp servers used for deploy the cdn resources. Each
##  line must provide a scriptname, username, password and ftp server url with
##  the following notation.
##  
##  <name><username>:<password>@<ftp.domain.tld>
##  
##  The domain must get used without the ftp:// protocol and the name
##  get used as a postfix for the deploy script e.g. <partsname>deploy-<name>
#
#        ftp = []
#        append = ftp.append
#        ftpStr = self.options.get('ftp')
#        if ftpStr is not None:
#            ftpLines = ftp.split('\n')
#            for line in ftpLines:
#                parts = line.strip().split('@')
#                if len(parts) != 3:
#                    raise ValueError("Not valid ftp value, must be " \
#                        "<scriptname><username>:<password>@<ftp.domain.tld>")
#                    username, password = parts[1].split(':')
#                    append(parts[0],username, password, domain)
#
#        for name, username, password, domain in ftp:
#            # generate deploy script and return locations
#            # setup script arguments and generate extract script
#            arguments = [output, domain, username, password]
#            dest.extend(zc.buildout.easy_install.scripts(
#                [('%sdeploy-%s' % (self.name, name),
#                  'p01.recipe.cdn.deploy', 'main')],
#                ws, self.buildout['buildout']['executable'],
#                self.buildout['buildout']['bin-directory'],
#                extra_paths = extra_paths,
#                arguments = arguments,
#                initialization = initialization,
#                ))

        return dest

    update = install


# minify setup
def addMinifyLibrary(options, lib):
    """Inject the libary defined by it'sname"""
    # inject relevant minification library
    if lib == 'jsmin':
        options['eggs'] = options['eggs'] + '\n' + 'jsmin'
    elif lib == 'lpjsmin':
        options['eggs'] = options['eggs'] + '\n' + 'lpjsmin'
    elif lib == 'slimit':
        options['eggs'] = options['eggs'] + '\n' + 'slimit'
    elif lib == 'cssmin':
        options['eggs'] = options['eggs'] + '\n' + 'cssmin'
    else:
        raise zc.buildout.UserError('minify library "%s" is unknown' % lib)


class MinifyRecipe:
    """Minify recipe.
    
    This recipe installes scripts for minify resources.

    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'

        # get library name
        self.lib = self.options.get('lib', None)
        if self.lib is None:
            raise zc.buildout.UserError('No lib configuration defined.')

        # inject default minification library
        addMinifyLibrary(self.options, self.lib)

        self.libs = []
        lines = self.options.get('libs', '').splitlines()
        for item in lines:
            if ' ' in item.strip():
                # load explicit defined minify libraries
                fName, lib = item.split()
                addMinifyLibrary(self.options, lib)
                # add filename, libarary tuple as libs option
                self.libs.append((fName, lib))

        # setup egg
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup additional egg path and working set
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # get header
        header = self.options.get('header', '')

        # get output path
        output = self.options.get('output', None)
        if output is None:
            raise zc.buildout.UserError('No output configuration defined.')
        # get real absolut output path
        output = getRealPath(ws, output)

        # get source files
        fPaths = []
        files = self.options.get('files', None)
        if files is None:
            raise zc.buildout.UserError('No input configuration defined.')

        # find real path
        for fPath in files.splitlines():
            fPath = getRealPath(ws, fPath)
            if fPath is None:
                # skip comments
                continue

            fName = os.path.basename(fPath)
            fPath = os.path.abspath(fPath)
            # check the given paths
            if not os.path.exists(fPath):
                raise zc.buildout.UserError(
                    'Given file path "%s" does not exist.' % fPath)
            fPaths.append((fName, fPath))

        # get skip file names
        skip = self.options.get('skip', None)
        if skip is None:
            skip = []

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # generate minify script and return script location
        arguments = [self.lib, header, output, fPaths, self.libs, skip]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.cdn.minify', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        return dest

    update = install


# glue setup
class GlueRecipe:
    """CSS and sprite generation recipe based on glue python package

    See: http://pypi.python.org/pypi/glue

    """

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.cdn'

        # optional inject Pillow (PIL fork)
        # NOTE: non of the PIL libraries does work with buildout or easy_install
        # because of a bad top level path setup. Pillow is a PIL fork which
        # installs PIL. But since glue defines PIL as a dependency we will
        # provide a copy of glue.py and skip the PIL install_requires defined
        # in glue/setup.py
        pil = self.options.get('pil')
        if pil == 'pillow':
            # use Pillow
            self.options['eggs'] = self.options['eggs'] + '\n' + 'Pillow'
        elif pil not in ['skip', 'no', 'false', 'False', '0']:
            # skip PIL and Pillow at all, your eggs must define PIL or a PIL
            # replacement egg. We support the following imports
            self.options['eggs'] = self.options['eggs'] + '\n' + 'PIL'

        # setup egg
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']

        # setup parts dir
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup additional egg path and working set
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        wd = options.get('working-directory', options['location'])

        # base_url
        source = self.options.get('source', None)
        if source is None:
            raise zc.buildout.UserError('No source configuration defined.')
        source = getRealPath(ws, source)

        # css
        css = self.options.get('css', None)
        if css is None:
            raise zc.buildout.UserError('No css configuration defined.')
        css = getRealPath(ws, css)

        # img
        img = self.options.get('img', None)
        if img is None:
            raise zc.buildout.UserError('No img configuration defined.')
        img = getRealPath(ws, img)

        # url
        url = self.options.get('url', None)
        if url is None:
            url = ''

        # project
        project = self.options.get('project', None)
        if project is None:
            project = 'false'
        else:
            project = 'true'

        # less
        less = self.options.get('less', None)
        if less is None:
            less = 'false'
        else:
            less = 'true'

        # html
        html = self.options.get('html', None)
        if html is None:
            html = 'false'
        else:
            html = 'true'

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # generate minify script and return script location
        arguments = [source, css, img, url, project, less, html]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.cdn.sprites', 'main')],
            ws, self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        return dest

    update = install
