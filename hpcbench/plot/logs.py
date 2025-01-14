#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot log files created with hpcbench.
"""

import argparse
import matplotlib.pyplot as plt
from hpcbench.plot.util import get_data
import hpcbench.plot.plot_style as style
import numpy as np

parser = argparse.ArgumentParser(
    description="Plot logs (e.g. temperature, power) hpcbench log files")
parser.add_argument("-m", "--matching", type=str, nargs="+",
                    help="Conditions that a hpcbench output json file has to "
                    "match to be included. The format is: "
                    "--matching entry:nestedentry=condition. You can supply "
                    "multiple matching args, all of them have to be true.")
parser.add_argument("-x", "--x", type=str,
                    help="Location(s) within the json file for the x values, "
                    "e.g. \"gromacs:Totals:Atoms\". A ? can also be used as a "
                    "wildcard.")
parser.add_argument("-y", "--y", type=str,
                    help="Location(s) within the json file for the y values, "
                    "e.g. \"gromacs:Totals:Wall Time (s)\". A ? can also be "
                    "used as a wildcard.")
parser.add_argument("-z", "--y2", type=str,
                    help="Location(s) within the json file for the y values "
                    "of the second axis (optional). e.g. gromacs:Totals:Wall"
                    " Time (s)\". A ? can also be used as a wildcard.")
parser.add_argument("-l", "--label", type=str,
                    help="Location(s) within the json file to use as a label,"
                    "e.g. \"meta:slurm:gres\". A ? can also be used as a "
                    "wildcard.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to search for hpcbench output files.")
parser.add_argument("-o", "--outfile", type=str, default=None,
                    help="Plot output filename")
parser.add_argument("-p", "--outside", action="store_true",
                    help="Show legend outside plot area")
parser.add_argument("-a", "--avgy", action="store_true",
                    help="Average y values")
parser.add_argument("-b", "--avgy2", action="store_true",
                    help="Average y2 values")
parser.add_argument("-t", "--time", action="store_true",
                    help="Simulation time on x axis")
parser.add_argument("--xaxislabel", type=str, help="x axis label")
parser.add_argument("--yaxislabel", type=str, help="y axis label")
parser.add_argument("--small", action="store_true", help="Small plot")

def rescale_time(x):
    """
    Given timestamps in unix time, rescale them so that they are seconds
    from 0.

    Args:
        x, a list of timestamps

    Returns:
        scaled, a list of timestamps (seconds from 0)
    """
    xtmin = min(x)
    scaled = []
    for item in x:
        scaled.append(item - xtmin)
    return scaled


def equalise_length(x1, x2):
    """
    For two lists, cut the longer one down to be the same length as the
    shorter one.

    Args:
        x1 and x2, lists

    Returns:
        x1 and x2, cut to be the same length

    """
    if len(x1 > x2):
        x1 = x1[:len(x2)]
    if len(x2 > x1):
        x2 = x2[:len(x1)]
    return x1, x2


def avg_dict(d):
    """
    For a dictionary containing several lists, return the average, key-wise.

    Args:
        d, a dictionary of lists

    Returns:
        a dictionary with one entry, 'avg', and the average values.

    """
    length = len(min(d.values(), key=len))
    data = []
    for value in d.values():
        data.append(value[:length])
    avg = [float(sum(col))/len(col) for col in zip(*data)]
    return {"avg": avg}


def plot(dicts, x, y, y2, label, outfile, x_time=True, legend_outside=False,
         avg_y=False, avg_y2=False, xtime=True, xaxislabel=None,
         yaxislabel=None, small=False):
    """
    Plot the contents of dicts, which is a dictionary, indexed by label,
    containing the contents of log files, with each log having an x, y and
    optionally a y2.

    Params:
        dicts: a dictioanry indexed by label containing log file outputs
        x: the location within the json files for the x values. Used to get
        the x axis label.
        y: the location within the json files for the y values.
        y2: the location within the json files for the y2 values.
        label: the location within the json files for the legend label.
        outfile: output plot filename.
        x_time: If is is True, the x-axis will be rescaled to start from 0
        seconds.
        legend_outside: if this is True, the legend will be placed outside the
        plot area.
        avg_y: if this is true, the y2 values will be averaged.
        avg_y2: if this is True, the y2 values will be averaged.

    Returns:
        None.
    """
    fig, ax = plt.subplots()
    if y2:
        ax2 = ax.twinx()
        y2label = y2.split(":")[-1]
    xlabel = x.split(":")[-1]
    ylabel = y.split(":")[-1]
    label = label.split(":")[-1]
    col = style.ColourGetter()
    try:
        for key, value in dicts.items():
            print(value.keys())
            times = []
            for keyn, valuen in value['x'][0].items():
                times.append(rescale_time(valuen))
            if avg_y:
                value['y'][0] = avg_dict(value['y'][0])
            for keyn, valuen in value['y'][0].items():
                label = str(key)+"("+keyn+")"
                ax.plot(times[0], valuen, label=label, color=col.get(label))
            if "y2" in value:
                if avg_y2:
                    value['y2'][0] = avg_dict(value['y2'][0])
                for keyn, valuen in value['y2'][0].items():
                    y2l = key+"("+keyn+")"
                    valuen, times[0] = equalise_length(valuen, times[0])
                    ax2.plot(times[0], valuen, label=y2l, linestyle='dashed')
    except AttributeError:
        for key, value in dicts.items():
            if xtime:
                #x = np.linspace(0, value['y2'][0], len(value['y'][0]))
                x = np.linspace(0, 1, len(value['y'][0])) # normalise length
                value['x'][0] = x
            plt.plot(value['x'][0], value['y'][0], label=key)
    if xaxislabel:
        ax.set_xlabel(xaxislabel)
    else:
        ax.set_xlabel(xlabel)
    if yaxislabel:
        ax.set_ylabel(yaxislabel)
    else:
        ax.set_ylabel(ylabel)
    if y2:
        ax2.set_ylabel(y2label)
    if legend_outside:
        ax.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", frameon=False)
    else:
        ax.legend()
    plt.tight_layout()
    if small:
        fig.set_size_inches([4.0, 3.0])
    plt.savefig(outfile, bbox_inches="tight", pad_inches=0)


def main(directory, matches, x, y, label, outfile, y2=None, outside=False,
         avg_y=False, avg_y2=False, xtime=False, xaxislabel=False,
         yaxislabel=False, small=False):
    """
    Extract logged values (e.g. temperature, gpu and cpu load) from hpcbench
    log files and plot the results.

    Params:
        directory: the directory to look for files in.
        matches: a list of strings, where each string is formatted as
        entry:nestedentry=condition. These correspond to values in a json file.
        Each entry has to be true for a json file to be selected.
        dicts: a dictioanry indexed by label containing log file outputs
        x: the location within the json value for the values on the x axis. Can
        include a wildcard (?). Normally this points toward a timestamp.
        y: the location within the json value for the values on the y axis. Can
        include a wildcard (?).
        y2: optional, the location within the json files for the y2 values. Can
        include a wildcard (?).
        label: the location within the json files for the legend label.
        outfile: output plot filename.
        plot area.
        outside: if this is True, the legend will be placed outside the
        plot area.
        avg_y: if this is true, the y2 values on the plot will be averaged.
        avg_y2: if this is True, the y2 values on the plot will be averaged.

    Returns:
        None.
    """
    if xtime:
        x = y
        y2 = "run:Totals:Simulation time (ns)"
    dicts = get_data(matches, x, y, label, directory, wildcard=True, y2=y2)
    if xtime:
        y2 = None
    if outfile:
        plot(dicts, x, y, y2, label, outfile, legend_outside=outside,
             avg_y=avg_y, avg_y2=avg_y2, xtime=True, xaxislabel=xaxislabel,
             yaxislabel=yaxislabel, small=small)
    return dicts


def test():
    """
    A test function that plots GPU utilisation for 1 GPU and a range of
    different numbers of atoms. Left here as an example.
    """
    directory = "/home/rob/Downloads/testdata2/test2"
    matches = ["meta:extra:Machine=JADE", "meta:slurm:gres=gpu:1"]
    x = "gpulog:?:timestamp"
    y = "gpulog:?:utilization.gpu [%]"
    # y2 = "cpulog:?"
    y2 = None
    label = "gromacs:Totals:Atoms"
    outfile = "test.pdf"
    dicts = get_data(matches, x, y, label, directory, wildcard=True, y2=y2)
    plot(dicts, x, y, y2, label, outfile)


def test2():
    """
    A test function that plots GPU utilisation for many GPUs (between 1 and 8).
    Left here as an example.
    """
    directory = "/home/rob/Downloads/testdata2/test2"
    matches = ["meta:extra:Machine=JADE", "gromacs:Totals:Atoms=2997924"]
    x = "gpulog:?:timestamp"
    y = "gpulog:?:utilization.gpu [%]"
    # y2 = "cpulog:?"
    y2 = None
    label = "meta:slurm:gres"
    outfile = "test.pdf"
    dicts = get_data(matches, x, y, label, directory, wildcard=True, y2=y2)
    plot(dicts, x, y, y2, label, outfile)


if __name__ == "__main__":
    args = parser.parse_args()
    dicts = main(args.directory, args.matching, args.x,
                 args.y, args.label, args.outfile, args.y2, args.outside,
                 args.avgy, args.avgy2, args.time, args.xaxislabel,
                 args.yaxislabel, args.small)
