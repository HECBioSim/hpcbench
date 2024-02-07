#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse NAMD stdout output and convert it to a json file.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals

parser = argparse.ArgumentParser(
    description="Get performance and system info from a NAMD log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to NAMD log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")


def find_in_line(line, word, offset):
    """
    Given a line of text, locate the word next to a keyword.

    Args:
        line: one line of text, a string.
        word: the keyword, a string
        offset: how many words over the target word is. An integer.
    Returns:
        the target word, a string,
    """
    line_fmt = ' '.join(line.split()).strip().split(" ")
    for c_word in range(len(line_fmt)):
        if line_fmt[c_word] == word:
            return line_fmt[c_word+offset]


def parse_namd_log(filename, standardise=True):
    """
    Parse the contents of a log file generate by NAMD. Return the
    performance information as a dictionary.

    Params:
        filename - path to the log file, a string.
    Returns:
        the performance inforation, as a dictionary.
    """
    nsperday = []
    sperstep = []
    with open(filename, "r") as file:
        lines = file.readlines()
    for line in lines:
        if "Benchmark time" in line:
            sperstep.append(find_in_line(line, "s/step", -1))
            nsperday.append(find_in_line(line, "ns/day", -1))
        if "WallClock:" in line:
            wallclock_time = find_in_line(line, "WallClock:", 1)
            cpu_time = find_in_line(line, "CPUTime:", 1)
        if "Finished startup" in line:
            startup_time = find_in_line(line, "at", 1)
        if "ATOMS" in line:
            atoms = find_in_line(line, "ATOMS", -1)
    nsperday = sum(map(float, nsperday))/len(nsperday)
    sperstep = sum(map(float, sperstep))/len(sperstep)
    stepspers = 1/sperstep
    walltime_nosetup = float(wallclock_time) - float(startup_time)
    output = {"Totals": {
        "ns/day": str(nsperday),
        "s/step": str(sperstep),
        "steps/s": str(stepspers),
        "CPU Time (s)": str(cpu_time),
        "Wall Clock Time including setup (s)": str(wallclock_time),
        "Wall Clock Time (s)": str(walltime_nosetup),
        "Setup time": startup_time,
        "Atoms": atoms
        }}
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"])
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_namd_log(args.log, args.keep)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
