#!/bin/bash
###SCHEDULER
#SBATCH --job-name=namd_${atoms}   # Job name
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes
#SBATCH --ntasks-per-node=16     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=1       # Allocate one gpu per MPI rank
#SBATCH --time=2:50:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001320 # Project for billing

###PREFIX
module load LUMI/24.03
module load partition/G
module load NAMD/3.0-cpeGNU-24.03-rocm-gpu-resident
eval "£(/users/welchrob/miniforge3/bin/conda shell.bash hook)"
export PATH=/pfs/lustrep1/users/welchrob/miniforge3/bin:£PATH # why is the system python on the path first???
num_gpus=0
gpus=(£(seq -s , 0 £num_gpus  ))
hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid -g amd gpulog.json &
hpcbench cpulog -p cpu.pid "'namd3'" cpulog.json &

###RUN
namd3 +idlepoll +p 16 +devices £gpus $benchmarkinfile | tee namdlog.txt

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench namdlog namdlog.txt run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:none'" -e "'Machine:LUMI-G'" -e "'MD:NAMD'" -e "'Atoms:$atoms'" meta.json
hpcbench namdenergy namdlog.txt thermo.json
sleep 5
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o namd_lumi_${atoms}atoms.json

