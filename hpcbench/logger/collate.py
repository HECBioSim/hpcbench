#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Combine together multiple json files.
"""

import json
import argparse
import os

parser = argparse.ArgumentParser(description="Combine json files.")
parser.add_argument('-l', '--list', nargs='+',
                    help='List of json files to collate', required=True)
parser.add_argument('-o', '--output', help='output json file', required=True)
parser.add_argument('-s', '--save', action="store_true",
                    help='Save original output files (normally deleted)')


__version__ = 0.1  # eventually this will be a module property

if __name__ == "__main__":
    args = parser.parse_args()
    output = {}
    for jsonfile in args.list:
        with open(jsonfile, "r") as file:
            output[jsonfile.replace(".json", "")] = json.load(file)
        if not args.save:
            os.remove(jsonfile)
        output['version'] = __version__
    with open(args.output, "w") as outfile:
        json.dump(output, outfile, indent=4)
