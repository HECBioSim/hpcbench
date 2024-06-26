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
parser.add_argument("-a", "--accounting", type=str, default="accounting.json",
                    help="Path to accounting data from hpcbench sacct or "
                    "hpcbench syslog.")


def parse_omm_log(filename, standardise=True, accounting="accounting.json"):
    """
    Parse an OMM log. Because OMM logs are output by OMM python scripts, which
    are already formatted correctly (at least the ones output by hpcbench
    templates), this is mostly just a wrapper which optionally passes the
    script output through hpcbenchmark.logger.crosswalk.standardise_totals.

    Args:
        filaname: name of the OMM log file, a string.
        standardise: if True, crosswalk will be used to standardise results
        accounting: path to the accounting.json file from hpcbench sacct, a
        string.

    Returns:
        output hpcbench log file as a dict
    """
    with open(filename, "r") as file:
        data = json.load(file)
    output = {"Totals": data}
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"], accounting)
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_omm_log(args.log, args.keep, args.accounting)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
