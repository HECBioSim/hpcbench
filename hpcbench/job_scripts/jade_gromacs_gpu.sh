#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1 
#SBATCH --time=00:30:00
#SBATCH --job-name=$jobname
#SBATCH --gres=gpu:$num_gpus
#SBATCH --cpus-per-task=4
#SBATCH --partition=$partition

###PREFIX
module load gromacs
export PATH="/jmain02/home/J2AD004/sxk40/rxw76-sxk40/anaconda3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench gpulog gpulog.json & gpuid=£!
hpcbench cpulog "'gmx mdrun -s $benchmarkfile'" cpulog.json & cpuid=£!
export GMX_FORCE_UPDATE_DEFAULT_GPU=true # Nvidia optimisations
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_ENABLE_DIRECT_GPU_COMM=1

###RUN
gmx mdrun -s $benchmarkfile -ntomp 10 -nb gpu -pme gpu -bonded gpu -dlb no -nstlist 300 -pin on -v -gpu_id 0

###POSTFIX
kill £gpuid
kill £cpuid
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench gmxlog md.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:$comment'" -e "'Machine:$machine'" meta.json
hpcbench gmxedr ener.edr thermo.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o $benchout
rm benchmark.tpr traj.trr
