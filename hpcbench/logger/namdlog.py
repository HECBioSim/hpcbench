#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse NAMD stdout output and convert it to a json file.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals
from hpcbenhc.logger.utils import find_in_line

parser = argparse.ArgumentParser(
    description="Get performance and system info from a NAMD log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to NAMD log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")
parser.add_argument("-a", "--accounting", type=str, default="accounting.json",
                    help="Path to accounting data from hpcbench sacct or "
                    "hpcbench syslog.")


def parse_namd_log(filename, standardise=True, accounting="accounting.json"):
    """
    Parse the contents of a log file generate by NAMD. Return the
    performance information as a dictionary.

    Params:
        filename - path to the log file, a string.
    Returns:
        the performance inforation, as a dictionary.
    """
    with open(filename, "r") as file:
        lines = file.readlines()
    for line in lines:
        if "WallClock:" in line:
            wallclock_time = find_in_line(line, "WallClock:", 1)
            cpu_time = find_in_line(line, "CPUTime:", 1)
        if "Finished startup" in line:
            startup_time = find_in_line(line, "at", 1)
        if "ATOMS" in line and len(line.split(" ")) == 3:
            atoms = find_in_line(line, "ATOMS", -1)
        if "Running for" in line:
            steps = find_in_line(line, "steps", -1)
        if "TIMESTEP" in line and "LDB" not in line:
            timestep = str(float(find_in_line(line, "TIMESTEP", 1))/1e6)
    simtime = str(float(timestep) * int(steps))
    walltime_nosetup = float(wallclock_time) - float(startup_time)
    nsperday = (float(simtime)/walltime_nosetup)*86400
    sperstep = walltime_nosetup/float(steps)
    stepspers = 1/sperstep
    output = {"Totals": {
        "ns/day": str(nsperday),
        "s/step": str(sperstep),
        "steps/s": str(stepspers),
        "CPU Time (s)": str(cpu_time),
        "Wall Clock Time including setup (s)": str(wallclock_time),
        "Wall Clock Time (s)": str(walltime_nosetup),
        "Setup time": startup_time,
        "Atoms": atoms,
        "Number of steps": steps,
        "Timestep (ns)": timestep,
        "Simulation time (ns)": simtime
        }}
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"], accounting)
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_namd_log(args.log, args.keep, args.accounting)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
