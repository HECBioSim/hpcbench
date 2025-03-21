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
parser.add_argument("-c", "--hardcode", action="store_true",
                    help="Add hardcoded meta info")
parser.add_argument("-b", "--debug", action="store_true",
                    help="Print debug info showing the quality of the fits")
parser.add_argument("-n", "--nodummy", action="store_true",
                    help="Don't add dummy data for missing benchmarks")

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

def fit_ten(x, a, b, c, d):
    """
    """
    #return a*10**((-b*x)+c)+d
    return 10**((-a*x)+(x*np.log10(b))+c)+d

def fit_pow(x, a, b):
    """
    An exponential function of the form ae^(1-log(bx))
    """
    return a*np.exp(1 - np.log(b*x))

def fit_log(x, a, b, c):
    return a*np.log(x*b + c)

def fit_mono_exp(x, a, b, c):
    return a * np.exp(b * x) + c

def fit_inv(x, a, b, c):
    return a*(1./(np.log(x*b)))+c

def fit_log_poly(x, a, b, c, d):
    """
    A third-degree polynomial of the form ax^3 + bx^2 + cx + d
    """
    return np.log(a*x**3 + b*np.log(x)**2 + c*x + d)

# lookup tables - append if needed (these should probably be command line args)
fiteq = {"ns/day": fit_poly, "J/ns": fit_poly} # fit functions for json fields
#p0 = {"ns/day": [7e6,  -1e-6, 3], "J/ns": [0.00001, 0.001, 0.1, 1]} # p0 for fit
#p0 = {"ns/day": [7e6, 1, -1e-6], "J/ns": [0.00001, 0.001, 0.1, 1]} # p0 for fit
p0 = {"ns/day": [0.0001, 1, 0, 0], "J/ns": [0.00001, 0.001, 0.1, 1]} # p0 for fit
log_transform = {"ns/day": True, "J/ns": False} # whether to do a log transform

maxnodes_atoms = [20000, 61000, 465000]
maxnodes_nodes = [3, 5, 12]
popt, pcov = curve_fit(fit_log, maxnodes_atoms, maxnodes_nodes, p0=[1, 1, 1])

hardcoded = {
    "maxnodes": {
        "fits": list(popt),
        "eqns": {"nodes": "fit_log"},
        "Machine": "ARCHER2",
        "meta": "Max nodes"
    },
    "gbperatomperns": 9.5/(5*1000000),
    "info": "hardcoded",
    "kwhperj": 2.7777778e-7,
    "storagepergbpernsperatom": 0.0000019,
    "ukavgkwhdar": 2700 / 365.25,
    "html": {
        "row": '<div class="res-row $class"><i class="fa $icon"></i> $text</div>',
        "option": '<option value="$name">$text</option>'
    },
    "atomwarning": "WARNING: your system contains $equality atoms than our $size test system. These results from this tool are probably wrong!",
    "texticons": {
        "node-hours": "fa-clock-o",
        "ns-day": "fa-solid fa-gauge",
        "storage-gb": " fa-hdd-o",
        "power-kwh": "fa-bolt",
        "house-days": "fa-home",
        "max-nodes": "fa-server",
        "message": "fa-warning",
    },
    "minmax": {
        "atoms": [19000, 3000000]
    },
    "textlabels": {
        "storage-gb": "$resultGB of storage",
        "ns-day": "$result ns/day",
        "power-kwh": "$result kWh of power",
        "house-days": "...which could power an average UK home for $result days",
        "node-hours": "$result node hours",
        "max-nodes": "1 node recommended for maximum efficiency",
        "message": "$result"
    }
}

# first the thing needs to get data from these
# also dummy data with a message for missing systems

dummy_data = [
    {
     "Machine":"ARCHER2",
     "program":"OpenMM",
     "nodata":"No data is available for OpenMM on ARCHER2. As OpenMM only "
     "provides a reference implementation on CPU, using it on CPU-based "
     "systems is not recommended.",
     },
    {
     "Machine":"LUMI-G",
     "program":"OpenMM",
     "nodata":"No data is available for OpenMM on LUMI-G. OpenMM "
     "theoretically supports AMD via the openmm-hip plugin, however this "
     "plugin was not compatible with the ROCm version supplied on LUMI-G and "
     "the OpenMM version required to run the benchmark. As ROCm support on "
     "OpenMM is not official, please proceed with caution!"
     }
]

messages = [
    {"keys": {
        "Machine": "ARCHER2",
        "program": "AMBER"},
    "values": {
        "message": "Warning: AMBER is primarily written for GPUs! It will run "
                   "badly on CPU-based systems like ARCHER2."}
    },
    {"keys": {
        "Machine": "JADE2",
        "program": "LAMMPS"},
    "values": {
        "message": "Warning: LAMMPS is not yet fully GPU-resident and some "
                   "features/fixes are not available on GPU."}
    },
    {"keys": {
        "Machine": "Grace Hopper Testbed",
        "program": "LAMMPS"},
    "values": {
        "message": "Warning: LAMMPS is not yet fully GPU-resident and some "
                   "features/fixes are not available on GPU."}
    },
]

def combine(original, new):
    """
    For a dictionary of fits created in the main function, append comments and
    other miscellaneous data to that dictionary.
    Args:
        original - the dictionary of results created by main()
        new - a list of dictionaries of dictionaries to append, of the
        following format, each dictionary contining a ["keys"] dictionary, which
        contains keys and values  that the target dictionary has to match, e.g.
        "Machine":"ARCHER2" and a ["values"] dictionary which contains the
        values that will be added to the results.
    Returns:
        the combined dictionary.
    """
    for new_item in new:
        for orig_item_idx in range(len(original)):
            orig_item = original[orig_item_idx]
            if new_item["keys"].items() <= orig_item.items():
                for key, value in new_item["values"].items():
                    original[orig_item_idx][key] = value
    return original
    

def plot_fit(x, y, fiteq, title, fitparams, out, loglog=False):
    """
    Plot the outcome of a fit found in get_fit.
    Args:
        x, y: data to fit (1-d arrays\lists)
        fiteq: equation used to get the fit (a function)
        title: plot title (a string)
        fitparams: parameters for fiteq (a list of floats)
        out: filename for plot output (a string)
    """
    if loglog:
        plt.plot = plt.loglog
    plt.figure()
    plt.title(title)
    plt.plot(x, y)
    xf = np.linspace(min(x), max(x))
    yf = fiteq(xf, *fitparams)
#    if len(fitparams) == 2:
#        yf = fiteq(xf, fitparams[0], fitparams[1])
#    if len(fitparams) == 3:
#        yf = fiteq(xf, fitparams[0], fitparams[1], fitparams[2])
#    if len(fitparams) == 4:
#        yf = fiteq(xf, fitparams[0], fitparams[1], fitparams[2], fitparams[3])
    plt.plot(xf, yf, linestyle="dashed")
    plt.savefig(out)


def get_fit(data_dict, fit_func, p0, log_transform, name=None):
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
        if log_transform[key]:
            x_sort = np.log10(x_sort)
            y_sort = np.log10(y_sort)
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


def main(directory, label, matches, x, y, hardcode=False):
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
        fits = get_fit(value, fiteq, p0, log_transform, key)
        results_item["fits"] = fits
        for match in matches:
            res_value = match.split("=")[1]
            res_key = match.split("=")[0].split(":")[-1]
            results_item[res_key] = res_value
        results_item[label.split(":")[-1]] = key
        results_item['log'] = log_transform
        results_item['eqns'] = {}
        for key2, value2 in fiteq.items():
            results_item['eqns'][key2] = value2.__name__
        results.append(results_item)
    if hardcode:
        results = combine(results, messages)
        if hardcoded not in results:
            results.append(hardcoded)
    return results

def sample_test(x, y, fit_func, fitparams, log_transform, unit="ns/day"):
    a, b, c, d = fitparams
    for atom, ns in zip(x, y):
        if log_transform:
            print("For "+str(atom)+" atoms, func = "+str(10**(fit_func(np.log10(atom), a, b, c, d)))+" "+unit+" (real answer: "+str(ns)+" "+unit+")")
        else:
            print("For "+str(atom)+" atoms, func = "+str(fit_func(atom, a, b, c, d))+" "+unit+" (real answer: "+str(ns)+" "+unit+")")

def test2(directory="/home/rob/benchout/jade2",
          matches=["meta:Machine=JADE2"],
          label = "slurm:program",
          x = "run:Totals:Number of atoms",
          y = ["run:Totals:ns/day", "run:Totals:J/ns"],
          plot=False):
    #directory = "/home/rob/benchout/jade2"
    #matches = ["meta:Machine=JADE2"]
    #matches = ["meta:Machine=JADE2","slurm:program=GROMACS"]
    #label = "slurm:program"
    #x = "run:Totals:Number of atoms"
    #y = ["run:Totals:ns/day", "run:Totals:J/ns"]
    
    results = []
    dicts = get_data(matches, x, y, label, directory, wildcard=True)
    for key, value in dicts.items():
        for item in range(len(value["y"])):
            new_dict = {}
            for key2, value2 in value["y"][item].items():
                new_dict[key2.split(":")[-1]] = value2
            value["y"][item] = new_dict
        results_item = {}
        fits = get_fit(value, fiteq, p0, log_transform, key)
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

    for key, value in dicts.items():
        for result in results:
            if result["program"] == key:
                res_value = result
        xs = value["x"]
        ys = {}
        for key2, value2 in value['y'][0].items():
            ys[key2] = []
        fits = copy.copy(ys)
        for item in value['y']:
            for key2, value2 in item.items():
                ys[key2].append(value2)
        
        name = res_value["Machine"]+"_"+res_value["program"]
        xsrt, ysrt = sort_together([xs, ys["ns/day"]])
        xenergy, yenergy = sort_together([xs, ys["J/ns"]])
        #print(res_value)
        print("---")
        if plot:
            plot_fit(np.log10(xsrt), np.log10(ysrt), fit_poly, name, res_value["fits"]["ns/day"], "/home/rob/Downloads/"+name+".pdf", loglog=True)
        print(key+":")
        print("xsrt: "+str(xsrt))
        print("ysrt: "+str(ysrt))
        print("res: "+str(res_value["fits"]["ns/day"]))
        print("log_transform: "+str(log_transform))
        
        sample_test(xsrt, ysrt, fit_poly, res_value["fits"]["ns/day"], log_transform=True)
        sample_test(xenergy, yenergy, fit_poly, res_value["fits"]["J/ns"], log_transform=False, unit="J/ns")
    
    

#test2()

if __name__ == "__main__":
    args = parser.parse_args()
    results = main(args.directory, args.label, args.match, args.x, args.y,
                   hardcode=args.hardcode)
    if args.nodummy:
        dummy_data = []
    if os.path.exists(args.out):
        with open(args.out, "r") as file:
            previous_results = json.load(file)["fits"]
    else:
        print("all is destroyed")
        previous_results = dummy_data
    previous_results += results
    with open(args.out, "w") as file:
        previous_results = json.dump({"fits": previous_results}, file,
                                     indent=4)
    if args.debug:
        test2(args.directory, args.match, args.label, args.x, args.y)
