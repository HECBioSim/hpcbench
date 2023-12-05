#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Write into a json file. Usually this is used to add meta info to an existing
json file.
"""

import argparse
import json

parser = argparse.ArgumentParser(
    description="Write info from a slurm script to a json file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-e", "--extra", action="append", type=str,
                    help="Add extra info to the output file. "
                    "Use the format --extra \"key:value\"")


if __name__ == "__main__":
    args = parser.parse_args()
    output = {}
    if len(args.extra) > 0:
        for arg in args.extra:
            argparsed = arg.split(":")
            output[argparsed[0]] = argparsed[1]
    with open(args.output, "w") as outfile:
        json.dump(output, outfile, indent=4)
