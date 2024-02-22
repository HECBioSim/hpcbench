#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recursively run a command on files matching a pattern. Useful for submitting
large amounts of jobs or running post-processing scripts on many files.
"""

from pathlib import Path
import argparse
import subprocess

parser = argparse.ArgumentParser(
    description="Recursively run a command on all files matching a pattern")
parser.add_argument("command", type=str, help="Command to run. Use ? for"
                    " the filemame.")
parser.add_argument("file", type=str, help="File to run the command on. Use "
                    "? as a wildcard.")
parser.add_argument("folder", type=str, help="Folder to operate on")
parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode ("
                    "don't print output)")
parser.add_argument("-n", "--noconfirmation", action="store_true", help="Don't"
                    " ask for confirmation before running commands. Use "
                    "with supreme confidence.")


def recrun(command, file, folder, noconfirm=False, quiet=False):
    paths = Path(folder).rglob(file.replace("?", "*"))
    commands = []
    locs = []
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
        if not quiet:
            print(result)
        results.append(result)
    return results


if __name__ == "__main__":
    args = parser.parse_args()
    recrun(args.command, args.file, args.folder, args.noconfirmation,
           args.quiet)
