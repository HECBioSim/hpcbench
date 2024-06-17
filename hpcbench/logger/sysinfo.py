#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump system info to a file.
"""

import argparse
import json
import subprocess
from hpcbench.logger.util import (GracefulKiller, exists, parse_nvidia_smi,
                                  parse_rocm_smi)

parser = argparse.ArgumentParser(
    description="Log system info (e.g. environment modules, environment "
                "variables, cpu and memory info, gpu info...) to a json file.")
parser.add_argument("output", type=str, help="Output json file")

SMI_COLS = "name,pci.bus_id,driver_version,pstate,count,serial,uuid," \
    "pcie.link.gen.max,pcie.link.gen.current,memory.total," \
    "index,accounting.mode,vbios_version,inforom.oem,inforom.img," \
    "inforom.power,gom.current,memory.total,index,clocks.sm,clocks.mem," \
    "clocks.gr"
SMI_COMMAND = "nvidia-smi --query-gpu="+SMI_COLS+" --format=csv"

ROCM_COMMAND = "rocm-smi -a --json"


def get_sysinfo(smi_command=SMI_COMMAND):
    """
    Collect and parse info from various command-line utilities.

    Returns:
        A python dictionary containing the collected output.
    """
    sysinfo = {}
    if exists("uname"):
        uname = subprocess.run(
            ['uname', '-r'],  capture_output=True, text=True).stdout.strip()
        sysinfo["kernel-release"] = uname

    if exists("lscpu"):
        sysinfo["CPU"] = {}
        cpu = subprocess.run("lscpu",  capture_output=True,
                             text=True).stdout.strip().split("\n")
        for line in cpu:
            line = " ".join(line.split())
            sysinfo["CPU"][line.split(":")[0]] = line.split(":")[1].strip()

    if exists("module"):
        modules = subprocess.run(
            ['module', 'list'],  capture_output=True, text=True).stdout.strip()
        modules = modules.strip().split(")")[1:]
        modules_fixed = []
        for module in modules:
            modules_fixed.append(module.split(" ")[1])
        sysinfo["modules"] = modules

    if exists("nvidia-smi"):
        nvout = subprocess.run(smi_command.split(
            " "), capture_output=True, text=True).stdout.strip()
        results = {}
        results = parse_nvidia_smi(nvout, results)
        sysinfo["GPU"] = results
    if exists("rocm-smi"):
        rocmout = subprocess.run(smi_command.split(
            " "), capture_output=True, text=True).stdout.strip()
        results = {}
        results = parse_rocm_smi(rocmout, results)
        sysinfo["GPU"] = results
    else:
        print("nvidia-smi\rocm-smi not found, skpipping...")

    if exists("printenv"):
        env = subprocess.run(['printenv'],  capture_output=True,
                             text=True).stdout.strip().split("\n")
        sysinfo["env"] = env

    return sysinfo


if __name__ == "__main__":
    args = parser.parse_args()
    killer = GracefulKiller()
    info = get_sysinfo()
    with open(args.output, "w") as outfile:
        json.dump(info, outfile, indent=4)
