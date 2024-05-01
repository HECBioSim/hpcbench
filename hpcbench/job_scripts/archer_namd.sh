#!/bin/bash
###SCHEDULER
#SBATCH --nodes=$nodes
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=$ntasks
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --account=c01-bio
#SBATCH --exclusive

# NOTE: Namd works a LOT better with mixed MPI and OMP, this is here for reference

###PREFIX
export OMP_NUM_THREADS=1
module load namd/2.14-nosmp
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench cpulog "'namd2'" cpulog.json & cpuid=£!
export SRUN_CPUS_PER_TASK=£SLURM_CPUS_PER_TASK

###RUN
srun --distribution=block:block --hint=nomultithread --unbuffered --cpu-bind=cores namd2 +setcpuaffinity benchmark.in > benchmark.log

###POSTFIX
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench namdlog benchmark.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench namdenergy benchmark.log thermo.json
hpcbench collate -l sysinfo.json thermo.json run.json accounting.json slurm.json meta.json -o $benchout
rm benchmark.coor* benchmark.dcd benchmark.pdb benchmark.psf benchmark.vel.*
