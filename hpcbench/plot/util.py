#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for hpcbench plotting tools.
"""

import json
from glob2 import glob
import re
from ast import literal_eval
import copy
import datetime


def bodge_timestamp(str_date):
    """
    Convert some string with a timestamp of format %Y/%m/%d %H:%M:%S.%f to unix
    time.
    Args:
        str_date: the string containing the time/date stamp
    Returns:
        that value as unix time.
    """
    d_date = datetime.datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S.%f')
    return d_date.astimezone().timestamp()


def bodge_numeric(s, try_datetime=True):
    """
    Convert some value encoded in a string into a numeric type. The string
    can contain other stuff, including units, commas, etc.

    Args:
        s: the string

    Returns:
        The value, as an int or a float.
    """
    if try_datetime:
        try:
            return bodge_timestamp(s)
        except ValueError:
            pass
        except TypeError:
            pass
    string = re.sub("[^-?\d\.]", "", s)
    val = literal_eval(string)
    is_int = isinstance(val, int) or (
        isinstance(val, float) and val.is_integer())
    if is_int:
        return int(val)
    else:
        return float(string)


def bodge_numeric_dict_wrapper(d):
    """
    Recursively apply bodge_numerioc to the contents of a dictionary.

    Args:
        d, a dictionary
    Returns:
        the same dictionary, but with all strings converted to floats/ints and
        timestamps converted to unix time.
    """
    if type(d) == list:
        rv = []
        for item in d:
            rv.append(bodge_numeric_dict_wrapper(item))
        return rv
    if type(d) == str:
        return bodge_numeric(d, True)
    if type(d) == dict:
        rv = {}
        for key, value in d.items():
            rv[key] = bodge_numeric_dict_wrapper(value)
        return rv


def get_paths(directory, ext="json"):
    """
    For a given directroy, return all files of a given type from that
    directory and all subdirectories.

    Args:
        directory, a file path, a string..

    Returns:
        A list containing the full paths to all the files.
    """
    return glob(directory+"/**/*."+ext)


def parse_path_arg(path_arg):
    """
    Parse the path argument that gives a location in a json file.
    Probably unnessecary.

    Args:
        path_arg: path arg. String formatted foo:bar:baz

    Returns:
        A list of locations, e.g [foo, bar, bas]
    """
    return path_arg.split(":")


def parse_match_arg(match_arg):
    """
    Parse the path argument that gives a location in a json file and an
    equality. Probably unnessecary.

    Args:
        match_arg: path arg. String formatted foo:bar:baz=quux

    Returns:
        A list of locations, e.g [foo, bar, baz], and the equality value.
    """
    pathstr, equal = match_arg.split("=")
    path = parse_path_arg(pathstr)
    return path, equal


def path_in_dict(d, path):
    """
    Check whether a given path (specified by a string) exists in a dictionary.

    Args:
        d: the dictionary.
        path: the path to check, a string, e.g.foo:bar:baz

    Returns:
        The thing in the dictionary at that location (if it exists), or False
        (if it doesn't)
    """
    try:
        element = path.pop(0)
        if len(path) == 0:
            return d[element]
        d[element]
        return path_in_dict(d[element], path)
    except KeyError:
        return False


def does_match(path, matches):
    """
    For a given json file (presumably representing a hpcbench benchmark), check
    if it matches with all the criteria supplied in matches (a list of
    locations within the json file formatted as foo:bar:baz=quux).

    Args:
        path: path to the json file
        matches: a list of strings

    Returns:
        The benchmark parsed as a dict, if it matches, None if it doesn't.
    """
    with open(path, "r") as file:
        bench = json.load(file)
    for match in matches:
        path, equal = parse_match_arg(match)
        destination = path_in_dict(bench, path)
        if destination != equal:
            return None
    return bench


def path_with_wildcard(d, path):
    """
    Check whether a given path (specified by a string) exists in a dictionary.
    This one supports wildcard, which are ? characters. Any wildcard will
    return a dictionary.

    Args:
        d: the dictionary.
        path: the path to check, a string, e.g.foo:bar:baz

    Returns:
        The thing in the dictionary at that location (if it exists), or False
        (if it doesn't)
    """
    try:
        element = path.pop(0)
        if len(path) == 0 and element != "?":
            return d[element]
        if len(path) == 0 and element == "?":
            return d
        if element != '?':
            d[element]
            return path_with_wildcard(d[element], path)
        else:
            retval = {}
            for key, value in d.items():
                # keep the path for the next iteration
                oldpath = copy.copy(path)
                retval[key] = path_with_wildcard(value, path)
                path = copy.copy(oldpath)
            return retval
    except KeyError:
        return False


def get_data(matches, x, y, label, directory, wildcard=False, y2=None):
    """
    Look through all the hpcbench json files in a directory, check that they
    match the criterion specified, and extract the data that will be used.

    Args:
        matches: a list of strings, each one specifying some criteria that the
        json file has to match eg. ['foo:bar:baz=quux']
        x: a string of the same format specifying the location of the x values
        e.g. foo:bar:baz
        y: the same, for the y values
        label: the same, for the plot label
        directory: the directory to look for the json files in.
    Returns:
        A dictionary containing the results indexed by label, with each result
        having a set of x and y values.
    """
    if wildcard:
        path_func = path_with_wildcard
        bodge_numeric_func = bodge_numeric_dict_wrapper
    else:
        path_func = path_in_dict
        bodge_numeric_func = bodge_numeric
    paths = get_paths(directory)
    dicts = []
    for path in paths:
        match = does_match(path, matches)
        if match:
            dicts.append(match)
    data = {}
    for hdict in dicts:
        xval = bodge_numeric_func(path_func(hdict, parse_path_arg(x)))
        if type(y) == list:
            yval = {}
            for element in y:
                yval[element] = bodge_numeric_func(
                    path_func(hdict, parse_path_arg(y)))
        else:
            yval = bodge_numeric_func(path_func(hdict, parse_path_arg(y)))
        labelval = path_func(hdict, parse_path_arg(label))
        if labelval not in data.keys():
            data[labelval] = {"x": [], "y": []}
        data[labelval]["x"].append(xval)
        data[labelval]["y"].append(yval)
        if y2:
            y2val = bodge_numeric_func(path_func(hdict, parse_path_arg(y2)))
            if 'y2' not in data[labelval].keys():
                data[labelval]["y2"] = []
            data[labelval]["y2"].append(y2val)
    return data
