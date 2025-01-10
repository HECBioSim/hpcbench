import hpcbench
import json
import os
import glob
import argparse

FMT = "ConsumedEnergyRaw,CPUTimeRAW,ElapsedRaw," \
      "JobID,AveRSS,MaxRSS,State,ExitCode"

parser = argparse.ArgumentParser(description="Add accounting info to a file that lacks it.")
parser.add_argument('file', help='hpcbench json file')
parser.add_argument('-j', '--jobid', help="jobid (only used if the jobid is not found in the file)", default=None)
parser.add_argument('-f', '--format', help="formatstr for sacct", default=FMT)

def add_accounting(filename, jobid=None, formatstring=FMT):
    with open(filename, "r") as cfile:
        file_json = json.load(cfile)
    try:
        file_json["version"]
    except KeyError:
        print(filename+" is not hpcbench file")
        raise IOError
    try:
        file_json["Accounting"]
    except KeyError:
        print("File "+str(filename)+" has no accounting info?")
        file_json["Accounting"] = {}
    try:
        file_json["meta"]["jobid"]
    except KeyError:
        job = jobid
        if job is None:
            raise IOError("No jobid in file, none given!")
    if file_json["Accounting"] == {}:
        sacct = hpcbench.logger.sacct.get_sacct(job, formatstring=formatstring)
        file_json["Accounting"] = sacct
        with open(filename, "w") as cfile:
            json.dump(file_json, cfile, indent=4)
        print("Wrote "+str(sacct)+ " to "+str(filename))
    else:
        print("nothing to do with "+str(file))

if __name__ == "__main__":
    args = parser.parse_args()
    add_accounting(args.file, args.jobid, args.format)
