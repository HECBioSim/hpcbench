#!/bin/bash
###SCHEDULER
#SBATCH --job-name=gmx_${atoms}   # Job name
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes
#SBATCH --ntasks-per-node=16     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=1       # Allocate one gpu per MPI rank
#SBATCH --time=0:30:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001320 # Project for billing

###PREFIX
#module load craype-accel-amd-gfx90a
#module load PrgEnv-amd
#module load rocm
#module load cray-fftw
module load LUMI/23.09
#module load EasyBuild-user
module load partition/G
module load GROMACS/2024.1-cpeAMD-23.09-VkFFT-rocm
eval "£(/users/welchrob/miniforge3/bin/conda shell.bash hook)"
export PATH=/pfs/lustrep1/users/welchrob/miniforge3/bin:£PATH # why is the system python on the path first???

hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid -g amd gpulog.json &
hpcbench cpulog -p cpu.pid "'gmx_mpi mdrun -s benchmark.tpr'" cpulog.json &
export GMX_FORCE_UPDATE_DEFAULT_GPU=true
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_ENABLE_DIRECT_GPU_COMM=1
export GMX_FORCE_GPU_AWARE_MPI=1 # ???

###RUN
gmx_mpi mdrun -s $benchfilename -ntomp 16 -nb gpu -pme gpu -bonded gpu -dlb no -nstlist 300 -pin on -v -gpu_id 0

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
hpcbench sacct £SLURM_JOB_ID accounting.json
hpcbench gmxlog md.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'Comment:none'" -e "'Machine:LUMI-G'" -e "'MD:Gromacs'" -e "'Atoms:$atoms'" meta.json
hpcbench gmxedr ener.edr thermo.json
sleep 5
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json accounting.json run.json slurm.json meta.json -o gromacs_lumi_${atoms}atoms.json
rm benchmark.tpr traj.trr
