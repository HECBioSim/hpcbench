#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPCbench bar chat plotter
"""
import matplotlib.pyplot as plt
import numpy as np
from hpcbench.plot.table import get_tabular
import hpcbench.plot.plot_style as style
import argparse
from util import bodge_numeric
from collections import OrderedDict

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
parser.add_argument("-a", "--annotation", type=str, action="append",
                    default=[], help="Add text to bars in the chart. Format is"
                    " group:label=annotation. Call multiple times for multiple"
                    " annotations.")
parser.add_argument("--xaxislabel", type=str, help="x axis label")
parser.add_argument("--yaxislabel", type=str, help="y axis label")
parser.add_argument("--yscalefactor", type=float, default=1,
                    help="y axis scale factor")
parser.add_argument("-s", "--sort", action="store_true",
                    help="Sort by x label")
parser.add_argument("-o", "--output", type=str,
                    help="Output file.")


def plot_bars(tabular, outfile, xlabel, label_index=1, value_index=0,
              annotate_bars=[], x_ax_label=None, y_ax_label=None, yscale=1.):
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
    # parse annotations (if they exist)
    annotate_dict = {}
    for item in annotate_bars:
        key = item.split("=")[0]
        value = item.split("=")[1]
        annotate_dict[key] = value
    
    # NOTE: this is a special tabular, column 1 is the value and column 2 is
    # the label name

    # set up dimensions
    col = style.ColourGetter()
    #colours = ['#377eb8', '#ff7f00', '#4daf4a', '#f781bf',
    #           '#a65628', '#984ea3', '#999999', '#e41a1c', '#dede00']
    #colours_lookup = {}
    bars_lookup = {}
    groups_lookup = {}
    labels = []
    xs = []
    for key, value in tabular.items():
        labels.append(key.split(", ")[1])
        xs.append(key.split(", ")[0])
    bars_per_index = len(set(labels))

    fig, ax = plt.subplots()
    bar_width = 1/bars_per_index*0.8
    start_offset = ((float(bars_per_index/2.))*-1)+(bar_width*2)
    used_labels = []

    # set colours (for shared labels and such)
    #for label in list(set(labels)):
    #    colours_lookup[label] = colours.pop(0)

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
        #colour = colours_lookup[label]
        plot_label = label
        if label in used_labels:
            plot_label = "_nolegend_"
        bar_height = bodge_numeric(list(cols.values())[value_index])*yscale
        bar_x = curr_group+(bar_width*start_offset) + (bar_width*curr_bar)
        if x+":"+label in annotate_dict.keys():
            annotation = annotate_dict[x+":"+label]
            ax.text(bar_x, bar_height + bar_height*0.1, annotation,
                    rotation=90, horizontalalignment="center")        
        ax.bar(bar_x, bar_height, bar_width*0.8, bottom=0, label=plot_label,
               capsize=5, color=col.get(label))
        used_labels.append(label)

    # other stuff
    ax.set(xticks=np.arange(len(set(xs)))+1, xticklabels=groups_lookup.keys())
    ax.legend()
    ax.autoscale_view()
    # https://matplotlib.org/stable/gallery/units/bar_unit_demo.html#sphx-glr-gallery-units-bar-unit-demo-py
    if x_ax_label:
        plt.xlabel(x_ax_label)
    else:
        plt.xlabel(xlabel)
    if y_ax_label:
        plt.ylabel(y_ax_label)
    else:
        plt.ylabel(list(list(tabular.values())[0].keys())[value_index])
    plt.tight_layout()
    plt.legend()
    plt.savefig(outfile, bbox_inches="tight", pad_inches=0)
    return


def sort_tabular(tabular, group_idx=1, sort_idx=0):
    """
    Sort AND group a tabular (created by get_tabular) by indexes of the
    contents of its rows.
    
    Args:
        tabular: the output of get_tabular
        group_idx: index of the element of the row group by
        sort_idx: index of the element to sort by
    Returns:
        sorted tabular
        
    Developer note: this is an evil hack to get certain figures in the paper to
    appear correctly and I would not recommend using it or re-using it if
    possible.
    """
    xs = []
    for key, value in tabular.items():
        xs.append(key.split(", ")[group_idx])
    xs = list(set(xs))
    sorted_by_xs = []
    for x in xs:
        curr_x = {}
        for key, value in tabular.items():
            if x in key:
                curr_x[key] = value
        sorted_by_xs.append(curr_x)
    for unsorted in range(len(sorted_by_xs)):
        sorted_by_xs[unsorted] = OrderedDict(
            sorted(sorted_by_xs[unsorted].items(),
                   key=lambda item: bodge_numeric(
                       item[0].split(", ")[sort_idx])))
    tabular_sorted = OrderedDict()
    for item in sorted_by_xs:
        for key, value in item.items():
            tabular_sorted[key] = value
    return tabular_sorted


def main(x, y, label, filter_list, directory, outfile, annotation, xal, yal,
         yscale=1., sort=False):
    tabular = get_tabular(filter_list, [y], [x, label], directory)
    if sort:
        tabular = sort_tabular(tabular)
    plot_bars(tabular, outfile, x, label_index=1, value_index=0,
              annotate_bars=annotation, x_ax_label=xal, y_ax_label=yal,
              yscale=yscale)


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
         args.output, args.annotation, args.xaxislabel, args.yaxislabel,
         args.yscalefactor, args.sort)
