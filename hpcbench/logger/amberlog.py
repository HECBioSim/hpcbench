#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse AMBER log files and convert them to json files.
"""

import argparse
import json

parser = argparse.ArgumentParser(
    description="Get performance and system info from an AMBER log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to AMBER mdout log file")
parser.add_argument("output", type=str, help="Output json file")


def parse_amber_log(logfile):
    """
    Parse the contents of an AMBER log file and extract the performance info.

    Args:
        logfile - path to the amber log file (normally mdout), a string

    Returns:
        a dictionary containing the performance info..
    """
    output = {"AMBER info": {}, "Infile": {}, "Totals": {}}
    with open(logfile, "r") as file:
        loglines = file.readlines()
    reading_inparams = False
    reading_timings = False
    reading_totals = False
    for line in loglines:
        if "Here is the input file" in line:
            reading_inparams = True
        if reading_inparams:
            if "," in line:
                for statement in line.split(","):
                    statement = statement.strip()
                    if "=" in statement:
                        before, after = statement.split("=")
                        output["Infile"][before.strip()] = after.strip()
        if "INFORMATION" in line:
            reading_inparams = False
        if "TIMINGS" in line:
            reading_timings = True
            timing_shortname = "NONE"
        if reading_timings:
            if "NonSetup CPU Time in Major Routines" in line:
                timing_shortname = "Major Routines"
            elif "PME Nonbond Pairlist CPU Time" in line:
                timing_shortname = "PME Nonbond Pairlist"
            elif "PME Direct Force CPU Time" in line:
                timing_shortname = "PME Direct Force"
            elif "PME Reciprocal Force" in line:
                timing_shortname = "PME Reciprocal Force"
            elif "Final Performance" in line:
                reading_timings = False
            else:
                line_fmt = ' '.join(line.split()).strip().split(" ")
                if len(line_fmt) > 3:
                    line_fmt = line_fmt[1:]
                    merge_max = len(line_fmt) - 2
                    line_fmt[0:merge_max] = [' '.join(line_fmt[0:merge_max])]
                    linedict = {"Sec": line_fmt[1], "%": line_fmt[2]}
                    try:
                        output[timing_shortname][line_fmt[0]] = linedict
                    except KeyError:
                        output[timing_shortname] = {}
                        output[timing_shortname][line_fmt[0]] = linedict
        if "Average timings for all steps" in line:
            reading_totals = True
        if reading_totals:
            # why format it like this, what is wrong with you
            line_fmt = ' '.join(line.split()).strip().split(" ")[1:]
            prev = 0
            for i in range(len(line_fmt)):
                if line_fmt[i] == "=":
                    value = line_fmt[i+1]
                    label = " ".join(line_fmt[prev:i])
                    prev = i+2
                    output["Totals"][label] = value
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_amber_log(args.log)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)