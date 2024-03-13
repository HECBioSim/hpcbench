#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse AMBER log files and convert them to json files.
"""

import argparse
import json
from hpcbench.logger.crosswalk import standardise_totals

parser = argparse.ArgumentParser(
    description="Get performance and system info from an AMBER log"
    " and write it to a json file")
parser.add_argument("log", type=str, help="Path to AMBER mdout log file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-k", "--keep", action='store_false',
                    help="Keep original totals formatting")
parser.add_argument("-a", "--accounting", type=str, default="accounting.json",
                    help="Path to accounting data from hpcbench sacct or "
                    "hpcbench syslog.")


def parse_amber_log(logfile, standardise=True, accounting="accounting.json"):
    """
    Parse the contents of an AMBER log file and extract the performance info.

    Args:
        logfile - path to the amber log file (normally mdout), a string
        standardise - whether to standardise the outputs using crosswalk
        accounting - if outputs are standardised, include slurm accounting or
        power consumption values from this file (normally the path to a json
        file created by hpcbench sacct) - a string

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
        if "NATOM" in line:
            output["Totals"]["Atoms"] = line.strip().split()[2]
        if 'nstlim' in output['Infile']:
            output['Totals']['Number of steps'] = output['Infile']['nstlim']
            output['Totals']['Simulation time (ns)'] = str(0.001 * int(
                output['Infile']['nstlim'])*float(output['Infile']['dt']))
            output['Totals']['Timestep (ns)'] = str(
                float(output['Infile']['dt']) / 1000)
    if standardise:
        output["Totals"] = standardise_totals(output["Totals"], accounting)
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    log = parse_amber_log(args.log, args.keep, args.accounting)
    with open(args.output, "w") as outfile:
        json.dump(log, outfile, indent=4)
