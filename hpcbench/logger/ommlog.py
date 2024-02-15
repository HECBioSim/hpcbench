#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse omm output and convert it to a json file.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals

parser = argparse.ArgumentParser(
    description="Get performance and system info from an OpenMM log"
    " and write it to a json file. Note: OMM doesn't have a standard log "
    "format, so this mostly just makes a few tweaks to the output from the "
    "exabiosim benchmark.py files.")
parser.add_argument("log", type=str, help="Path to OMM log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")


def parse_omm_log(filename, standardise=True):
    """
    """
    with open(filename, "r") as file:
        data = json.load(file)
    output = {"Totals": data}
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"])
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_omm_log(args.log, args.keep)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
