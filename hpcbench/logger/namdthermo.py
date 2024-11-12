#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get thermo output from namd and output it as a json file
"""

import json
import argparse

parser = argparse.ArgumentParser("Get energy info from namd log file.")
parser.add_argument("log", type=str, help="namd log file")
parser.add_argument("json", type=str, help="json output file.")


def parse_namd_energies_log(mdout):
    """
    Get the energies from the log in namd stdout file as a dictionary.

    Args:
        mdout - path to namd stdout file
    Returns:
        results - a dictionary of results
    """
    results = {}
    header = []
    with open(mdout, "r") as infile:
        for line in infile:
            if "ETITLE" in line:
                for name in line.split():
                    if name not in results:
                        results[name] = []
                        header.append(name)
            if "ENERGY" in line:
                for item, name in zip(line.split(), header):
                    results[name].append(item)
    return results


if __name__ == "__main__":
    args = parser.parse_args()
    results = parse_namd_energies_log(args.log)
    with open(args.json, "w") as outfile:
        json.dump(results, outfile, indent=4)
