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
export SRUN_CPUS_PER_TASK=£SLURM_CPUS_PER_TASK
export OMP_NUM_THREADS=£SLURM_CPUS_PER_TASK
module load gromacs
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
export I_MPI_PIN_DOMAIN=omp

hpcbench infolog sysinfo.json
hpcbench cpulog "'gmx_mpi mdrun -s benchmark.tpr'" cpulog.json & cpuid=£!

###RUN
srun --cpu-freq=2250000 --unbuffered --cpu-bind=cores --distribution=block:block --hint=nomultithread gmx_mpi mdrun -s benchmark.tpr

###POSTFIX
kill £cpuid
hpcbench gmxlog md.log gromacs.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json gromacs.json slurm.json meta.json -o $benchout
