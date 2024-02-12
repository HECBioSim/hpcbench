#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --job-name=$jobname
#SBATCH --gres=gpu:$num_gpus
#SBATCH --cpus-per-task=4
#SBATCH --partition=$partition

###PREFIX
set -e
export PATH="/jmain02/home/J2AD004/sxk40/rxw76-sxk40/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
#hpcbench syslog -s /sys/class/hwmon/hwmon3/device/power1_average:power:1 -s /sys/class/hwmon/hwmon4/temp1_input:temp:0.001 syslog.json
hpcbench gpulog gpulog.json & gpuid=£!
hpcbench cpulog "'benchmark.py'" cpulog.json & cpuid=£!

###RUN
python $benchmarkinfile $num_gpus

###POSTFIX
kill £gpuid
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json run.json accounting.json slurm.json meta.json -o $benchout
