#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parses a GROMACS log file to extract performance and system info.
"""

import argparse
import json

parser = argparse.ArgumentParser(
    description="Get performance and system info from a GROMACS system log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to GROMACS log file")
parser.add_argument("output", type=str, help="Output json file")


def parse_gmx_log(log):
    """Parse a gmx log file into a python dictionary.
    This function is a horrid mess, because gromacs log files are a horrid
    mess.

    Args:
        path: path to the log file. Normally called 'md.log'.

    Returns:
        The contents of the log file in dictionary format.
    """
    parse_gmx_info = False
    parse_megaflops = False
    parse_cycle_time = False
    parse_infile = False
    output = {"Gromacs info": {}, "Megaflops": {},
              "Cycles": {}, "Infile": {}, "Totals": {}}
    with open(log) as file:
        for line in file:
            line = line.replace("\n", "").strip()
            if "------" in line:
                continue
            if "There are:" in line:
                output["Totals"]["Atoms"] = line.strip().split(" ")[2]
            if "dt" in line and "=" in line:
                output["Totals"]["Timestep"] = ''.join(
                    line.strip().split()).split("=")[1]
            if "nsteps" in line:
                output["Totals"]["Steps"] = ''.join(
                    line.strip().split()).split("=")[1]
            # Parse GMX info
            if "GROMACS version:" in line and not parse_gmx_info:
                parse_gmx_info = True
            if parse_gmx_info:
                if line == "":
                    parse_gmx_info = False
                    continue
                linesplit = ''.join(line.strip().split()).split(":")
                output["Gromacs info"][linesplit[0]] = linesplit[1]
            # Parse gromacs input file
            if "Input Parameters" in line:
                parse_infile = True
                continue
            if parse_infile:
                if "=" in line:
                    parsed = ''.join(line.strip().split()).split("=")
                    output["Infile"][parsed[0]] = parsed[1]
                else:
                    parse_infile = False
            # Parse megaflops info
            if "Computing:" in line and "M-Number" in line:
                parse_megaflops = True
            if parse_megaflops:
                if "Rest" in line:
                    line = line.replace("Rest", "Rest 0 0 0")  # lame hack
                if line == "":
                    parse_megaflops = False
                    continue
                if "Computing:" in line:
                    cols = ' '.join(line.strip().split()).split(" ")
                    cols.remove("%")
                    cols.remove("Computing:")
                    cols[cols.index("Flops")] = "% Flops"
                    print("Mflop cols: "+str(cols))
                    continue
                if "Total" in line:
                    output["Totals"]["Mflops"] = ' '.join(
                        line.strip().split()).split(" ")[1]
                    continue
                rows = ' '.join(line.strip().split()).split(" ")
                if len(rows) > len(cols):
                    diff = len(rows) - len(cols)
                    rows[0:diff] = [' '.join(rows[0:diff])]
                label = rows.pop(0)
                output["Megaflops"][label] = {
                    cols[i]: rows[i] for i in range(len(rows))}
            # Parse time info
            if "Computing:" in line and "Giga-Cycles" in line:
                parse_cycle_time = True
                continue
            if parse_cycle_time:
                if "(s)" in line:
                    cols = ' '.join(line.strip().split()).split(" ")
                    cols.remove("sum")
                    cols[cols.index("Count")] = "Calls"
                    cols[cols.index("(s)")] = "Wall time (s)"
                    cols[cols.index("total")] = "Giga-cycles (total)"
                    cols[cols.index("%")] = "% Runtime"
                    print("Cycle cols: "+str(cols))
                    continue
                if "Total" in line:
                    totline = ' '.join(line.strip().split()).split(" ")
                    output["Totals"]["Wall time (s)"] = totline[1]
                    output["Totals"]["Giga-Cycles"] = totline[2]
                    parse_cycle_time = False
                    continue
                rows = ' '.join(line.strip().split()).split(" ")
                if len(rows) > len(cols):
                    diff = len(rows) - len(cols)
                    rows[0:diff] = [' '.join(rows[0:diff])]
                label = rows.pop(0)
                output["Cycles"][label] = {
                    cols[i]: rows[i] for i in range(len(rows))}
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_gmx_log(args.log)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
