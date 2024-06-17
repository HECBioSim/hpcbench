#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logs GPU info (e.g. temperature, load) to a file.
"""

import argparse
import json
import subprocess
import time
from hpcbench.logger.util import GracefulKiller, exists, parse_nvidia_smi, parse_rocm_smi
import sys
import os

SMI_COLS = "timestamp,pstate,clocks_throttle_reasons.hw_slowdown," \
    "temperature.gpu,fan.speed,utilization.gpu,utilization.memory," \
    "memory.free,memory.used,power.draw,index,clocks.sm,clocks.mem," \
    "clocks.gr"
SMI_COMMAND = "nvidia-smi --query-gpu="+SMI_COLS+" --format=csv"

ROCM_COMMAND = "rocm-smi -f -P -t -u --showmemuse -b -c -g -o  --json"

parser = argparse.ArgumentParser("Log the output of nvidia-smi to a json file")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-i", "--interval", type=int, default=5,
                    help="How often to log. Defaults to 1.")
parser.add_argument("-c", "--cols", type=str, default=SMI_COLS,
                    help="Which columns from nvidia-smi to run.")
parser.add_argument("-p", "--pid", type=str, help="Write PID to a file")
parser.add_argument("-g", "--gpu", type=str, help="Which gpu to use (can be "
                    " 'amd' or 'nvidia'.", default="nvidia")


def log_smi(killer, for_time, smi_command=SMI_COMMAND, interval=5, write=None,
            parser=parse_nvidia_smi):
    """
    Log the output from smi.

    Args:
        killer: instance of the GracefulKiller object which handles SIGINT
        for_time: return after x seconds.
        smi_command: the nvidia-smi or rocm-smi command to use in its entirity
        interval: take measurements every x seconds.
        write: string, name of file to write
        parser: the function with which to parse the output of the smi command,
        probably either parse_nvidia_smi or parse_rocm_smi

    Returns:
        a dictionary with the name and value of each column
    """
    elapsed_time = 0
    output = {}
    while elapsed_time < for_time and not killer.kill_now:
        p = subprocess.run(SMI_COMMAND.split(
            " "), capture_output=True, text=True).stdout.strip()
        output = parser(p, output)
        time.sleep(interval)
        elapsed_time += interval
        with open(args.output, "w") as outfile:
            json.dump(output, outfile, indent=4)
    if killer.kill_now:
        print("Killed logging of smi early at "+str(elapsed_time)+"s")


if __name__ == "__main__":
    args = parser.parse_args()
    if not exists("nvidia-smi") and not exists("rocm-smi"):
        print("nvidia-smi\rocm-smi not detected, exiting...")
        sys.exit(1)
    if args.pid:
        with open(args.pid, "w") as file:
            file.write(str(os.getpid()))
    killer = GracefulKiller()
    if args.gpu == "nvidia":
        logs = log_smi(killer, 1e30, interval=args.interval, write=args.output)
    elif args.gpu == "amd":
        logs = log_smi(killer, 1e30, interval=args.interval, write=args.output,
                       parser=parse_rocm_smi, smi_command=ROCM_COMMAND)
    else:
        print("Please specify either nvidia or amd")
        sys.exit(1)
    with open(args.output, "w") as outfile:
        json.dump(logs, outfile, indent=4)
