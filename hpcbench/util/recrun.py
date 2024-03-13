#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recursively run a command on files matching a pattern. Useful for submitting
large amounts of jobs or running post-processing scripts on many files.
"""

from pathlib import Path
import argparse
import subprocess
import time

parser = argparse.ArgumentParser(
    description="Recursively run a command on all files matching a pattern")
parser.add_argument("command", type=str, help="Command to run. Use ? for"
                    " the filemame.")
parser.add_argument("file", type=str, help="File to run the command on. Use "
                    "? as a wildcard.")
parser.add_argument("folder", type=str, help="Folder to operate on")
parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode ("
                    "don't print output)")
parser.add_argument("-r", "--retry", type=int, default=None, help="Retry "
                    " command if an error is returned (no of seconds to wait)")
parser.add_argument("-n", "--noconfirmation", action="store_true", help="Don't"
                    " ask for confirmation before running commands. Use "
                    "with supreme confidence.")


def recrun(command, file, folder, noconfirm=False, quiet=False, retry=None):
    """
    Recursively run a command on all files matching some pattern.

    Args:
        command: the command to run, with a ? in place of the filename
        file: the filename, can use ? as a wildcard
        folder: the folder to operature on
        noconfirm: if false, will ask for confirmation
        quiet: if false, will not print output
        retry: will retry the command if it returns an error. Useful for
        submitting slurm jobs. Specify number of seconds to wait.

    Returns:
        a list of CompletedProcess options from subprocess.run
    """
    paths = Path(folder).rglob(file.replace("?", "*"))
    commands = []
    locs = []
    command_new = []
    for arg in command.split(" "):
        if "?" in arg:
            command_new.append("?")
        else:
            command_new.append(arg)
    command = " ".join(command_new)
    for path in paths:
        commands.append(command.replace("?", path.name))
        locs.append(str(path.parent))
    if not noconfirm:
        print("Will run the following commands:")
        for com, loc in zip(commands, locs):
            print(com+" (in "+loc+")")
        result = input("Okay? y/N: ")
        if result.lower() != "y":
            return
    results = []
    for com, loc in zip(commands, locs):
        result = subprocess.run(com.split(" "), cwd=loc)
        if result.returncode > 0 and retry:
            while True:
                print("Command "+com+" failed ("+str(result.returncode)+")")
                time.sleep(retry)
                result = subprocess.run(com.split(" "), cwd=loc)
                if result.returncode == 0:
                    time.sleep(retry)
                    break
        if not quiet:
            print(result)
        results.append(result)
    return results


if __name__ == "__main__":
    args = parser.parse_args()
    recrun(args.command, args.file, args.folder, args.noconfirmation,
           args.quiet, args.retry)
