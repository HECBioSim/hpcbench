#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 09:57:50 2024

@author: rob
"""

import argparse
from hpcbench.plot.util import get_paths, path_with_wildcard, does_match
from hpcbench.deps import tabulate

parser = argparse.ArgumentParser(
    description="Make a table from hpcbench log files")
parser.add_argument("-m", "--matching", type=str, action="append", default=[],
                    help="Conditions that a hpcbench output json file has to "
                    "match to be included. The format is: "
                    "--matching entry:nestedentry=condition. You can supply "
                    "multiple matching args, all of them have to be true.")
parser.add_argument("-r", "--rows", type=str, action='append',
                    help="Location(s) within the json file for the x values, "
                    "e.g. \"gromacs:Totals:Atoms\". A ? can also be used as a "
                    "wildcard.")
parser.add_argument("-c", "--cols", type=str, action="append",
                    help="Location(s) within the json file for the y values, "
                    "e.g. \"gromacs:Totals:Wall Time (s)\". Call multiple "
                    "times to make a stack plot.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to search for hpcbench output files.")
parser.add_argument("-f", "--format", type=str,
                    help="How to format the table. Can be any python tabulate"
                    " format string. Suggested: simple, simple_grid, html,"
                    " latex, csv,")
parser.add_argument("-o", "--output", type=str,
                    help="Output file, otherwise output is printed.")


def test():
    # matches = ["meta:Machine=Grace Hopper Testbed"]
    matches = []
    rows = ['run:Totals:Number of atoms', 'run:Totals']
    cols = ['slurm:program', 'meta:Machine']
    directory = "/home/rob/benchout"
    return get_tabular(matches, rows, cols, directory)


def get_tabular(matches, rows, cols, directory):
    """
    Look through all the hpcbench json files in a directory, check that they
    match the criterion specified, extract the data that will be used,
    and return a dictionary.

    Args:
        matches: a list of strings, each one specifying some criteria that the
        json file has to match eg. ['foo:bar:baz=quux']
        x: a list of strings of the same format specifying the location of the
        rows, e.g. ['foo:bar:baz']. If multiple values are provided then the
        row will be labelled with all of them.
        x: a list of strings of the same format specifying the location of the
        columns, e.g. ['foo:bar:baz']. There will be as many columns as there
        are entries in this list.
        directory: the directory to look for the hpcbench json files in.

    Returns:
        the tablular data, paradoxically in json format.
    """
    path_func = path_with_wildcard
    paths = get_paths(directory)
    dicts = []
    for path in paths:
        match = does_match(path, matches)
        if match:
            dicts.append(match)
    data = {}
    for curr_dict in dicts:
        dict_contents = {}
        for row in rows:
            name = row.split(":")[-1]
            contents = path_func(curr_dict, row.split(":"))
            if type(contents) is dict:
                for key, value in contents.items():
                    dict_contents[key] = value
            else:
                dict_contents[name] = contents
        name = ""
        for element in cols:
            try:
                name += path_func(curr_dict, element.split(":"))+", "
            except TypeError as e:
                print("element "+str(element)+" not in "+str(curr_dict))
        name = name[:-2]
        data[name] = dict_contents
    return data


def convert_to_table(tabular, table_format):
    """
    Convert the tabular data output by get_tabular into a text table.

    Args:
        tabular: tabular data output by get_tabular
        table_format: a valid format for the 'tabulate' package, e.g. simple,
        simple_grid, html, latex, csv
    Returns:
        the table, as a string.
    """
    table = [[]]
    for value in tabular.values():
        cols = value.keys()
    table[0] = [''] + list(cols)
    for key, value in tabular.items():
        table += [[key] + list(value.values())]
    table = [list(map(lambda x: x if x != False else '', i)) for i in table]
    if table_format == "csv":
        outstr = ""
        for row in table:
            outstr += ",".join(list(map(str, row)))
            outstr += "\n"
        return outstr
    return tabulate.tabulate(table, tablefmt=table_format, headers="firstrow")


def main(directory, matches, rows, cols, table_format, output=None):
    """
    Look through all the hpcbench json files in a directory, check that they
    match the criterion specified, extract the data that will be used,
    and return a table.

    Args:
        matches: a list of strings, each one specifying some criteria that the
        json file has to match eg. ['foo:bar:baz=quux']
        x: a list of strings of the same format specifying the location of the
        rows, e.g. ['foo:bar:baz']. If multiple values are provided then the
        row will be labelled with all of them.
        x: a list of strings of the same format specifying the location of the
        columns, e.g. ['foo:bar:baz']. There will be as many columns as there
        are entries in this list.
        directory: the directory to look for the hpcbench json files in.
    Returns:
        A dictionary containing the results indexed by label, with each result
        having a set of x and y values.
    """
    tabular = get_tabular(matches, rows, cols, directory)
    table = convert_to_table(tabular, table_format)
    if output:
        with open(output, "w") as file:
            file.write(table)
    return table


if __name__ == "__main__":
    args = parser.parse_args()
    table = main(args.directory, args.matching, args.rows, args.cols,
                 args.format, args.output)
    if not args.output:
        print(table)
