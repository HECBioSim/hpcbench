#!/bin/bash
###SCHEDULER
#SBATCH --job-name=lmp_${atoms}   # Job name
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes
#SBATCH --ntasks-per-node=1     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=1       # Allocate one gpu per MPI rank
#SBATCH --time=03:00:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001320 # Project for billing

###PREFIX
module load LUMI/24.03
module load partition/G
module load LAMMPS/2Aug2023_update3-cpeAMD-24.03-rocm

export MPICH_GPU_SUPPORT_ENABLED=1
export OMP_PROC_BIND=true

eval "£(/users/welchrob/miniforge3/bin/conda shell.bash hook)"
export PATH=/pfs/lustrep1/users/welchrob/miniforge3/bin:£PATH # why is the system python on the path first???
hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid -g amd gpulog.json &
hpcbench cpulog -p cpu.pid "'lmp'" cpulog.json &

###RUN
srun lmp -k on g 1 -sf kk -pk kokkos neigh half -in benchmark.in

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench lmplog log.lammps run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:none'" -e "'Machine:LUMI-G'" -e "'MD:LAMMPS'" -e "'Atoms:$atoms'" meta.json
truncate -s-2 thermo.json && echo "{\"thermo\":[" | cat - thermo.json > temp && mv temp thermo.json && echo ']}' >> thermo.json # hack, ugly
sleep 5
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o lmp_lumi_${atoms}atoms.json

