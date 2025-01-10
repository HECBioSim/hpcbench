#!/bin/bash
###SCHEDULER
#SBATCH --job-name=amber_${atoms}   # Job name
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes
#SBATCH --ntasks-per-node=16     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=1       # Allocate one gpu per MPI rank
#SBATCH --time=2:50:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001320 # Project for billing

###PREFIX
module load LUMI/24.03
module load partition/G
module load Amber/24.0-cpeGNU-24.03-AmberTools-24.0-rocm
eval "£(/users/welchrob/miniforge3/bin/conda shell.bash hook)"
export PATH=/pfs/lustrep1/users/welchrob/miniforge3/bin:£PATH # why is the system python on the path first???

hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid -g amd gpulog.json &
hpcbench cpulog -p cpu.pid "'pmemd.hip'" cpulog.json &

###RUN
pmemd.hip -O -i $benchmarkinfile -p $benchmarktopfile -c $benchmarkrstfile -ref $benchmarkrstfile -o benchmark.mdout -r benchmark2.rst -x benchmark.nc

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench amberlog benchmark.mdout run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:none'" -e "'Machine:LUMI-G'" -e "'MD:AMBER'" -e "'Atoms:$atoms'" meta.json
hpcbench amberenergy benchmark.mdout thermo.json
sleep 5
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o amber_lumi_${atoms}atoms.json

