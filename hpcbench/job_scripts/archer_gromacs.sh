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

###PREFIX
export OMP_NUM_THREADS=1
export SRUN_CPUS_PER_TASK=£SLURM_CPUS_PER_TASK
module load gromacs
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"

hpcbench infolog sysinfo.json
hpcbench cpulog "'gmx_mpi mdrun -s benchmark.tpr'" cpulog.json & cpuid=£!

###RUN
srun --cpu-freq=2250000 --unbuffered --cpu-bind=cores --distribution=block:block --hint=nomultithread gmx_mpi mdrun -s benchmark.tpr

###POSTFIX
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench gmxlog md.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench gmxedr ener.edr thermo.json
hpcbench collate -l sysinfo.json thermo.json run.json accounting.json slurm.json meta.json -o $benchout
rm benchmark.tpr traj.trr
