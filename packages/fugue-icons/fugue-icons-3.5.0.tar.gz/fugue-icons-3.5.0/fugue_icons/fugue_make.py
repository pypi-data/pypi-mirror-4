#!/usr/bin/env python
"""
Downloads the Fugue Icons and generates a cascading stylesheet and image with
the icons as CSS sprites. To use those sprites, link the generated CSS file to
your HTML, and then use ``class="fugue-icon fugue-name-of-theicon"`` on the
elements that are supposed to show the icon.
"""

import argparse
import logging
import os
import pygame
import StringIO
import urllib
import zipfile


REPO_URL = 'https://github.com/yusukekamiyamane/fugue-icons/zipball/master'
URL = 'http://p.yusukekamiyamane.com/icons/downloads/fugue-icons-%s.zip'
SIZE = 16
WIDTH = 64
OUT_NAME = 'fugue-icons'
COMMENT = """/*
    Fugue Icons
    http://p.yusukekamiyamane.com/
    (c) 2011 Yusuke Kamiyamane. All rights reserved.
    These icons are available under a Creative Commons Attribution 3.0 license.
*/"""
PREFIX='fugue'

def get_file(path_or_url):
    """Open the file or download it."""

    if path_or_url.startswith('http'):
        logging.info('Downloading from %s' % path_or_url)
        return StringIO.StringIO(urllib.urlopen(path_or_url).read())
    else:
        logging.info('Reading from %s' % path_or_url)
        return open(path_or_url, 'rb')

def main(url=None, version=None, width=WIDTH, size=SIZE, base_name=OUT_NAME,
         prefix=PREFIX, use_important=False):
    if use_important:
        logging.info('Using !important.')
        important = '!important'
    else:
        important = ''
    logging.info('Putting %d icons in a row.' % width)
    logging.info('Each icon is %d pixels.' % size)
    if url is None:
        if version:
            url = URL % version
        else:
            url = REPO_URL
    archive = zipfile.ZipFile(get_file(url))
    icons = [path for path in archive.namelist()
             if 'icons/' in path and path.endswith('.png')]
    merged = pygame.Surface((width * size, len(icons) / width * size),
                            pygame.SRCALPHA)
    css = [
        COMMENT,
        (".%s-icon{"
            "background-image:url('%s.png');text-indent:16px;"
            "overflow:hidden;height:16px;width:16px;display:inline-block;"
            "vertical-align:middle"
        "}") % (prefix, base_name)
    ]
    for i, path in enumerate(icons):
        name = os.path.basename(path).rsplit('.', 1)[0]
        icon = pygame.image.load(StringIO.StringIO(archive.open(path).read()))
        y, x = divmod(i, width)
        merged.blit(icon, (x * size, y * size))
        css.append('.%s-%s{background-position:-%dpx -%dpx%s}'
                   % (prefix, name, x * size, y * size, important))
    open('%s.css' % base_name, 'wb').write('\n'.join(css))
    logging.info('File %s.css written.' % base_name)
    pygame.image.save(merged, '%s.png' % base_name)
    logging.info('File %s.png written.' % base_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', nargs='?', default=None,
        help="Address or path of the icons archive.")
    parser.add_argument('--version', default=None,
        help="Version of archive to download.")
    parser.add_argument('--width', type=int, default=WIDTH,
        help="Put that many icons on a row.")
    parser.add_argument('--size', type=int, default=SIZE,
        help="The size of each icon.")
    parser.add_argument('--log', type=int, default=logging.INFO,
        help="Log level.")
    parser.add_argument('--out', default=OUT_NAME,
        help="Base name of output files.")
    parser.add_argument('--prefix', default=PREFIX,
        help="Prefix to use in CSS classes.")
    parser.add_argument('--important', default=False, action='store_true',
        help="Use !important in the generated CSS.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log)
    main(url=args.url, version=args.version, width=args.width, size=args.size,
         base_name=args.out, prefix=args.prefix, use_important=args.important)
