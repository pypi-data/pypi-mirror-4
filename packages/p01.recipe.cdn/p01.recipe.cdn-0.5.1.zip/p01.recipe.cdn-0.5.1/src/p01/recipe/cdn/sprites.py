###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: sprites.py 3640 2013-01-28 08:07:35Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import platform
import optparse
import os.path
import sys
import traceback
from ConfigParser import ConfigParser

import glue

TRUE_VALUES = ['1', 'true', 'ok', 'yes']
FALSE_VALUES = ['0', 'false', 'no']


def makeBool(value):
    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False
    else:
        # raise error if None, unkonw value or empty value is given
        raise ValueError("Must use a known bool string")


def get_options(args=None):
    if args is None:
        args = sys.argv

    parser = optparse.OptionParser(
        usage=("usage: %prog [options] source_dir [<output> | --css=<dir> --img=<dir>]"))
    parser.add_option("--project", action="store_true", dest="project",
            help="generate sprites for multiple folders")
    parser.add_option("-c", "--crop", dest="crop", action='store_true',
            help="crop images removing unnecessary transparent margins")
    parser.add_option("-l", "--less", dest="less", action='store_true',
            help="generate output stylesheets as .less instead of .css")
    parser.add_option("-u", "--url", dest="url",
            help="prepend this url to the sprites filename")
    parser.add_option("-q", "--quiet", dest="quiet", action='store_true',
            help="suppress all normal output")
    parser.add_option("-p", "--padding", dest="padding",
            help="force this padding in all images")
    parser.add_option("--ratios", dest="ratios",
            help="Create sprites based on these ratios")
    parser.add_option("--retina", dest="retina", action='store_true',
            help="Shortcut for --ratios=2,1")
    parser.add_option("-w", "--watch", dest="watch", default=False,
            action='store_true',
            help=("Watch the source folder for changes and rebuild "
                  "when new files appear, disappear or change."))
    parser.add_option("-v", "--version", action="store_true", dest="version",
            help="show program's version number and exit")

    group = optparse.OptionGroup(parser, "Output Options")
    group.add_option("--css", dest="css_dir", default='', metavar='DIR',
            help="output directory for css files")
    group.add_option("--img", dest="img_dir", default='', metavar='DIR',
            help="output directory for img files")
    group.add_option("--html", dest="html", action="store_true",
            help="generate test html file using the sprite image and CSS.")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Advanced Options")
    group.add_option("-a", "--algorithm", dest="algorithm", metavar='NAME',
            help=("allocation algorithm: square, vertical, horizontal "
                  "(default: square)"), )
    group.add_option("--ordering", dest="ordering", metavar='NAME',
            help=("ordering criteria: maxside, width, height or "
                  "area (default: maxside)"), )
    group.add_option("--margin", dest="margin", type=int,
            help="force this margin in all images")
    group.add_option("--namespace", dest="namespace",
            help="namespace for all css classes (default: sprite)")
    group.add_option("--png8", action="store_true", dest="png8",
            help="the output image format will be png8 instead of png32")
    group.add_option("--ignore-filename-paddings", action='store_true',
            dest="ignore_filename_paddings", help="ignore filename paddings")
    group.add_option("--debug", dest="debug", action='store_true',
            help="don't catch unexpected errors and let glue fail hardly")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Output CSS Template Options")
    group.add_option("--separator", dest="separator", metavar='SEPARATOR',
            help=("Customize the separator used to join CSS class "
                  "names. If you want to use camelCase use "
                  "'camelcase' as separator."))
    group.add_option("--global-template", dest="global_template",
            metavar='TEMPLATE',
            help=("Customize the global section of the output CSS."
                  "This section will be added only once for each "
                  "sprite."))
    group.add_option("--each-template", dest="each_template",
            metavar='TEMPLATE',
            help=("Customize each image output CSS."
                  "This section will be added once for each "
                  "image inside the sprite."))
    group.add_option("--ratio-template", dest="ratio_template",
            metavar='TEMPLATE',
            help=("Customize ratios CSS media queries template."
                  "This section will be added once for each "
                  "ratio different than 1."))
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Optipng Options",
                "You need to install optipng before using these options")
    group.add_option("--optipng", dest="optipng", action='store_true',
            help="postprocess images using optipng")
    group.add_option("--optipngpath", dest="optipngpath",
            help="path to optipng (default: optipng)", metavar='PATH')
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Browser Cache Invalidation Options")
    group.add_option("--cachebuster", dest="cachebuster", action='store_true',
            help=("use the sprite's sha1 first 6 characters as a "
                  "queryarg everytime that file is referred from the css"))
    group.add_option("--cachebuster-filename", dest="cachebuster_filename",
            action='store_true',
            help=("append the sprite's sha first 6 characters "
                  "to the otput filename"))
    parser.add_option_group(group)

    options, positional = parser.parse_args(args)
    if not positional:
        parser.error("No options defined")
    options.source = positional[0]
    options.css_dir = positional[1]
    options.img_dir = positional[2]
    url = positional[3]
    if url:
        options.url = url
    options.project = makeBool(positional[4])
    options.less = makeBool(positional[5])
    options.html = makeBool(positional[6])
    return options


def main(args=None):
    options = get_options(args)

    output = None
    source = options.source

    if not os.path.isdir(source):
        parser.error("Directory not found: '%s'" % source)

    if options.project:
        manager_cls = glue.ProjectSpriteManager
    else:
        manager_cls = glue.SimpleSpriteManager

    # Get configuration from file
    config = glue.get_file_config(options.source)

    # Convert options to dict
    options = options.__dict__

    config = glue.ConfigManager(config, priority=options,
        defaults=glue.DEFAULT_SETTINGS)
    manager = manager_cls(path=source, output=output, config=config)

    if config.optipng and not command_exists(config.optipngpath):
        parser.error("'optipng' seems to be unavailable. You need to "
                     "install it before using --optipng, or "
                     "provide a path using --optipngpath.")

    if manager.config.watch:
        glue.WatchManager(path=source, action=manager.process).run()
        sys.exit(0)

    try:
        manager.process()
    except glue.MultipleImagesWithSameNameError, e:
        sys.stderr.write("Error: Some images will have the same class name:\n")
        for image in e.args[0]:
            sys.stderr.write('\t %s => .%s\n' % (image.name, image.class_name))
        sys.exit(e.error_code)
    except glue.SourceImagesNotFoundError, e:
        sys.stderr.write("Error: No images found.\n")
        sys.exit(e.error_code)
    except glue.NoSpritesFoldersFoundError, e:
        sys.stderr.write("Error: No sprites folders found.\n")
        sys.exit(e.error_code)
    except glue.InvalidImageOrderingError, e:
        sys.stderr.write("Error: Invalid image ordering %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except glue.InvalidImageAlgorithmError, e:
        sys.stderr.write("Error: Invalid image algorithm %s.\n" % e.args[0])
        sys.exit(e.error_code)
    except glue.PILUnavailableError, e:
        sys.stderr.write(("Error: PIL %s decoder is unavailable"
                          "Please read the documentation and "
                          "install it before spriting this kind of "
                          "images.\n") % e.args[0])
        sys.exit(e.error_code)
    except Exception:
        sys.stderr.write("Glue version: %s\n" % glue.__version__)
        sys.stderr.write("PIL version: %s\n" % glue.PImage.VERSION)
        sys.stderr.write("Platform: %s\n" % platform.platform())
        sys.stderr.write("Config: %s\n" % config.sources)
        sys.stderr.write("Args: %s\n" % sys.argv)
        sys.stderr.write("\n")
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)
