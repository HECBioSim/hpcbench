#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --gres=gpu:1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=$partition

###PREFIX
export PATH="/jmain02/home/J2AD004/sxk40/rxw76-sxk40/.local/bin:£PATH"
module load cuda/11.1-gcc-9.1.0
module load gcc/9.1.0
hpcbench infolog sysinfo.json
#hpcbench syslog -s /sys/class/hwmon/hwmon3/device/power1_average:power:1 -s /sys/class/hwmon/hwmon4/temp1_input:temp:0.001 syslog.json
hpcbench gpulog gpulog.json & gpuid=£!
hpcbench cpulog "'lmp'" cpulog.json & cpuid=£!

###RUN
mpirun -np 4 lmp -sf gpu -pk gpu 1 -in $benchmarkinfile

kill £gpuid
kill £cpuid

###POSTFIX
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench lmplog log.lammps run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o $benchout
rm restart.* benchmark.dcd
