#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get the status of hpcbench runs in a folder.
"""
from pathlib import Path
import json
import argparse

parser = argparse.ArgumentParser("Recursively check directories for benchmark"
                                 " output files.")
parser.add_argument("folder", type=str, help="Folder to check")
parser.add_argument("filename", type=str, help="Filename pattern. Use ? for a"
                    "wildcard.")


def check_status(folder, file):
    """
    Recursively check a directory to see if it contains valid benchmark
    files and print the results.

    Args:
        folder: folder to check, a string
        file: the filename to match. Can contain a wildcard (?), e.g. ?.json
    """
    folders = {}
    paths = list(Path(folder).rglob(file.replace("?", "*")))
    for path in paths:
        folders[str(path.parent)] = False
    for path in paths:
        with open(path, "r") as infile:
            try:
                contents = json.load(infile)
            except Exception:
                print(str(path)+" is unreadable")
                continue
        try:
            contents['version']
            folders[str(path.parent)] = True
        except KeyError:
            pass
    print("---")
    for key, value in folders.items():
        if not value:
            print(str(key)+" contains no valid benchmarks")


if __name__ == "__main__":
    args = parser.parse_args()
    check_status(args.folder, args.filename)
