#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPCbench bar chat plotter
"""
import matplotlib.pyplot as plt
import numpy as np
from hpcbench.plot.table import get_tabular
import argparse
from util import bodge_numeric

parser = argparse.ArgumentParser(
    description="Plot a bar chart")
parser.add_argument("-m", "--matching", type=str, action="append", default=[],
                    help="Conditions that a hpcbench output json file has to "
                    "match to be included. The format is: "
                    "--matching entry:nestedentry=condition. You can supply "
                    "multiple matching args, all of them have to be true.")
parser.add_argument("-x", "--xlabel", type=str,
                    help="Location(s) within the json file for the x labels, "
                    "e.g. \"meta:basis\". This should ideally be a string.")
parser.add_argument("-y", "--yvalue", type=str,
                    help="Location(s) within the json file for the y values, "
                    "e.g. \"gromacs:Totals:Wall Time (s)\".")
parser.add_argument("-l", "--legend", type=str,
                    help="Location within the json value for the legend. "
                    "Bars are grouped by their xlabel, so one bar with each"
                    "Legend will appear in each group.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to search for hpcbench output files.")
parser.add_argument("-o", "--output", type=str,
                    help="Output file.")


def plot_bars(tabular, outfile, xlabel, label_index=1, value_index=0):
    """
    Plot a grouped bar chart.

    Args:
        tabular: results from the output of the function
        hpcbench.plot.table.get_tabular. The output has to be formatted with
        two columns, one for the value and one for the key.
        outfile: a string, output file to write to.
        xlabel: label for the x axis, string
        label_index: the index of the column to find the label at in the
        tabular
        value_index: the index within the tabular of the column containing the
        values.

    Returns:
        nothing, but creates a file called outfile
    """
    
    # NOTE: this is a special tabular, column 1 is the value and column 2 is
    # the label name
    indices = np.arange(len(tabular.keys()))

    # set up dimensions
    colours = ['#377eb8', '#ff7f00', '#4daf4a', '#f781bf',
               '#a65628', '#984ea3', '#999999', '#e41a1c', '#dede00']
    colours_lookup = {}
    bars_lookup = {}
    groups_lookup = {}
    labels = []
    xs = []
    print()
    print(tabular)
    for key, value in tabular.items():
        labels.append(key.split(", ")[1])
        xs.append(key.split(", ")[0])
    bars_per_index = len(set(labels))

    fig, ax = plt.subplots()
    bar_width = 1/bars_per_index*0.8
    start_offset = ((float(bars_per_index/2.))*-1)+(bar_width*2)
    used_labels = []

    # set colours (for shared labels and such)
    for label in list(set(labels)):
        colours_lookup[label] = colours.pop(0)

    # set indexes for bars
    i = 0
    for label in list(set(labels)):
        bars_lookup[label] = i
        i += 1

    # set indexes for groups
    i = 1
    for group in xs:
        if group not in groups_lookup:
            groups_lookup[group] = i
        i += 1

    # create bars
    curr_group = 1
    for row, cols in tabular.items():
        label = row.split(", ")[1]
        x = row.split(", ")[0]
        curr_group = groups_lookup[x]
        curr_bar = bars_lookup[label]
        colour = colours_lookup[label]
        plot_label = label
        if label in used_labels:
            plot_label = "_nolegend_"
        ax.bar(curr_group+(bar_width*start_offset) + (bar_width*curr_bar),
               bodge_numeric(list(cols.values())[value_index]), bar_width*0.8, bottom=0, label=plot_label,
               capsize=5, color=colour)
        used_labels.append(label)

    # other stuff
    ax.set(xticks=np.arange(len(set(xs)))+1, xticklabels=groups_lookup.keys())
    ax.legend()
    ax.autoscale_view()
    # ax.set_ylim(bottom = bot, top=top)
    # https://matplotlib.org/stable/gallery/units/bar_unit_demo.html#sphx-glr-gallery-units-bar-unit-demo-py
    plt.xlabel(xlabel)
    plt.ylabel(list(list(tabular.values())[0].keys())[value_index])
    plt.tight_layout()
    plt.legend()
    plt.savefig(outfile)
    return


def main(x, y, label, filter_list, directory, outfile):
    tabular = get_tabular(filter_list, [y], [x, label], directory)
    plot_bars(tabular, outfile, x, label_index=1, value_index=0)


def test():
    x = "meta:basis"
    y = "Accounting:CPUTimeRAW"
    label = "meta:Machine"
    filter_list = ["meta:QM=Psi4"]
    directory = "/home/rob/benchout/archer/psi4"
    outfile = "test.pdf"
    tabular = get_tabular(filter_list, [y], [x, label], directory)
    plot_bars(tabular, outfile, x, label_index=1, value_index=0)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.xlabel, args.yvalue, args.legend, args.matching, args.directory,
         args.output)
