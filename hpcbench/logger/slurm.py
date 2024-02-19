#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parses a slurm script to extract SLURM parameters.
"""

import argparse
import json
import time

parser = argparse.ArgumentParser(
    description="Submit a list of slurm scripts and report the results")
parser.add_argument("script", type=str, help="Path to submission script")
parser.add_argument("output", type=str, help="Output json file")


def parse_submission_script(script):
    output = {"slurm": {}, "modules": [],
              "program": "unknown", "arguments": "", "date": 0}
    with open(script) as file:
        for line in file:
            line = line.strip().replace("/n", "")
            if "#SBATCH" in line:
                param = line.split(" ")[1].replace("--", "").split("=")
                output["slurm"][param[0]] = param[1]
            if "module" in line:
                output["modules"].append(line.split(" ")[2])
            if "gmx" in line:
                output["program"] = "GROMACS"
                output["arguments"] = line
            if "benchmark.py" in line:
                output["program"] = "OpenMM"
                output["arguments"] = line
            if "namd3" in line:
                output["program"] = "namd3"
                output["arguments"] = line
            if "namd" in line:
                output["program"] = "namd2"
                output["arguments"] = line
            if "pmemd" in line:
                output["program"] = "AMBER"
                output["arguments"] = line
            if "lmp" in line:
                output["program"] = "LAMMPS"
                output["arguments"] = line
            # TODO here: make sure to get openmp parallelisation
            # it might be eaiser to read this from OMP_NUM_THREADS and always
            # use that instead of something like -ntomp
    output["date"] = time.time()
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    parsed = parse_submission_script(args.script)
    with open(args.output, "w") as outfile:
        json.dump(parsed, outfile, indent=4)
