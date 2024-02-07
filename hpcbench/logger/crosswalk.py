#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standardise information from different benchmark outputs.
"""

from hpcbench.deps.numericalunits import s, ns, ms, hour, W, Wh, kWh, day
from hpcbench.plot.util import bodge_numeric_dict_wrapper
import copy

totals = {
        "Atoms": "2997924",
        "Elapsed(s)": "2366.06",
        "Per Step(ms)": "236.61",
        "ns/day": "0.73",
        "seconds/ns": "118302.93"
}

# TODO: add energy use: kwh/ns, kwh/step, kwh total, kwh/step/atom

unitlookup = {
    "Wall time (s)": s,
    "ns/day": ns/day,
    "day/ns": day/ns,
    "ns/s": ns/s,
    "s/ns": s/ns,
    "s/step": s,
    "hours/ns": hour/ns,
    "steps/s": 1/s,
    "step/s": 1/s,
    "Wall Clock Time (s)": s,
    "hours/ns,": hour/ns,
    "timesteps/s,": 1/s,
    "timesteps/s": 1/s,
    "Elapsed(s)": s,
    "seconds/ns": s/ns,
    "second/ns": s/ns,
    "Steps/second": 1/s,
    "Number of atoms": 1,
    "Atoms": 1,
    'CPU Time (s)': s,
    'Wall Clock Time including setup (s)': s,
    'Setup time': s,
    'Giga-Cycles': 1,
    'Mflops': 1,
    'Steps': 1,
    'Timestep': ns,
    'hour/ns': hour/ns,
    "s/step": s,
    "Per Step(ms)": ms,
}

# Used to rename quantities from the benchmark outputs so that they have the
# same names. Useful later when plotting results from different programs
# against one another.
crosswalk = {
    "Wall time (s)": "Wall Clock Time (s)",
    "timesteps/s,": "steps/s",
    "Elapsed(s)": "Wall Clock Time (s)",
    "seconds/ns": "s/ns",
    "Steps/second": "step/s",
    "Steps/s": "step/s",
    "days/ns": "day/ns",
    'CPU Time (s)': "Wall Clock Time (s)",
    "Atoms": "Number of atoms",
    "timesteps/s": "step/s",
    "Per Step(ms)": "s/step",
}

# The stanrdardised names of each quantity.
standard_original = {
    "Wall Clock Time (s)": None,
    "Number of atoms": None,
    "step/s": None,
    "ns/s": None,
    "ns/day": None,
    "s/step": None,
    "s/ns": None,
    "day/ns": None,
}

def standardise_totals(totals):
    """
    Rename quantities from a hpcbench output file to have standard names and
    units.
    
    Params:
        totals: the 'Totals' block from a hpcbench output file, a dictionary.
    
    Returns:
        The same block, with standardised names and units.
    """
    
    standard = copy.copy(standard_original)
    totals = bodge_numeric_dict_wrapper(totals)

    # Identify names and units of quantities
    for name, value in totals.items():
        units = unitlookup[name]
        if name in crosswalk:
            name = crosswalk[name]
        if name in standard:
            standard[name] = value * units

    # If ns/s is missing, convert ns/day to units of ns/s
    if standard["ns/s"] is None and standard["ns/day"] is not None:
        unitless = standard["ns/day"] / (ns/day)
        converted = unitless / (day/s)
        standard["ns/s"] = converted * ns/s
    
    if standard["step/s"] is None and standard["Wall Clock Time (s)"]:
        if 'Steps' in totals:
            standard["step/s"] = totals['Steps'] / \
                standard["Wall Clock Time (s)"]

    # Set missing values of reciprocals
    for name, value in standard.items():
        if value is None:
            if "/" in name:
                backwards = "/".join(list(reversed(name.split("/"))))
                if backwards in standard and standard[backwards] is not None:
                    standard[name] = 1/standard[backwards]
    
    # Give quantities back in real units
    for key, value in standard.items():
            standard[key] = (value / unitlookup[key])
    
    return standard