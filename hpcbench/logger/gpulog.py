#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logs GPU info (e.g. temperature, load) to a file.
"""

import argparse
import json
import subprocess
import time
from hpcbench.logger.util import GracefulKiller, exists, parse_smi
import sys

SMI_COLS = "timestamp,pstate,clocks_throttle_reasons.hw_slowdown," \
    "temperature.gpu,fan.speed,utilization.gpu,utilization.memory," \
    "memory.free,memory.used,power.draw,index,clocks.sm,clocks.mem," \
    "clocks.gr"
SMI_COMMAND = "nvidia-smi --query-gpu="+SMI_COLS+" --format=csv"

parser = argparse.ArgumentParser("Log the output of nvidia-smi to a json file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-i", "--interval", type=int, default=5,
                    help="How often to log. Defaults to 1.")
parser.add_argument("-c", "--cols", type=str, default=SMI_COLS,
                    help="Which columns from nvidia-smi to run.")


def log_smi(killer, for_time, smi_command=SMI_COMMAND, interval=5, write=None):
    """
    Log the output from nvidia-smi.

    Args:
        killer: instance of the GracefulKiller object which handles SIGINT
        for_time: return after x seconds.
        smi_command: the nvidia-smi command to use in its entirity
        interval: take measurements every x seconds.
        write: string, name of file to write

    Returns:
        a dictionary with the name and value of each column
    """
    elapsed_time = 0
    output = {}
    while elapsed_time < for_time and not killer.kill_now:
        p = subprocess.run(SMI_COMMAND.split(
            " "), capture_output=True, text=True).stdout.strip()
        output = parse_smi(p, output)
        time.sleep(interval)
        elapsed_time += interval
        with open(args.output, "w") as outfile:
            json.dump(output, outfile, indent=4)
    if killer.kill_now:
        print("Killed logging of nvidia-smi early at "+str(elapsed_time)+"s")


if __name__ == "__main__":
    args = parser.parse_args()
    if not exists("nvidia-smi"):
        print("nvidia-smi not detected, exiting...")
        sys.exit(1)
    killer = GracefulKiller()
    logs = log_smi(killer, 1e30, interval=args.interval, write=args.output)
    with open(args.output, "w") as outfile:
        json.dump(logs, outfile, indent=4)
