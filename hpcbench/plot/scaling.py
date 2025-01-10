#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot scaling
"""

import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from more_itertools import sort_together
from hpcbench.plot.util import get_data, path_with_wildcard
import numpy as np
from collections import OrderedDict

parser = argparse.ArgumentParser(
    description="Plot scaling (e.g. ns/hour, ns/watt) from hpcbench log files")
parser.add_argument("-m", "--matching", type=str, action="append",
                    help="Conditions that a hpcbench output json file has to "
                    "match to be included. The format is: "
                    "--matching entry:nestedentry=condition. You can supply "
                    "multiple matching args, all of them have to be true.")
parser.add_argument("-x", "--x", type=str,
                    help="Location(s) within the json file for the x values, "
                    "e.g. \"gromacs:Totals:Atoms\". A ? can also be used as a "
                    "wildcard.")
parser.add_argument("-y", "--y", type=str, action="append",
                    help="Location(s) within the json file for the y values, "
                    "e.g. \"gromacs:Totals:Wall Time (s)\". Call multiple "
                    "times to make a stack plot.")
parser.add_argument("-l", "--label", type=str,
                    help="Location(s) within the json file to use as a label,"
                    "e.g. \"meta:slurm:gres\". A ? can also be used as a "
                    "wildcard.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to search for hpcbench output files.")
parser.add_argument("-o", "--outfile", type=str, default=None,
                    help="Plot output filename")
parser.add_argument("-s", "--xscale", type=str, default="log",
                    help="Plot x scale. Can be linear, log, symlog or logit")
parser.add_argument("-c", "--yscale", type=str, default="log",
                    help="Plot y scale. Can be linear, log, symlog or logit")
parser.add_argument("-p", "--outside", action="store_true",
                    help="Show legend outside plot area")
parser.add_argument("-t", "--stack", action="store_true",
                    help="Make a stack plot")
parser.add_argument("-i", "--dash", type=str,
                    help="Labels matching this text will be dashed")
parser.add_argument("--xaxislabel", type=str, help="x axis label")
parser.add_argument("--yaxislabel", type=str, help="y axis label")
parser.add_argument("--noysci", action="store_true",
                    help="Disable scientific notation on the y axis")
parser.add_argument("--noxsci", action="store_true",
                    help="Disable scientific notation on the x axis")

def plot(data, xlabel, ylabel, outfile, xscale="linear", yscale="linear",
         legend_outside=False, sort=True, dash=None, x_axis_label=None,
         y_axis_label=None, noxsci=False, noysci=False):
    """
    Plot the results from get_data.

    Args:
        data: the dictionary produced by get_data, a dictionary indexed by
        the label, with each entry being a dictionary with x and y values
        xlabel: plot x-axis label, a string
        ylabel: plot y-axis label, a string
        outfile: name of output file, a string
        xscale: scale of the x-axis. can be 'linear', 'log', etc
        xscale: scale of the y-axis. can be 'linear', 'log', etc
        legend_outside: whether to put the legend outside the main plot
        area. A boolean.
        sort: whether to sort the data by the x values. A boolena.
    """
    fig, ax = plt.subplots()
    for key, value in data.items():
        x, y = value['x'], value['y']
        if sort:
            x, y = sort_together([x, y])
        linestyle = "-"
        if dash and (dash in key):
            linestyle = "dashed"
        ax.plot(x, y, label=key, linestyle=linestyle)
    if x_axis_label:
        ax.set_xlabel(x_axis_label)
    else:
        ax.set_xlabel(xlabel)
    if y_axis_label:
        ax.set_ylabel(y_axis_label)
    else:
        ax.set_ylabel(ylabel)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    if noysci:
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    if noxsci:
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    if legend_outside:
        ax.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", frameon=False)
    else:
        ax.legend()
    plt.tight_layout
    plt.savefig(outfile, bbox_inches="tight")


def transpose(d):
    """
    Tranpose the contents of a dictionary, where the elements of that
    dictionary are dictionaries with 'x' and 'y' elements, which are lists.

    Args
        d: input dictionary

    Returns:
        transposed dictionary

    """
    wildcard = OrderedDict()
    for key, value in d.items():
        for key1 in value['y'].keys():
            wildcard[key1] = []
    for key in wildcard:
        values = path_with_wildcard(d, ["?", "y", key])
        wildcard[key] = values.values()
    return wildcard


def sort_dictionary(d):
    """
    Sort a dictionary of lists by the average value of those lists.

    Args:
        d: the dictionary

    Returns
        an OrderedDict ordered by the average value of its elements.
    """
    ascending = OrderedDict()
    means = OrderedDict()
    for key, value in d.items():
        means[key] = np.mean(list(value))
    means = dict(sorted(means.items(), key=lambda item: item[1]))
    for key, value in means.items():
        ascending[key] = d[key]
    return ascending


def stackplot(data, xlabel, ylabel, outfile, xscale="linear", yscale="linear",
              legend_outside=False, sort=True):
    """
    Create a 'stackplot' which breaks down the scaling of the program by which
    functions/routines are being invoked.
    Args:
        data - output of hpcbench.plot.utilget_data, a dictionary.
        xlabel - x label for plot, a string
        ylabel - y label for plot, a string
        outfile - output filename, a string.
        xscale - scale to use for the x axis, a string. Passed to
        matplotlib ax.set_xscale. (Usually 'linear' or 'logarithmic')
        yscale - scale to use for the y axis, a string. Passed to
        matplotlib ax.set_yscale. (Usually 'linear' or 'logarithmic')
        legend_outside - whether to overlay the legend or put it outside the
        plot area. A boolean.
        sort - whether to sort the stack with the most expensive functions at
        the top, a boolean.
    """
    for key, value in data.items():
        for key1, value1 in value.items():
            if len(value1) == 1:
                data[key][key1] = value1[0]
    wildcard = transpose(data)
    to_delete = []
    for key, values in wildcard.items():
        if None in values:
            to_delete.append(key)
    for key in to_delete:
        del wildcard[key]
    wildcard = sort_dictionary(wildcard)
    # plot
    xs = list(map(float, data.keys()))
    fig, ax = plt.subplots()
    if sort:
        for key, value in wildcard.items():
            xs, wildcard[key] = sort_together([xs, value])
    ax.stackplot(list(xs), list(wildcard.values()),
                 labels=list(wildcard.keys()))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    if legend_outside:
        ax.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", frameon=False)
    else:
        ax.legend()
    plt.tight_layout
    plt.savefig(outfile, bbox_inches="tight")


def main(directory, matches, x, y, label, outfile, xscale, yscale,
         legend_outside=False, stack=False, dash=None, xaxlabel=None,
         yaxlabel=None, noxsci=False, noysci=False):
    """
    Look through all the hpcbench json files in a directory, check that they
    match the criterion specified, and extract the data that will be used,
    then plot the results.

    Args:
        directory: the directory to look for the hpcbench json files in.
        matches: a list of strings, each one specifying some criteria that the
        json file has to match eg. ['foo:bar:baz=quux']
        data: the dictionary produced by get_data, a dictionary indexed by
        the label, with each entry being a dictionary with x and y values
        x: a string of the same format specifying the location of the x values
        e.g. foo:bar:baz
        y: the same, for the y values
        outfile: name of output file, a string
        xscale: scale of the x-axis. can be 'linear', 'log', etc
        xscale: scale of the y-axis. can be 'linear', 'log', etc
        legend_outside: whether to put the legend outside the main plot
        area. A boolean.
        dash: lines with this string in the label will appear dashed,=
    Returns:
        A dictionary containing the results indexed by label, with each result
        having a set of x and y values.
    """
    dicts = get_data(matches, x, y, label, directory, wildcard=True)
    if outfile and type(y) is str:
        plot(dicts, x.split(":")[-1], y.split(":")[-1], outfile, xscale,
             yscale, legend_outside=legend_outside, dash=dash,
             x_axis_label=xaxlabel, y_axis_label=yaxlabel, noxsci=noxsci,
             noysci=noysci)
    if outfile and type(y) is list:
        stackplot(dicts, x.split(":")[-1], y.split(":")[-1], outfile, xscale,
                  yscale, legend_outside=legend_outside, stack=stack)
    return dicts


def test():
    """
    A test function showing example values of all the params.
    """
    directory = "/home/rob/Downloads/testdata2/test2"
    matches = ["meta:extra:Machine=JADE"]
    x = "meta:slurm:gres"
    y = "gromacs:Totals:Wall time (s)"
    label = "gromacs:Totals:Atoms"
    outfile = "test.pdf"
    xscale = "log"
    yscale = "log"
    dicts = get_data(matches, x, y, label, directory, wildcard=True)
    plot(dicts, x.split(":")[-1], y.split(":")[-1],
         outfile, xscale, yscale)


def test2():
    directory = "/home/rob/Downloads/testdata2/test2"
    matches = ["meta:extra:Machine=JADE", "meta:slurm:gres=gpu:1"]
    x = "gromacs:Totals:Atoms"
    y = "gromacs:Cycles:?:Wall time (s)"
    label = "gromacs:Totals:Atoms"
    outfile = "test.pdf"
    xscale = "log"
    yscale = "log"
    dicts = get_data(matches, x, y, label, directory, wildcard=True)
    stackplot(dicts, x.split(":")[-1], y.split(":")[-1],
              outfile, xscale, yscale, legend_outside=True)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.y and len(args.y) == 1:
        args.y = args.y[0]
    dicts = main(args.directory, args.matching, args.x, args.y,
                 args.label, args.outfile, args.xscale, args.yscale,
                 args.outside, dash=args.dash, xaxlabel=args.xaxislabel,
                 yaxlabel=args.yaxislabel, noxsci=args.noxsci,
                 noysci=args.noysci)
