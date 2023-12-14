#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Submit jobs and parse output from slurm scheduler
"""

import subprocess
import time
import os
import glob
import argparse
import sys

parser = argparse.ArgumentParser(
    description="Submit a list of slurm scripts and report the results.")
parser.add_argument("-s", "--scripts", nargs="+", type=str,
                    help="A list of slurm scripts to submit.", required=True)
parser.add_argument("-c", "--check", type=int, default=5,
                    help="How often to check slurm. Defaults to 5.")


def update_progress(progress, bar_length=50, text="Progress"):
    """
    Print a progress bar.

    Args:
        progress - a float between 0 and 1
        bar_length: length of the progress bar (characters), an int
        text: text to show before the progress bar.
    """
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done.\r\n"
    block = int(round(bar_length*progress))
    text = "\r"+text+": [{0}] {1}% {2}".format(
        "#"*block + "-"*(bar_length-block), round(progress*100, 2), status)
    sys.stdout.write(text)
    sys.stdout.flush()


def submit(job):
    """
    Submit a job via slurm.

    Args:
        job: the bash script for the job.

    Returns:
        if the job is successful, the job ID is returned. Otherwise, an error
        is raised. If the job can't run due to some kind of limit on the
        maximum number of concurrent jobs, a ValueError is raised. If the job
        can't run for a legitemate reason, a RuntimeError with the job error
        code is raised instead.
    """
    jobreturn = subprocess.run(['sbatch', os.path.basename(job)],
                               cwd=os.path.dirname(job),
                               capture_output=True, text=True)
    if jobreturn.returncode != 0:
        if ("QOSMaxSubmitJobPerUserLimit" in jobreturn.stderr) or (
                "QOSMaxSubmitJobPerUserLimit" in jobreturn.stdout):
            raise ValueError("Max jobs reached")
        else:
            raise RuntimeError(jobreturn.stderr+"\n"+jobreturn.stdout)
    else:
        return int(jobreturn.stdout.strip().split(" ")[-1])


def get_queue():
    """
    Get a list of currently running jobs via slurm.

    Returns:
        A list of currently running jobs as a list of dictionaries. Each
        dictionary contains key-value pairs based on the columns output
        by slurm (e.g. jobid, p[artition, name, user, nodelist(reason)
    """
    user = os.environ["USER"]
    queuetxt = subprocess.run(['squeue', '-u', user],
                              capture_output=True, text=True)
    queuetxt = queuetxt.stdout
    queue = []
    lines = queuetxt.split("\n")
    header = lines.pop(0).strip().split()
    for line in lines:
        if line.strip() == "":
            break
        curr_line = line.strip().split()
        queue.append({header[i]: curr_line[i] for i in range(len(curr_line))})
    return queue


def get_job_status(script_id=None, script_path=None):
    """
    Attempt to ascertain the status of a job that has already run.

    Args:
        script_id: the slurm ID of the job, a float
        script_path: path to the job script, a string

    Returns:
        a string. If the job has a status given by sacct and an ID is supplied,
        the string is the status code. If there is no ID, or sacct can't
        determine the ID, the slurm output file is checked, and the status from
        the output file is returned. If there is no error in the slurm output,
        the string 'FINISHED' is returned.
    """
    if script_id:
        queue = get_queue()
        for job in queue:
            if job["JOBID"] == script_id:
                return job["STATUS"]
        acct = subprocess.run(['sacct', '--jobs='+str(script_id)],
                              capture_output=True, text=True)
        acct = acct.stdout.split("\n")
        header = acct.pop(0).strip().split()
        acct.pop(0)
        accts = []
        for line in acct:
            curr_line = line.strip().split()
            accts.append(
                {header[i]: curr_line[i] for i in range(len(curr_line))})
        for acct in accts:
            if acct != {}:
                if acct["JobID"] == str(script_id):
                    return acct["State"]
        if not script_path:
            raise IndexError("No job with ID "+str(script_id))
    if script_path:
        folder = os.path.dirname(script_path)
        slurm_outs = glob.glob(folder+os.path.sep+'slurm-*.out')
        if (len(slurm_outs) > 1) and script_id is None:
            raise ValueError("Multiple scripts in directory, please add ID")
        if len(slurm_outs) == 0:
            return "NONEXISTENT"
        if len(slurm_outs) == 1:
            script_name = slurm_outs[0]
        else:
            script_name = folder+os.path.sep+"slurm-"+str(script_id)+".out"
        with open(script_name, "r") as file:
            for line in file:
                if "srun" in line:
                    return line.strip()
        return "FINISHED"


def process_queue(jobs, submit_freq=1):
    """
    For a list of slurm scripts, submit them, monitor their progress, and
    report their status once they're no longer in the queue. This is useful if
    you want to submit more jobs than the HPC system will allow you to hold in
    the queue at once, or if you want to see straight away whether a batch of
    jobs has run successfully or not.

    Args:
        jobs: a list of strings, which are paths to bash scripts to be
        submitted.
        submit_freq: how many seconds to wait in between submitting jobs.
    Returns:
        Prints a report showing the status of submitted jobs and returns a
        dictionary with job scripts as keys and statuses as values.
    """
    submitted_jobs = []
    num_submitted_jobs = 0
    curr_time = 0
    num_jobs = len(jobs)
    while len(jobs) != 0:
        if curr_time % submit_freq == 0:
            num_submitted_jobs += 1
            try:
                curr_job = submit(jobs[0])
                submitted_jobs.append([curr_job, jobs[0]])
                jobs.pop(0)
            except ValueError:
                pass
            except RuntimeError as e:
                print("Error: could not process queue.")
                print("Jobs submitted: "+str(submitted_jobs))
                print("Jobs yet to submit: "+str(jobs))
                raise e
        time.sleep(1)
        curr_time += 1
        done = float(num_submitted_jobs/num_jobs)
        update_progress(done, bar_length=50, text="Submitting")
    submitted_ids = list(map(str, [i[0] for i in submitted_jobs]))
    while True:
        queue = get_queue()
        ids = [i["JOBID"] for i in queue]
        jobs_running = len(set(ids).intersection(set(submitted_ids)))
        done = 1 - (jobs_running/len(submitted_ids))
        update_progress(done, bar_length=52, text="Finished")
        if jobs_running == 0:
            break
        time.sleep(1)
    print(str(num_jobs)+" jobs to run, "+str(len(submitted_jobs))+" submitted")
    statuses = {}
    for job_id, job_path in submitted_jobs:
        status = get_job_status(job_id, job_path)
        statuses[job_path] = status
        print("Job: "+str(job_id)+" ("+str(job_path)+") status: "+status)
    return statuses


if __name__ == "__main__":
    args = parser.parse_args()
    process_queue(args.scripts)
