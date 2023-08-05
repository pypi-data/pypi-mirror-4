#!/usr/bin/env python

import argparse
import logging
import sys

from globtailer import TailMostRecentlyModifiedFileMatchingGlobPatternGenerator


def console_script():
    parser = argparse.ArgumentParser(description='Tail logs matching a glob pattern.')
    parser.add_argument('glob_pattern', help='Glob pattern of files to tail.')
    parser.add_argument('--verbose', action='store_true', help='Be verbose.')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    for line in TailMostRecentlyModifiedFileMatchingGlobPatternGenerator(args.glob_pattern):
        sys.stdout.write(line)


if __name__ == '__main__':
    console_script()
