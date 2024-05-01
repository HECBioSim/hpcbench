#!/bin/bash
###SCHEDULER
#SBATCH --nodes=$nodes
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --tasks-per-node=$ntasks
#SBATCH --cpus-per-task=$nthreads
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --exclusive
#SBATCH --account=c01-bio

###PREFIX
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench cpulog "'lmp'" cpulog.json & cpuid=£!
export OMP_NUM_THREADS=£SLURM_CPUS_PER_TASK
export I_MPI_PIN_DOMAIN=omp
export SRUN_CPUS_PER_TASK=£SLURM_CPUS_PER_TASK

###RUN
srun --cpu-freq=2250000 --unbuffered --cpu-bind=cores --hint=nomultithread --distribution=block:block /work/c01/c01/rwelch/software/lammps-2Aug2023/build/lmp -sf omp -pk omp $nthreads -in benchmark.in

kill £cpuid

###POSTFIX
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench lmplog log.lammps run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o $benchout
rm restart.* benchmark.dcd
