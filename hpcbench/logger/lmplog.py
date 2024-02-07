#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parses a LAMMPS log file to extract performance and system info.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals

parser = argparse.ArgumentParser(
    description="Get performance and system info from a LAMMPS log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to LAMMPS log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")


def parse_lammps_log(log, standardise=True):
    """Parse a lammps log file into a python dictionary.

    Args:
        path: path to the log file. Normally called 'log.lammps'.

    Returns:
        The contents of the log file in dictionary format.
    """
    output = {}
    totals = []
    atoms = []
    stepss = []
    times = []
    breakdowns = []
    in_bd = False
    breakdowns = []
    in_bd = False
    with open(log, "r") as file:
        for line in file:
            line = " ".join(line.split())
            if "breakdown" in line and in_bd is False:
                in_bd = True
                curr_bd = []
                continue
            if in_bd and "|" in line:
                split = line.strip('\n').split("|")
                curr_bd.append(split)
            if in_bd and "|" not in line and "---" not in line:
                in_bd = False
                breakdowns.append(curr_bd)
            if "Performance:" in line:
                line = line.strip('\n').split(" ")
                perf = {}
                perf[line[2]] = float(line[1].replace(",",""))
                perf[line[4]] = float(line[3].replace(",",""))
                perf[line[6]] = float(line[5].replace(",",""))
                totals.append(perf)
            if "Loop time of" in line:
                line = line.strip('\n').split(" ")
                natoms = line[line.index("atoms")-1]
                atoms.append(natoms)
                steps = line[line.index("steps")-1]
                stepss.append(steps)
                time = line[line.index("of")+1]
                times.append(time)
            if "ERROR:" in line:
                raise IOError("Logfile contains error!")
        for total, natoms, nsteps, time in zip(totals, atoms, stepss, times):
            total["Atoms"] = natoms
            total["Wall Clock Time (s)"] = time
        breakdowns_list = []
        for breakdown in breakdowns:
            breakdown_dict = {}
            for line_no in range(len(breakdown)):
                line = breakdown[line_no]
                line = list(map(str.strip, line))
                if line_no == 0:
                    labels = line[1:]
                else:
                    name = line.pop(0)
                    breakdown_dict[name] = {
                        labels[i]: line[i] for i in range(len(labels))}
            breakdowns_list.append(breakdown_dict)
        output["Totals"] = totals
        output["Breakdowns"] = breakdowns_list
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"])
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_lammps_log(args.log, args.keep)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
