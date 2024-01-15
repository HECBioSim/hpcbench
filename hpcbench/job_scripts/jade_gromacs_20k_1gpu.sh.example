#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=00:20:00
#SBATCH --job-name=gmx_1gpu_20ka
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mail-type=NONE
#SBATCH --mail-user=robert.welch@stfc.ac.uk
#SBATCH --partition=small

module load gromacs
export PATH="/jmain02/home/J2AD004/sxk40/rxw76-sxk40/anaconda3/bin:$PATH"

hpcbench infolog sysinfo.json
#hpcbench syslog -s /sys/class/hwmon/hwmon3/device/power1_average:power:1 -s /sys/class/hwmon/hwmon4/temp1_input:temp:0.001 syslog.json
hpcbench gpulog gpulog.json & gpuid=$!
hpcbench cpulog "'gmx mdrun -s benchmark.tpr'" cpulog.json & cpuid=$!

# Nvidia optimisations
export GMX_FORCE_UPDATE_DEFAULT_GPU=true
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_ENABLE_DIRECT_GPU_COMM=1

gmx mdrun -s benchmark.tpr -ntomp 10 -nb gpu -pme gpu -bonded gpu -dlb no -nstlist 300 -pin on -v -gpu_id 0

kill $gpuid
kill $cpuid

hpcbench gmxlog md.log gromacs.json
hpcbench slurmlog jade_gromacs_20k_1gpu.sh slurm.json
hpcbench extra -e "'Comment:example run'" -e "'Machine:JADE'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json gromacs.json slurm.json meta.json -o jade_gromacs_20k_1gpu.json
