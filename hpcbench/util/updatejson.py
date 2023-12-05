#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge two json files together.
"""

import argparse
import json

parser = argparse.ArgumentParser("Merge two json files together.")
parser.add_argument("source", type=str, help="source json file")
parser.add_argument("target", type=str, help="json file to be written into")

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.source, "r") as infile:
        source = json.load(infile)
    with open(args.target, "r") as infile:
        target = json.load(infile)
    for key, value in source.items():
        target[key] = value
    with open(args.target, "w") as outfile:
        json.dump(target, outfile, indent=4)
