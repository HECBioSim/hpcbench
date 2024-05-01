#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get the energies from the log in an amber mdout file as a dictionary
"""

import json
import argparse

parser = argparse.ArgumentParser("Dump get energy info from AMBER log file.")
parser.add_argument("log", type=str, help="AMBER log file")
parser.add_argument("json", type=str, help="json output file.")


def parse_amber_energies_log(mdout):
    """
    Get the energies from the log in an amber mdout file as a dictionary.

    Args:
        mdout - path to amber mdout file
    Returns:
        results - a dictionary of results
    """
    with open(mdout, "r") as infile:
        for line in infile:
            if (line.count("=") == 3) or ("Density" in line and "=" in line):
                line = line.split()
                for i in range(len(line)):
                    if line[i] == "=":
                        key = line[i-1]
                        value = line[i+1]
                        try:
                            results[key].append(value)
                        except KeyError:
                            results[key] = [value]
    for key, value in results.items():
        if len(value) == 1:
            del results[key]
    return results


if __name__ == "__main__":
    args = parser.parse_args()
    results = parse_amber_energies_log(args.edr)
    with open(args.json, "w") as outfile:
        json.dump(results, outfile, indent=4)
