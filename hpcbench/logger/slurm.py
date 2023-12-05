#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parses a slurm script to extract SLURM parameters.
"""

import argparse
import json
import time

parser = argparse.ArgumentParser(
    description="Write info from a slurm script to a json file")
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
            if line.startswith("gmx"):
                output["program"] = "GROMACS"
                output["arguments"] = line
    output["date"] = time.time()
    return output


if __name__ == "__main__":
    args = parser.parse_args()
    parsed = parse_submission_script(args.script)
    with open(args.output, "w") as outfile:
        json.dump(parsed, outfile, indent=4)
