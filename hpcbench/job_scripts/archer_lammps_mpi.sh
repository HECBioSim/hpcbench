#!/bin/bash
###SCHEDULER
#SBATCH --nodes=$nodes
#SBATCH --time=02:00:00
#SBATCH --job-name=$jobname
#SBATCH --tasks-per-node=$ntasks
#SBATCH --cpus-per-task=1
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --exclusive
#SBATCH --account=c01-bio

###PREFIX
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench cpulog "'lmp'" cpulog.json & cpuid=£!
export OMP_NUM_THREADS=1

###RUN
srun --cpu-freq=2250000 --unbuffered --cpu-bind=cores --distribution=block:block --hint=nomultithread /work/c01/c01/rwelch/software/lammps-2Aug2023/build/lmp -in benchmark.in

kill $cpuid

###POSTFIX
hpcbench lmplog log.lammps lammps.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json lammps.json slurm.json meta.json -o $benchout