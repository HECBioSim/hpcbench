#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge two json files together.
"""

import argparse
import json
import os

parser = argparse.ArgumentParser("Insert values from one json file into"
                                 " another json file.")
parser.add_argument("source", type=str, help="source json file")
parser.add_argument("target", type=str, help="json file to be written into")
parser.add_argument("-l", "--sourceloc", type=str,
                    help="Get contents of source at this location, using the "
                    "syntax obj1:obj2:etc.")
parser.add_argument("-c", "--targetloc", type=str,
                    help="Write into target at this location, using the "
                    "syntax obj1:obj2:etc.")
parser.add_argument("-d", "--delete", action="store_true",
                    help="Delete source file when done.")


def get_dict_element(d, element, make=False):
    """
    Get an element from a dictionary, based on a : delimited string.
    
    Params:
        d, the dictionary
        e, a :-delimited string of dictionary keys, e.g. key1:key2:key3
        make: if there is no element d[key1][key2] etc, make an empty dict
    
    Returns:
        the element
    """
    element = element.split(":")
    for e in element:
        try:
            d = d[e]
        except KeyError as e:
            if make:
                d[e] = {}
                d = d[e]
            else:
                raise e
    return d


def update(source, target, sourceloc=None, targetloc=None, delete=False):
    """
    With two json files, merge objects from one into the other.
    
    Args:
        source: path to the source json file, a string
        target: path to the target json file, a string
        sourceloc: location within the source json file to copy from, as a
        :-delimited string.
        tagetloc: location within a the target json file to copy to, as a
        :-delmited string. Will be created if it doesn't exist.
        delte: if true, original file will be deleted.
    """
    with open(args.source, "r") as infile:
        source = json.load(infile)
    with open(args.target, "r") as infile:
        target = json.load(infile)
        
    if sourceloc:
        source = get_dict_element(source, sourceloc)
        
    if targetloc:
        new_element = get_dict_element(target, targetloc, make=True)
        for key, value in source.items():
            new_element[key] = value
                
    else:
        for key, value in source.items():
            target[key] = value
            
    with open(args.target, "w") as outfile:
        json.dump(target, outfile, indent=4)
    if delete:
        os.remove(source)


if __name__ == "__main__":
    args = parser.parse_args()
    update(args.source, args.target, args.sourceloc, args.targetloc, args.delete)