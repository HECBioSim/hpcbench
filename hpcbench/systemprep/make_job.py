#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Createa a HPC job script from a template
"""

from string import Template
import argparse
from pathlib import Path
import glob
import os


here = Path(__file__).parent  # hack
templates_dir = here.parent.joinpath("job_scripts")
available_templates = glob.glob(str(templates_dir)+os.path.sep+'*.sh')


def list_available_templates(available_templates):
    """
    From the avilable templates (found in the job_scripts folder) list the
    filenames and the string template variables.

    Note: unusually, this is listed before the argument parser, as the
    resulting string is displayed in the script's help function.

    Args:
        available_templates: a list of strings, filenames for templates

    Returns:
        a string listing all the filenames and variables that need to be filled
        out for each one.
    """
    output = ""
    for template in available_templates:
        params = []
        with open(template, "r") as file:
            s = Template(file.read())
        params = [m.group('named') or m.group('braced')
                  for m in s.pattern.finditer(s.template)
                  if m.group('named') or m.group('braced')]
        output += os.path.basename(
            template)+" - params: "+", ".join(list(set(params)))+'\n'
    return output


parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Create a HPC submission script from a template.\n\n"
        "You can optionally supply one of a list of premade "
        "templates:\n"+list_available_templates(available_templates))
parser.add_argument('-s', '--substitute',
                    action=type('', (argparse.Action, ),
                                dict(__call__=lambda a, p, n, v, o:
                                     getattr(n, a.dest).update(
                                         dict([v.split('=')])))), default={},
                    help="Call with template string substitutions, e.g. x=y."
                    " Call this multiple times to replace multiple strings.")
parser.add_argument("template", type=str, help="Input template file")
parser.add_argument("output", type=str, help="Output script file.")
parser.add_argument("-p", "--prefix", type=str, nargs="+",
                    help="Add extra lines into the job script, before the MD "
                    "run. Call multiple times to add multiple lines.")
parser.add_argument("-o", "--postfix", type=str, nargs="+",
                    help="Add extra lines into the job script, after the MD "
                    "run. Call multiple times to add multiple lines.")


def insert_fixes(template_text, prefix_lines, postfix_lines):
    """
    Add pre and postfixes to an MD job script. The script must have markers
    indicating where these go, in the forms of lines consisting of '###PREFIX'
    and '###POSTFIX'.

    Args:
        template_text: a string, the text of the job script
        prefix_lines: a list of strings, one for each prefix line
        postfix_lines: a list of strings, one for each postfix line

    Returns:
        a string, the text of the modified job script
    """
    prefix_loc = None
    postfix_loc = None
    template_lines = template_text.split("/n")
    for line_no in range(len(template_lines)):
        if template_lines[line_no] == "###PREFIX":
            prefix_loc = line_no
        if template_lines[line_no] == "###POSTFIX":
            postfix_loc = line_no
    if postfix_loc:
        template_lines.insert(postfix_loc+1, postfix_lines)
    if prefix_loc:
        template_lines.insert(prefix_loc+1, prefix_lines)
    return "\n".join(template_lines)


def fill_template(template_text, fill_dict):
    """
    Replaces the contents of a template file using python string templates
    (where variables are indicated by the syntax $var). Also converts £ to $
    in the template - this is a hack used to stop python from trying to fill
    in bash variables.

    Args:
        template_text: a python template string
        fill_dict: a dictionary, where the keys are template variables and the
        values are the strings that will replace them.

    Returns:
        the modified template_text, a string
    """
    substituted = template_text.substitute(fill_dict)
    substituted = substituted.replace("£", "$")
    return substituted


def make_job(template, output, substitutions, prefix=None, postfix=None):
    """
    For a given job script template (in the python string template format),
    replace the items in the template file with values according to a
    a dictionary of substitutions. Also, optionally, add a prefix and postfix
    to the template (arbitrary lines inserted before and after the md [or
    whatever] run).

    Args:
        template: a string, either an absolute path to the template file or the
        name of a file from the job_scripts folder in the hpcbench module.
        output_string: name of the output file.
        substitutions: a dictionary, where the keys are template variables and
        the values are the strings that will replace them.
        prefix: text to be added in the 'prefix' section of the job script. a
        list of strings, one for each prefix line.
        postfix_lines: a list of strings, one for each postfix line.
    Returns:
        nothing, but writes out a file.
    """
    try:
        with open(template, "r") as file:
            template_text = Template(file.read())
    except FileNotFoundError:
        with open(str(templates_dir)+os.path.sep+template, "r") as file:
            template_text = Template(file.read())
    template_filled = fill_template(template_text, substitutions)
    if prefix or postfix:
        template_filled = insert_fixes(
            template_filled, prefix, postfix)
    with open(output, "w") as file:
        file.write(template_filled)


if __name__ == "__main__":
    args = parser.parse_args()
    make_job(args.template, args.output, args.substitute, args.prefix,
             args.postfix)
