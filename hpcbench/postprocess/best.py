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
                    help="Variables to consider as influencing the value of "
                    "best. For example, set these to the number of atoms to "
                    "find the best ns/day for each number of atoms. Use the "
                    "obj1:obj1 etc syntax.")
parser.add_argument("-t", "--mark", type=str,
                    help="Location in each hpcbench output file to mark. Using"
                    "the syntax obj1:obj2:etc. Sets the value to True.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to look in.")


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
    # table is formatted as follows: values, best, path to json file
    paths = get_paths(directory)
    dicts = {}
    for path in paths:
        match = does_match(path, matches)
        # print("Matches "+str(path)+" = "+str(type(match)))
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
            if float(best_value) > dict_table[name][-2]:
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


# mark: meta:Best ns/day threads
# set mark to true for everything in the table
def update_best(table, mark):
    for entry in table[1:]:
        with open(entry[-1], "r") as file:
            target = json.load(file)
        add_dict_element(target, mark, set_to="yes")
        with open(entry[-1], "w") as file:
            json.dump(target, file, indent=4)
    return


def main(best, variables, directory, mark, matches=None):
    table = get_best(best, variables, directory, matches=matches)
    if mark:
        update_best(table, mark)
    else:
        print(tabulate.tabulate(table,
                                tablefmt="simple_grid", headers="firstrow", ))


def test():
    best = "run:Totals:ns/day"
    variables = ["slurm:slurm:nodes", "run:Totals:Number of atoms",
                 "slurm:slurm:cpus-per-task"]
    directory = "/home/rob/benchout/archer2/"
    best = get_best(best, variables, directory)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.best, args.variables, args.directory, args.mark, args.match)
