#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions for hpcbench data loggers
"""

import signal
from shutil import which
import json


def find_in_line(line, word, offset):
    """
    Given a line of text, locate the word next to a keyword.

    Args:
        line: one line of text, a string.
        word: the keyword, a string
        offset: how many words over the target word is. An integer.
    Returns:
        the target word, a string,
    """
    line_fmt = ' '.join(line.split()).strip().split(" ")
    for c_word in range(len(line_fmt)):
        if line_fmt[c_word] == word:
            return line_fmt[c_word+offset]


def parse_nvidia_smi(smi, results):
    """
    Parse the output of nvidia-smi and reformat it into a dictionary.

    Args:
        smi: the string output by nvidia-smi in csv mode
        results: a dictionary with results from this function. If there is no
        dictionary yet, pass an empty dictionary.

    Returns:
        results: a dictionary containing the results, indexed by GPU number.
    """
    cols, values = smi.split("\n")[0].split(","), smi.split("\n")[1:]
    cols = list(map(str.strip, cols))
    id_col = cols.index("index")
    if results == {}:
        for value in values:
            value = list(map(str.strip, value.split(",")))
            results[value[id_col]] = {}
            for col in cols:
                results[value[id_col]][col] = []
    for row in values:
        row = list(map(str.strip, row.split(",")))
        for name, value in zip(cols, row):
            results[row[id_col]][name].append(value)
    return results


def parse_rocm_smi(smi, results):
    """
    Parse the output of rocm-smi and reformat it into a dictionary.

    Args:
        smi: the string output by rocm-smi in json mode
        results: a dictionary with results from this function. If there is no
        dictionary yet, pass an empty dictionary.

    Returns:
        results: a dictionary containing the results, indexed by GPU number.
    """
    parsed = json.loads(smi)
    if results == {}:
        for key, value in parsed.items():
            results[key.replace("card", "")] = {}
            for key2, value2 in value.items():
                results[key.replace("card", "")][key2] = []
    for key, value in parsed.items():
        for key2, value2 in value.items():
            results[key.replace("card", "")][key2].append(value2)
    return results


def cat(file):
    """
    Read a file and strip it. This is a utility function mostly used to grab
    text from /sys.

    Args:
        file: path to the file. (or 'file')

    Returns:
        A string containing the contents of the file.
    """
    return open(file, 'r').read().strip()


def exists(command):
    """
    Check if a command-line tool exists (or at least, is on the $PATH).

    Args:
        command: command to test, string.

    Return:
        True or False depending on if the command exists.
    """
    return which(command) is not None


class GracefulKiller:
    """
    Handle sigterm/sigint gracefully, still saving the contents of the file.
    """
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True
