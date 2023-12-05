#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read info from ps for a given process to a json file.
"""

import argparse
import subprocess
import time
from hpcbench.logger.util import GracefulKiller
import json

parser = argparse.ArgumentParser(
    description="Log the CPU usage of a particular process to a json file.")
parser.add_argument("process", type=str,
                    help="Name of the process to check the CPU usage for.")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-i", "--interval", type=int, default=5,
                    help="How often to log. Defaults to 1.")


def log_cpu(progname, killer, output, for_time=1e30, interval=5):
    """
    Log the CPU usage of some process.

    Args:
        progname: name of the process executable, a string.
        killer: object, handler for sigterm etc.
        for_time: return after x seconds.
        interval: take measurements every x seconds.

    Returns:
        A dictionary containing lists of CPU usage for each core.
    """
    elapsed_time = 0
    cores = {}
    while elapsed_time < for_time and not killer.kill_now:
        cpu = subprocess.run(['ps', '-Leo', 'pid,ppid,tid,psr,%cpu,%mem,cmd'],
                             capture_output=True, text=True).stdout
        for line in cpu.split("\n"):
            if progname in line and "python" not in line:
                line = ' '.join(line.strip().split()).split(" ")
                try:
                    cores[line[3]].append(line[4])
                except KeyError:
                    cores[line[3]] = []
                    cores[line[3]].append(line[4])
        time.sleep(interval)
        elapsed_time += interval
        with open(output, "w") as outfile:
            json.dump(cores, outfile, indent=4)
    if killer.kill_now:
        print("Killed logging of CPU usage early at "+str(elapsed_time)+"s")
    return cores


if __name__ == "__main__":
    args = parser.parse_args()
    killer = GracefulKiller()
    with open(args.output, "w") as outfile:
        cpulog = log_cpu(args.process, killer, args.output,
                         interval=args.interval)
        json.dump(cpulog, outfile, indent=4)
