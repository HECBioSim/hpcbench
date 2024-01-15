#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create bulk HPC jobs based on a template and a set of parameters.
"""

import itertools
from collections import OrderedDict
from hpcbench.systemprep.make_job import (make_job, available_templates,
                                          list_available_templates,
                                          templates_dir)
import hpcbench.schedulers
import os
import shutil
import re
import argparse
from pkgutil import iter_modules
import importlib
import sys
p = os.path

# TODO: params can have default values which can be specified by a comment in
# the bash script, these should be loaded automatically
# also: would be good if you could provice multiple sets of extra files, and it
# loops over all of them?

all_schedulers = [x.name for x in iter_modules(hpcbench.schedulers.__path__)]

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Create multiple HPC submission script from a template, "
        "and optionally submit them.\n\n"
        "You can optionally supply one of a list of premade "
        "templates:\n"+list_available_templates(available_templates))
parser.add_argument('-s', '--substitute',
                    action=type('', (argparse.Action, ),
                                dict(__call__=lambda a, p, n, v, o:
                                     getattr(n, a.dest).update(
                                         dict([v.split('=')])))), default={},
                    help="Call with template string substitutions, e.g. x=y."
                    " Call this multiple times to replace multiple strings. "
                    "Call with multiple values e.g. a=x,y,z to create "
                    "multiple permutations.")
parser.add_argument("-t", "--template", type=str,
                    help="Input template file")
parser.add_argument("-o", "--output", type=str,
                    help="Output directory name.")
parser.add_argument("-p", "--prefix", type=str, nargs="+",
                    help="Add extra lines into the job script, before the MD "
                    "run. Call multiple times to add multiple lines.")
parser.add_argument("-f", "--postfix", type=str, nargs="+",
                    help="Add extra lines into the job script, after the MD "
                    "run. Call multiple times to add multiple lines.")
parser.add_argument("-e", "--extra", type=str, nargs="+",
                    help="Extra files to include with the job script, e.g. "
                    "input and structure files. Call multiple  times to"
                    " include multiple files.")
parser.add_argument("-w", "--overwrite", action="store_true", help="If the "
                    "output directory already exists, delete and replace it "
                    "instead of throwing an error.")
parser.add_argument("-c", "--cat", type=str, help="View the contents of one of"
                    " the included template files (listed above).")
parser.add_argument("-d", "--schedule", type=str, help="Submit the jobs "
                    "to the HPC system, specifying the scheduler. Can be one "
                    "of: "+", ".join(all_schedulers))


def combine_values(jobparams):
    """
    Create all possible combinations of some dictionary of HPC job parameters.

    Args:
        jobparams, a dictionary of lists of strings

    Returns:
        a list of dictionaries of strings, representing every possible
        combination of values for those strings.
    """
    jobs = []
    permutations = list(itertools.product(*jobparams.values()))
    for permutation in permutations:
        job = {}
        for key, value in zip(jobparams.keys(), permutation):
            job[key] = value
        jobs.append(job)
    return jobs


def make_name(job, name_list, use_key=False):
    """
    Set the name for a HPC job script/folder.

    Args:
        job, a dictionary containing python string template parameteres.
        name_list: a list of strings which should be used to name the script.
        Normally the name list should be the parameters that change between
        jobs.
        use_key: add the key to the name as well as the value. Optional.

    Returns:
        the name, a string.
    """
    name = ""
    for key, value in job.items():
        if not use_key:
            add = value+"_"
        else:
            add = key+"_"+value+"_"
        if key in name_list or name_list == []:
            name += add
    clean = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)
    return clean[:-1]


def make_jobs(jobparams, template, outdir, extrafiles=[],
              prefix=None, postfix=None, name=[], override=False):
    """
    For a set of job parameters, create a set of HPC jobs.

    Args:
        jobparams: a dictionary of lists of strings, where the dictionary keys
        correspond to string template parameters in the template job script.
        The lists are possible values, e. g. 1, 2, 4, 8 GPUs, and jobs with all
        possible combinations of values will be created.
        template: path to a file to be used as the python string template.
        Should have a number of template_parameters $param equal to the keys of
        the jobparams dictionary.
        outdir: output directory, will be created.
        extrafiles: a list of strings, paths to files, which will be included
        with each job script.
        prefix: a list of strings, each string should be a line of text to be
        added to each job script, after the ###PREFIX header.
        postfix: a list of strings, each string should be a line of text to be
        added to each job script, after the ###POSTFIX header.
        name: optional, a list of strings denoting which keys to name the
        resulting files and folders after. If this is ignored, it will be
        set automatically.
        override: a boolean, optional. If this is set to true, and there is
        already a directory qwith the naem of the outdir, it will be deleted
        before the outdir is created.

    Returns
        job_paths: a list of strings with paths to the created jobs.
    """
    if name == []:
        for key, value in jobparams.items():
            if len(value) > 1:
                name.append(key)
    try:
        os.mkdir(outdir)
    except FileExistsError as e:
        if override:
            shutil.rmtree(outdir)
            os.mkdir(outdir)
        else:
            raise e
    jobs = combine_values(jobparams)
    job_paths = []
    for job in jobs:
        curr_dir = make_name(job, name)
        os.mkdir(outdir+p.sep+curr_dir)
        job_path = outdir+p.sep+curr_dir+p.sep+curr_dir+".sh"
        job_paths.append(job_path)
        make_job(template, job_path, job, prefix=prefix, postfix=postfix)
        for file in extrafiles:
            shutil.copyfile(file, outdir+p.sep+curr_dir+p.sep+p.basename(file))
    return job_paths


def test():
    jobparms = OrderedDict({
        "jobname": ["test"],
        "num_gpus": ["gres:1", "gres:2", "gres:4", "gres:8"],
        "partition": ["small"],
        "benchmarkfile": ["benchmark.tpr"],
        "comment": ["test"],
        "machine": ["JADE", "ARCHER"],
        "benchout": ["output"],
    })
    template = "jade_gromacs_gpu.sh"
    outdir = "/home/rob/Downloads/test"
    extrafiles = ["/home/rob/Downloads/sminfo.txt"]
    make_jobs(jobparms, template, outdir, extrafiles=extrafiles)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.cat:
        with open(str(templates_dir)+p.sep+args.cat, "r") as file:
            print("#Contents of "+str(str(templates_dir)+p.sep+args.cat))
            lines = file.read()
            print(lines)
            sys.exit(0)
    if args.template is None:
        sys.exit("Template (--t) is required!")
    if args.output is None:
        sys.exit("Output directory (-o) is required!")
    jobparams = {}
    for key, value in args.substitute.items():
        jobparams[key] = value.split(",")
    jobs = make_jobs(jobparams, args.template, args.output,
                     extrafiles=args.extra, prefix=args.prefix,
                     postfix=args.postfix, override=args.overwrite)
    if args.schedule:
        scheduler = importlib.import_module(
            'hpcbench.schedulers.'+args.schedule)
        scheduler.process_queue(jobs)
    else:
        print("Jobs created: "+", ".join(jobs))
