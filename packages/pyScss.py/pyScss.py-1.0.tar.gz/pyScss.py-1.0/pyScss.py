#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
pyScss.py, a standalone program interface to pyScss

@author     Brandon Carl <brandon@brandoncarl.me>
@version    1.0
@see        https://github.com/bcarl/pyScss.py
@copyright  (c) 2013 Brandon Carl (bcarl)
@license    BSD License
            http://opensource.org/licenses/BSD-2-Clause

pyScss.py is a standalone program that provides an interface to pyScss[1] via
a "binary." The pyScss library must be installed separately.

[1]: https://github.com/Kronuz/pyScss

'''

import argparse
import sys

from scss import Scss

def main(infile, outfile):
    _scss = Scss()
    if infile == '-':
        css = _scss.compile(sys.stdin.read())
    else:
        with open(infile, 'r') as f:
            css = _scss.compile(f.read())

    if outfile == '-':
        print css
    else:
        with open(outfile, 'w') as f:
            f.write(css)

def parse_args():
    parser = argparse.ArgumentParser(description='Convert SCSS to CSS.')
    parser.add_argument('infile', default='-', nargs='?',
                        help='the input file. if omitted, defaults to stdin')
    parser.add_argument('outfile', default='-', nargs='?',
                        help='the output file. if omitted, defaults to stdout')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args.infile, args.outfile)
