#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --job-name=psi4
#SBATCH --cpus-per-task=128
#SBATCH --ntasks-per-node=1
#SBATCH --partition=highmem
#SBATCH --qos=highmem
#SBATCH --account=c01-bio

###PREFIX
source /work/c01/c01/rwelch/conda.sh
conda activate psi4
export PSI_SCRATCH=/mnt/lustre/a2fs-nvme/work/c01/c01/rwelch/psiscratch/
export OMP_NUM_THREADS=128
hpcbench infolog sysinfo.json
hpcbench cpulog -p cpu.pid "'python psi4single.py'" cpulog.json &

###RUN
python psi4single.py "basis"

###POSTFIX
kill £(< cpu.pid)
hpcbench slurmlog "'bassan.benchmark.sh'" slurm.json
hpcbench extra -e "'QM:Psi4'" -e "'Machine:Archer2'" -e "'comment:none'" meta.json
hpcbench collate -l sysinfo.json cpulog.json slurm.json meta.json -o "'bassan.json'"
exit 0
