#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --job-name=$jobname
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=$partition

# NOTE: this does not scale to multiple GPUs OR with MPI because CUDA and MPI on jade2 are totally scuffed and AMBER on jade2 isn't compiled with OMP

###PREFIX
module load amber
export PATH="/jmain02/home/J2AD004/sxk40/rxw76-sxk40/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench gpulog gpulog.json & gpuid=£!
hpcbench cpulog "'pmemd.cuda'" cpulog.json & cpuid=£!

###RUN
pmemd.cuda -O -i $benchmarkinfile -p $benchmarktopfile -c $benchmarkrstfile -ref $benchmarkrstfile -o benchmark.mdout -r benchmark2.rst -x benchmark.nc

###POSTFIX
kill £gpuid
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench amberlog benchmark.mdout run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json accounting.json run.json slurm.json meta.json -o $benchout
