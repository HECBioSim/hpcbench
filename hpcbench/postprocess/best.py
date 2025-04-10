#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mark hpcbench output files when they fulfil certain criteria.
"""

# get best
# vars: slurm:slurm:nodes, run:Totals:Number of atoms
# best: run:Totals:ns/day


from hpcbench.plot.util import get_paths, path_with_wildcard, does_match
from hpcbench.util.updatejson import get_dict_element
import json
import argparse
from hpcbench.deps import tabulate
import copy

parser = argparse.ArgumentParser("Find (and mark) results with the highest "
                                 "value of some json field.")
parser.add_argument("best", type=str, help="The value within the benchmark "
                    "output file to maxmimise, using the syntax obj1:obj2:etc")
parser.add_argument("-v", "--variables", type=str, action="append",
                    help="Variables to consider as influencing the value of "
                    "best. For example, set these to the number of atoms to "
                    "find the best ns/day for each number of atoms. Use the "
                    "obj1:obj1 etc syntax.")
parser.add_argument("-m", "--match", type=str, action="append",
                    help="Use only hpcbench output files matching this pattern"
                    ". For example, obj1:obj2=value.")
parser.add_argument("-t", "--mark", type=str,
                    help="Location in each hpcbench output file to mark. Using"
                    "the syntax obj1:obj2:etc. Sets the value to True.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to look in.")
parser.add_argument("-f", "--format", type=str, default="simple_grid",
                    help="Output table format")


def add_dict_element(d, element, set_to=None):
    """
    Add an element to a dictionary, based on a : delimited string.

    Params:
        d, the dictionary
        e, a :-delimited string of dictionary keys, e.g. key1:key2:key3

    Returns:
        the element
    """
    element = element.split(":")
    for e in element:
        try:
            d = d[e]
        except KeyError:
            d[e] = set_to
            if type(d[e]) is dict:
                d = d[e]
    return d


def get_best(best, variables, directory, path_func=path_with_wildcard,
             matches=None):
    """
    For a directory containing hpcbench log files, get the log file with the
    highest value of the variable 'best'. For the variables listed in
    'variables', the value of best will be provided for each combination of
    those variables. For example, you could find the best value of ns/day for
    each MD software on each machine.

    Args:
        best - the value to maximise. Corresponds to an item in a hpcbench
        json output file. A colon-separated string, e.g item1:item2:item3 etc,
        where the items are json keys (a string)
        variables - uses the same syntax as best, but provide a list of of
        the locations of values in the hpcbench output file (a list of strings)
        directory - the directory to check. All json files within this
        directory (recursively) will be parsed (a string)
        mark - the location within the json file to mark if the value of best
        is maximised. Set using the same syntax as best and variables (e.g.
        loc1:loc2:loc3). The value at this location is set to True (string)
        path_func - either path_in_dict or path_with_wildcard from plot.util
        matches: a whitelist of values and their locations in the hpcbench
        output file. e.g. ["loc1:loc2=value", "loc3:loc4=value"]. all of these
        conditions have to be met for the output file to be included in the
        comparison (a list of strings)

    Returns:
        table, a table of values stored as a list of lists, with the first list
        being the header, formatted like so: values, best, path to json file
        if 'mark' is some value then the json files will also be updated with
        mark=yes.
    """
    # values, best, path to json file
    paths = get_paths(directory)
    dicts = {}
    for path in paths:
        match = does_match(path, matches)
        if match:
            dicts[path] = match
    dict_table = {}
    header = []
    for var in variables:
        header.append(var.split(":")[-1])
    header.append(best.split(":")[-1])
    header.append("Path")
    for path, curr_dict in dicts.items():
        row = []
        best_value = path_func(curr_dict, best.split(":"))
        for var in variables:
            row.append(path_func(curr_dict, var.split(":")))
        name = "¬".join(list(map(str, row)))
        if name in dict_table:
            if float(best_value) > float(dict_table[name][-2]):
                row.append(best_value)
                row.append(path)
                dict_table[name] = row
        else:
            row.append(best_value)
            row.append(path)
            dict_table[name] = row
    table = []
    table.append(header)
    for key, value in dict_table.items():
        table.append(value)
    return table


def update_best(table, mark):
    """
    For a 'best' table (generated by get_best), mark the hpcbench output files
    with some value to indicate if they are best.

    Args:
        table - a 2d python list of tabulated values generated by get_best
        mark - the location in the json file to mark. A string, with json keys
        separated by colons, e.g loc1:loc2.

    Returns:
        nothing, but adds mark=yes to those files.
    """
    for entry in table[1:]:
        with open(entry[-1], "r") as file:
            target = json.load(file)
        add_dict_element(target, mark, set_to="yes")
        with open(entry[-1], "w") as file:
            json.dump(target, file, indent=4)
    return


def main(best, variables, directory, mark, matches=None):
    """
    Find (and potentially mark) the hpcbench log file with a certain value
    at its maximum. Optionally, provide a maximum value for every combination
    of another set of variables.

    Args:
        best - the value to maximise. Corresponds to an item in a hpcbench
        json output file. A colon-separated string, e.g item1:item2:item3 etc,
        where the items are json keys (a string)
        variables - uses the same syntax as best, but provide a list of of
        the locations of values in the hpcbench output file (a list of strings)
        directory - the directory to check. All json files within this
        directory (recursively) will be parsed (a string)
        mark - the location within the json file to mark if the value of best
        is maximised. Set using the same syntax as best and variables (e.g.
        loc1:loc2:loc3). The value at this location is set to True (string)
        matches: a whitelist of values and their locations in the hpcbench
        output file. e.g. ["loc1:loc2=value", "loc3:loc4=value"]. all of these
        conditions have to be met for the output file to be included in the
        comparison (a list of strings)

    Returns:
        best, a table of values stored as a list of lists, with the first list
        being the header, formatted like so: values, best, path to json file
        if 'mark' is some value then the json files will also be updated
        in accordance with the contents of 'mark'
    """
    best = get_best(best, variables, directory, matches=matches)
    if mark:
        update_best(best, mark)
    return best


def test():
    best = "run:Totals:ns/day"
    variables = ["slurm:slurm:nodes", "run:Totals:Number of atoms",
                 "slurm:slurm:cpus-per-task"]
    directory = "/home/rob/benchout/archer/namd"
    best = get_best(best, variables, directory)
    print(tabulate.tabulate(best,
                            tablefmt="simple_grid", headers="firstrow", ))


if __name__ == "__main__":
    args = parser.parse_args()
    best = main(
        args.best, args.variables, args.directory, args.mark, args.match)
    if not args.mark:
        print(tabulate.tabulate(best,
                                tablefmt=args.format, headers="firstrow", ))
