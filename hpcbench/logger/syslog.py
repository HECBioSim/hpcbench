#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logs info from /sys/ to a file.
"""

import argparse
import asyncio
import json
from hpcbench.logger.util import GracefulKiller, cat

parser = argparse.ArgumentParser(
    description="Log info from a specified location in /sys/ to a json file.")
parser.add_argument("output", type=str, help="Output json file")
parser.add_argument("-i", "--interval", type=int, default=5,
                    help="How often to log. Defaults to 1.")
parser.add_argument("-s", "--sys", type=str, action="append",
                    help="""Log something from /sys. Of the format
                    '/path:label:factor' where path is the path of the thing to
                    log, label is the name of the thing, and factor is a
                    multiplication factor (e.g. for converting units).""")


async def log_sys(path, factor, killer, for_time=1e30, interval=5):
    """
    Log the contents of some file (normally from /sys/), at some interval.

    Args:
        path: path to the file. (or 'file')
        factor: value from the file is multiplied by this.
        for_time: return after x seconds.
        interval: take measurements every x seconds.

    Returns:
        A list of floats containing the value of the 'file' at the specified
        inverval.
    """
    elapsed_time = 0
    output = []
    while elapsed_time < for_time and not killer.kill_now:
        output.append(float(cat(path))*factor)
        await asyncio.sleep(interval)
        elapsed_time += interval
    if killer.kill_now:
        print("Killed logging of "+path+" early at "+str(elapsed_time)+"s")
    return output


async def make_logs(sys, interval, killer):
    """
    Log the contents of multiple files simultaneously.

    Args:
        sys: the CLI argument 'sys', formatted as 'path:name:factor'
        interval; interval (in seconds) with which to take measurements, int

    Returns:
        A dictionary of lists containing values for the length of the run at
        the specified interval.
    """
    logs = {}
    for log in args.sys:
        path, label, factor = log.split(":")
        logs[label] = asyncio.create_task(
            log_sys(path, float(factor), killer, interval=interval))
    for label, log in logs.items():
        await log
        logs[label] = log.result()
    return logs

if __name__ == "__main__":
    args = parser.parse_args()
    killer = GracefulKiller()
    logs = asyncio.run(make_logs(args.sys, args.interval, killer))
    with open(args.output, "w") as outfile:
        json.dump(logs, outfile, indent=4)
