#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hpcbench cli launcher utility
"""

__version__ = '0.1'

import sys
import os

has_color = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty(
    ) and sys.platform != 'Pocket PC' and (
    sys.platform != 'win32' or 'ANSICON' in os.environ)


class color:
    """
    This class defines ANSI escape codes for common colours in bash.
    """
    PURPLE = '\033[1;35;48m'
    CYAN = '\033[1;36;48m'
    BOLD = '\033[1;37;48m'
    BLUE = '\033[1;34;48m'
    GREEN = '\033[1;32;48m'
    YELLOW = '\033[1;33;48m'
    RED = '\033[1;31;48m'
    BLACK = '\033[1;30;48m'
    UNDERLINE = '\033[4;37;48m'
    RESET = '\033[1;37;0m'


_c = color()


def col(text, col, cols=_c):
    """
    Makes a string colourful.

    Args:
        text: the text to print
        col: the colour, a member of the class 'color'
        cols: an instance of the class 'color'.
    Returns:
        A new string with that colour.
    """
    if has_color:
        return col+text+cols.RESET
    else:
        return text


def print_table(d, widths, colours=None, header=None, indentation=0,
                short=False):
    """
    Prints the table returned from filter_tag with nice colours and formatting.

    Args:
        d, the output of filter_tag, a list of lists where the first index is
        the column of the table and the second is the row.
        widths: a list of integers as long as one of the rows of the table,
        specifying the with of each row.
        colours: the same, but specifying the colour of each row, a member of
        the class color.
        header: A string, the table header.
        indentation: how many characters to indent the table by, an int.
    Returns:
        nothing. Prints the table.
    """
    if short:
        print(col(header, colours[0])+": "+", ".join([r[0] for r in d]),
              end="")
        return

    if (has_color is False or colours is None):
        colours = [""]*len(widths)
    table = ""
    if header:
        table += col(header+"\n", _c.UNDERLINE+_c.BOLD)
    for row in range(len(d)):
        table += " "*indentation
        for column in range(len(d[row])):
            column_item = d[row][column]
            spaces = widths[column]
            added_spacing = spaces - len(column_item)
            table += col(column_item+(" "*added_spacing)+" ", colours[column])
        if row < len(d)-1:
            table += "\n"
    if table != "" and table != "\n":
        print(table)


def filter_tag(tools, tags, add_tags=False, ignore_tags=[]):
    """
    This function peruses the 'tools' data structure, which is a list of
    dictionaries containing information about different tools, and returns a
    table that can be printed by print_table.

    Args:
        tools: the 'tools' data structure, a list of dictionaries (of lists)
        add_tags: whether to display the tool's tags in the table itself, a
        bool
        tags: a list of tags to include in the table
        ignore_tags: a list of tags to ignore

    Returns:
        filtered_table, a list of lists, where the first index is the column
        of the table and the second is the row.
    """
    if type(tags) != list:
        tags = [tags]
    filtered_table = []
    for tool in tools[:]:
        if set(tags).issubset(tool["Tags"]):
            if add_tags:
                for unprintable_tag in ignore_tags:
                    if unprintable_tag in tool["Tags"]:
                        tool["Tags"].remove(unprintable_tag)
                filtered_table.append(
                    [tool["Names"][0], tool["Help"],
                     "("+", ".join(tool["Tags"])+")"])
            else:
                filtered_table.append([tool["Names"][0], tool["Help"]])
            tools.remove(tool)
    return filtered_table


cwd = os.path.dirname(os.path.abspath(__file__))

tools = []

tools.append({"Names": ["collate"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "logger", "collate.py"),
              "Help": "Combine multiple json files together"})

tools.append({"Names": ["cpulog"],
              "Tags": ["logger"],
              "Location": os.path.join(cwd, "logger", "cpulog.py"),
              "Help": "Log CPU usage to a json file"})

tools.append({"Names": ["extra"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "logger", "extra.py"),
              "Help": "Write arbitrary info into a json file"})

tools.append({"Names": ["gmxlog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "gmxlog.py"),
              "Help": "Convert a gromacs md log to a json file"})

tools.append({"Names": ["nvlog", "gpulog"],
              "Tags": ["logger"],
              "Location": os.path.join(cwd, "logger", "gpulog.py"),
              "Help": "Log info from nvidia-smi to a json file"})

tools.append({"Names": ["slurmlog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "slurm.py"),
              "Help": "Convert SLURM parameters to a json file"})

tools.append({"Names": ["infolog", "sysinfo"],
              "Tags": ["logger"],
              "Location": os.path.join(cwd, "logger", "sysinfo.py"),
              "Help": "Write generic system info to a json file"})

tools.append({"Names": ["syslog"],
              "Tags": ["logger"],
              "Location": os.path.join(cwd, "logger", "syslog.py"),
              "Help": "Log values from /sys/ to a json file"})

tools.append({"Names": ["scaling"],
              "Tags": ["plot"],
              "Location": os.path.join(cwd, "plot", "scaling.py"),
              "Help": "Plot scaling to a PDF (incl. stack plots)"})

tools.append({"Names": ["log"],
              "Tags": ["plot"],
              "Location": os.path.join(cwd, "plot", "logs.py"),
              "Help": "Plot logs to a pdf (e.g. temperature, utilisation)"})

tools.append({"Names": ["findjob"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "util", "find_job.sh"),
              "Help": "Find the location of a slurm job by its job ID"})

tools.append({"Names": ["recrun"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "util", "recursive_run.sh"),
              "Help": "Run a script on every file with some filename"})

tools.append({"Names": ["insert"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "util", "updatejson.py"),
              "Help": "Insert object(s) from one json file into another"})

tools.append({"Names": ["amberlog", "amblog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "amberlog.py"),
              "Help": "Convert an amber md log to a json file"})

tools.append({"Names": ["namdlog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "namdlog.py"),
              "Help": "Convert namd stdout output to a json file"})

tools.append({"Names": ["lmplog", "lammpslog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "lmplog.py"),
              "Help": "Convert a lammps log file to a json file"})

tools.append({"Names": ["ommlog", "openmmlog"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "logger", "ommlog.py"),
              "Help": "Tidy up openmm benchmark output"})

tools.append({"Names": ["slurm"],
              "Tags": ["prep", "scheduler"],
              "Location": os.path.join(cwd, "schedulers", "slurm.py"),
              "Help": "Manage submission of large numbers of SLURM jobs"})

tools.append({"Names": ["makejob", "job"],
              "Tags": ["prep"],
              "Location": os.path.join(cwd, "systemprep", "make_job.py"),
              "Help": "Create a job submission script from a template"})

tools.append({"Names": ["makejobs", "jobs"],
              "Tags": ["prep"],
              "Location": os.path.join(cwd, "systemprep", "make_jobs.py"),
              "Help": "Make many job submission scripts at once"})

tools.append({"Names": ["sacct"],
              "Tags": ["parser"],
              "Location": os.path.join(cwd, "schedulers", "sacct.py"),
              "Help": "Write sacct info into a json file"})

tools.append({"Names": ["crosswalk"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "logger", "crosswalk.py"),
              "Help": "Convert benchmark output files to a standard format"})

tools.append({"Names": ["stall"],
              "Tags": ["util"],
              "Location": os.path.join(cwd, "util", "stall.sh"),
              "Help": "Sleep until a specified job is finished"})

tools.append({"Names": ["table"],
              "Tags": ["plot"],
              "Location": os.path.join(cwd, "plot", "table.py"),
              "Help": "TODO"})


def entry_point():
    """
    This is the hpcbench entry point, it's the code that runs when you type
    hpcbench in the terminal. This function either prints a fancy help
    message or launches the appropriate hpcbench script.

    Args:
        None, but reads sys.argv

    Args:
        None, but launches utilities or prints help
    """
    get_help = (len(sys.argv) == 1)
    if get_help:
        col_widths = [10, 68, 20]
        ignore = ["Coexistence", "PMFs", "Common", "System prep"]
        header_col = ""
        print("hpcbench version "+__version__ + ". ", _c.PURPLE)
        log = filter_tag(tools, ["scheduler"], ignore_tags=ignore)
        print_table(log, col_widths, header=col("Schedulers", header_col),
                    colours=[_c.RED, "", ""])
        print("")
        log = filter_tag(tools, ["prep"], ignore_tags=ignore)
        print_table(log, col_widths, header=col("System prep", header_col),
                    colours=[_c.PURPLE, "", ""])
        print("")

        log = filter_tag(tools, ["logger"], ignore_tags=ignore)
        print_table(log, col_widths, header=col("Logging", header_col),
                    colours=[_c.GREEN, "", ""])

        print("")

        log = filter_tag(tools, ["parser"], ignore_tags=ignore)
        print_table(log, col_widths, header=col("Parsers", header_col),
                    colours=[_c.BLUE, "", ""])
        print("")
        plot = filter_tag(tools, ["plot"], ignore_tags=ignore)
        print_table(plot, col_widths, header=col("Plot", header_col),
                    colours=[_c.CYAN, "", ""])
        print("")
        plot = filter_tag(tools, ["util"], ignore_tags=ignore)
        print_table(plot, col_widths, header=col("Utilities", header_col),
                    colours=[_c.YELLOW, "", ""])
    elif len(sys.argv) > 1:
        for tool in tools:
            names = [name.replace('-', '_') for name in tool["Names"]] + \
                [name.replace('-', '') for name in tool["Names"]]+tool["Names"]
            if sys.argv[1] in names:
                curr_tool = tool

        try:
            if ".py" in curr_tool["Location"]:
                runwith = "python"
            if ".sh" in curr_tool["Location"]:
                runwith = "bash"
            args = runwith+" "+curr_tool["Location"]+" "+" ".join(sys.argv[2:])
            os.system(args)
        except UnboundLocalError:
            print("No tool found with name '" +
                  sys.argv[1]+"'. Run hpcbench with no arguments for a list.")


if __name__ == "__main__":
    entry_point()
