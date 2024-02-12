#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get output from sacct for a given job.
"""
import argparse
import json
import subprocess

default_format_string="ConsumedEnergyRaw,CPUTimeRAW,NodeList,ElapsedRaw"

parser = argparse.ArgumentParser(description="Get output from sacct for a"
                                 " given job and save it to a json file.")
parser.add_argument("jobid", type=str, help="id of the job")
parser.add_argument("-f", "--format", type=str, default=default_format_string,
                    help="sacct format string")
parser.add_argument("output", type=str, help="json file to be written into")


a="""ConsumedEnergyRaw|CPUTimeRAW|NodeList|ElapsedRaw|
|2004|dgk119|501|
102378|2004|dgk119|501|"""

def get_sacct(jobid, formatstring = default_format_string):
    pwrout = subprocess.run(
        ['sacct', '-j', str(jobid), '--format='+formatstring,"-P"],
        capture_output=True, text=True).stdout.strip()
    lines = pwrout.split("\n")
    header = lines.pop(0).split("|")
    output = {}
    for line in lines:
        line = line.split("|")
        for col in range(len(line)):
            if line[col] != "" and header[col] not in output:
                output[header[col]] = line[col]
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    output = get_sacct(args.jobid, args.format)
    with open(args.output, "w") as outfile:
        json.dump(output, outfile, indent=4)