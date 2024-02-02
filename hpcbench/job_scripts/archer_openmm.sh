#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=$nthreads
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --exclusive
#SBATCH --account=c01-bio

# NOTE: OMM isn't really meant for CPUs and doesn't scale well beyond about 16 threads

###PREFIX
set -e
source /work/c01/c01/rwelch/conda.sh
export OMP_NUM_THREADS=$nthreads
OPENMM_CPU_THREADS=$nthreads
hpcbench infolog sysinfo.json	
hpcbench cpulog "'benchmark.py'" cpulog.json & cpuid=£!

###RUN
python benchmark.py

###POSTFIX
kill £cpuid
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json openmm.json slurm.json meta.json -o $benchout
