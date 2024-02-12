#!/bin/bash
###SCHEDULER
#SBATCH --nodes=$nodes
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --cpus-per-task=$nthreads
#SBATCH --ntasks-per-node=$ntasks
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --account=c01-bio
#SBATCH --exclusive

###PREFIX
export OMP_NUM_THREADS=$nthreads
#export SRUN_CPUS_PER_TASK=£SLURM_CPUS_PER_TASK # this setting is usually necessary to prevent oversubscribing but it causes namd to crash
export OMP_NUM_THREADS=£SLURM_CPUS_PER_TASK
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
export I_MPI_PIN_DOMAIN=omp
export PPN=£((£SLURM_CPUS_PER_TASK-1))
export OMP_PLACES=cores
module load namd
hpcbench infolog sysinfo.json
hpcbench cpulog "'namd2'" cpulog.json & cpuid=£!

###RUN
srun --cpu-freq=2250000 --distribution=block:block --unbuffered --cpu-bind=cores namd2 +setcpuaffinity +ppn £PPN benchmark.in > benchmark.log

###POSTFIX
kill $cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench namdlog md.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json run.json accounting.json slurm.json meta.json -o $benchout

