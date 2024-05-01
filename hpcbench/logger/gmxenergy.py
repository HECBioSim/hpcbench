#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 10:53:21 2024

@author: rob
"""

import json
import argparse
import hpcbench.deps.pyedr

parser = argparse.ArgumentParser("Dump gromacs edr/xdr to json.")
parser.add_argument("edr", type=str, help="edr input file")
parser.add_argument("json", type=str, help="json output file.")

if __name__ == "__main__":
    args = parser.parse_args()
    edr = hpcbench.deps.pyedr.edr_to_dict(args.edr)
    for key, value in edr.items():
        edr[key] = value.tolist()
    with open(args.json, "w") as outfile:
        json.dump(edr, outfile, indent=4)
