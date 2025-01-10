#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=1:00:00
#SBATCH --job-name=relion
#SBATCH --gres=gpu:2
#SBATCH --mail-type=NONE
#SBATCH --mail-user=robert.welch@stfc.ac.uk
#SBATCH --partition=devel
#$BATCH -e XXXerrfileXXX
#$BATCH -o XXXoutfileXXX
#$BATCH -l dedicated=XXXdedicatedXXX
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --cpus-per-task=XXXthreadsXXX

source .bashrc
module load cuda
module load use.dev
module load cmake gcc openmpi
module load libpng
module load tiff
module load xz

hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid gpulog.json &
hpcbench cpulog -p cpu.pid "'relion'" cpulog.json &

export PATH=$PATH:/jmain02/home/J2AD004/sxk40/rxw76-sxk40/software/relion/build/bin

XXXcommandXXX

kill $(< gpu.pid)
kill $(< cpu.pid)
hpcbench slurmlog $0 slurm.json
hpcbench extra -e "'EM:Relion 5'" -e "'Machine:JADE'" -e "'Dataset:relion3tutorial'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json slurm.json meta.json -o benchout.json
mv benchout.json XXXnameXXXbenchout.json
