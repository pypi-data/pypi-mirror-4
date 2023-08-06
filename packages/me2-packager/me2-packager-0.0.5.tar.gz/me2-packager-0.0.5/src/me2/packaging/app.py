#!/usr/bin/env python
'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import os
import sys
import logging

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import argparse

from me2.packaging.package import Packager, BundleSpecError

def main():
    #ToDO: Important: the constructor of Packager should not raise an error
    try:
        packager = Packager()
    except BundleSpecError, e:
        print >>sys.stderr, "[CRITICAL] Error evaluating spec file! Check syntax!"
        sys.exit(1)
    parser = argparse.ArgumentParser(prog = 'm2pack')
    parser.add_argument('--verbose', '-v', action = 'count', default = 1, help = "The verbosity level. More v's means more logging")
    subparsers = parser.add_subparsers(help = 'commands')

    parser_package = subparsers.add_parser('package', help = 'Package operations')
    parser_package.set_defaults(func = packager)
    packager.setup_parser(parser_package)

    opts = parser.parse_args()

    # Setup logging
    if opts.verbose > 4:
        log_level = 10
    else:
        log_level = 50 - opts.verbose * 10
    logging.basicConfig(format = '[ %(levelname)-8s %(filename)s:%(lineno)d (%(name)s) ] --> %(message)s',
                        datefmt = '%d/%b/%Y %H:%M:%S',
                        level = log_level)
    opts.func(opts)

if __name__ == "__main__":
    main()
