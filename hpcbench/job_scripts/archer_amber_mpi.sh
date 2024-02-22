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
export SLURM_CPU_FREQ_REQ=2250000
export PATH="/work/c01/c01/rwelch/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench cpulog "'pmemd.MPI'" cpulog.json & cpuid=£!
source /work/c01/c01/rwelch/software/amber22alt/amber22/amber.sh
export I_MPI_PIN_MODE=pm
export I_MPI_PIN_DOMAIN=auto

###RUN
srun --unbuffered --cpu-bind=cores --distribution=block:block --hint=nomultithread pmemd.MPI -O -i benchmark.in -p benchmark.top -c benchmark.rst -ref benchmark.rst -o benchmark.mdout -r benchmark2.rst -x benchmark.nc

###POSTFIX
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench amberlog benchmark.mdout run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench collate -l sysinfo.json run.json accounting.json slurm.json meta.json -o $benchout
