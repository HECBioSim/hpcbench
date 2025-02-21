#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fit curves to results from hpcbench
"""

import argparse
from hpcbench.plot.util import get_data
import numpy as np
import copy
from scipy.optimize import curve_fit
from more_itertools import sort_together
import matplotlib.pyplot as plt
import os
import json

parser = argparse.ArgumentParser("Get parameters for curve fits from benchmark"
                                 " data and dump them to a file.")
parser.add_argument("-x", "--x", type=str,
                    help="x axis variable for the best fit graph, e.g "
                    "'run:Totals:Number of atoms'.")
parser.add_argument("-y", "--y", type=str, action="append",
                    help="y axis variable for the best fit graph, e.g. "
                    "'run:Totals:ns/day' Call multiple times for mutliple"
                    " fits")
parser.add_argument("-l", "--label", type=str,
                    help="Label results by this (location in a hpcbench input"
                    " file). E.g. slurm:program.")
parser.add_argument("-m", "--match", type=str, action="append",
                    help="Use only hpcbench output files matching this pattern"
                    ". For example, obj1:obj2=value.")
parser.add_argument("-d", "--directory", type=str,
                    help="Directory to look in. Should contain hpcbench "
                    "output files.")
parser.add_argument("-o", "--out", type=str,
                    help="Output file. If an existing file is supplied, the "
                    "results will be appended to that file.")


def fit_poly(x, a, b, c, d):
    """
    A third-degree polynomial of the form ax^3 + bx^2 + cx + d
    """
    return a*x**3 + b*x**2 + c*x + d


def fit_exp(x, a, b):
    """
    An exponential function of the form ae^(bx)
    """
    return a*np.exp(b*x)


def fit_pow(x, a, b):
    """
    An exponential function of the form ae^(1-log(bx))
    """
    return a*np.exp(1 - np.log(b*x))


# lookup tables - append if needed
fiteq = {"ns/day": fit_exp, "J/ns": fit_poly}
p0 = {"ns/day": [7e6,  1e-7], "J/ns": [0.00001, 0.001, 0.1, 1]}


def plot_fit(x, y, fiteq, title, fitparams, out):
    """
    Plot the outcome of a fit found in get_fit.
    Args:
        x, y: data to fit (1-d arrays\lists)
        fiteq: equation used to get the fit (a function)
        title: plot title (a string)
        fitparams: parameters for fiteq (a list of floats)
        out: filename for plot output (a string)
    """
    plt.figure()
    plt.title(title)
    plt.plot(x, y)
    xf = np.linspace(min(x), max(x))
    if len(fitparams) == 2:
        yf = fiteq(xf, fitparams[0], fitparams[1])
    if len(fitparams) == 3:
        yf = fiteq(xf, fitparams[0], fitparams[1], fitparams[2])
    if len(fitparams) == 4:
        yf = fiteq(xf, fitparams[0], fitparams[1], fitparams[2], fitparams[3])
    plt.plot(xf, yf, linestyle="dashed")
    plt.savefig(out)


def get_fit(data_dict, fit_func, p0, name=None):
    """
    Get the parameters of a fit function from some data.
    Params:
        data_dict: a dictionary, one of the items in the dictionary returned
        by get_data.
        fit_func: a dictionary of fit functions, indexed by the dictionary key
        that the y values are contained in within data_dict (e.g. 'ns/day').
        p0: initial guesses for fit parameters (a, b, c, etc). A dictionary of
        lists.
        name - how to name the generated plot if there's a problem with the fit
    Returns:
        fits, a list, the popt values from scipy's curve_fit function
    """
    x = data_dict['x']
    ys = {}
    for key, value in data_dict['y'][0].items():
        ys[key] = []
    fits = copy.copy(ys)
    for item in data_dict['y']:
        for key, value in item.items():
            ys[key].append(value)
    for key in fits:
        y = ys[key]
        x_sort, y_sort = sort_together([x, y])
        popt, pcov = curve_fit(fit_func[key], x_sort, y_sort, p0[key])
        err = abs(np.mean(np.sqrt(np.diag(pcov))/popt))
        if err > 5:
            print("Bad fit suspected in "+str(name))
            name = ''.join(ch for ch in key+name if ch.isalnum())
            plot_fit(x_sort, y_sort, fit_func[key],
                     key+" "+name, popt, name+".pdf")
        fits[key] = popt.tolist()
    return fits


def test():
    results = []
    directory = "/home/rob/benchout/jade2"
    matches = ["meta:Machine=JADE2"]
    label = "slurm:program"
    x = "run:Totals:Number of atoms"
    y = ["run:Totals:ns/day", "run:Totals:J/ns"]
    results = main(directory, label, matches, x, y)


def main(directory, label, matches, x, y):
    """
    Get the parameters of fits for a range of hpcbench outputs.
    Params:
        directory: directory in which the json files are stored, a string
        label: label by which the benchmarks will be indexed, a string
        (specifying their location within the json file, e.g. slurm:program)
        matches: a list of strings specifying how values have to be set in the
        json files to be included in the comparison, e.g.
        ["meta:Machine=JADE2"]
        x: the location of the x data within the json files (a string)
        y: the location of the y data within the json files (a list of strings)
    Returns:
        a list of dictionaries, with each dictionary containg the fit
        parameters, fit functions, and meta info.
    """
    if label == None:
        label = matches[0]
    results = []
    dicts = get_data(matches, x, y, label, directory, wildcard=True)
    for key, value in dicts.items():
        for item in range(len(value["y"])):
            new_dict = {}
            for key2, value2 in value["y"][item].items():
                new_dict[key2.split(":")[-1]] = value2
            value["y"][item] = new_dict
        results_item = {}
        fits = get_fit(value, fiteq, p0, key)
        results_item["fits"] = fits
        for match in matches:
            res_value = match.split("=")[1]
            res_key = match.split("=")[0].split(":")[-1]
            results_item[res_key] = res_value
        results_item[label.split(":")[-1]] = key
        results_item['eqns'] = {}
        for key2, value2 in fiteq.items():
            results_item['eqns'][key2] = value2.__name__
        results.append(results_item)
    return results


if __name__ == "__main__":
    args = parser.parse_args()
    results = main(args.directory, args.label, args.match, args.x, args.y)
    if os.path.exists(args.out):
        with open(args.out, "r") as file:
            previous_results = json.load(file)["fits"]
    else:
        previous_results = []
    previous_results += results
    with open(args.out, "w") as file:
        previous_results = json.dump({"fits": previous_results}, file,
                                     indent=4)
