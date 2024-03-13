#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parses a GROMACS log file to extract performance and system info.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals

parser = argparse.ArgumentParser(
    description="Get performance and system info from a GROMACS system log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to GROMACS log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")
parser.add_argument("-a", "--accounting", type=str, default="accounting.json",
                    help="Path to accounting data from hpcbench sacct or "
                    "hpcbench syslog.")


def parse_gmx_log(log, standardise=True, accounting="accounting.json"):
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
                output["Totals"]["Timestep (ns)"] = str(float(''.join(
                    line.strip().split()).split("=")[1]) * 0.001)
            if "nsteps" in line:
                output["Totals"]["Number of steps"] = ''.join(
                    line.strip().split()).split("=")[1]
                if "Timestep (ns)" in output["Totals"]:
                    output["Totals"]
            if "Number of steps" in output["Totals"] and \
            "Timestep (ns)" in output["Totals"]:
                output["Totals"]["Simulation time (ns)"] = str(float(
                    output["Totals"]["Timestep (ns)"]) * \
                    int(output["Totals"]["Number of steps"]))
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
            if "Activity" in line and "Giga-Cycles" in line:
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
            if "Performance:" in line:
                perfline = line.strip().split()
                output["Totals"]["ns/day"] = perfline[1]
                output["Totals"]["hour/ns"] = perfline[2]
    output["Totals"]["step/s"] = int(output["Totals"]["Number of steps"]) / \
        float(output["Totals"]["Wall time (s)"])
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"], accounting)
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_gmx_log(args.log, args.keep, args.accounting)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
