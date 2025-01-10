#!/bin/bash
###SCHEDULER
#SBATCH --nodes=1
#SBATCH --time=23:00:00
#SBATCH --job-name=psi
#SBATCH --cpus-per-task=128
#SBATCH --ntasks-per-node=1
#SBATCH --partition=highmem
#SBATCH --qos=highmem
#SBATCH --account=c01-bio

source /work/c01/c01/rwelch/conda.sh
conda activate psi4
export PSI_SCRATCH=/mnt/lustre/a2fs-nvme/work/c01/c01/rwelch/psiscratch/
export OMP_NUM_THREADS=128
export MKL_NUM_THREADS=128
hpcbench infolog sysinfo.json
hpcbench cpulog -p cpu.pid "'python psi4single.py'" cpulog.json &

python psi4single.py "basis" "psimem" "psimethod" 128

kill $(< cpu.pid)
hpcbench slurmlog $0 slurm.json
hpcbench extra -e "'QM:Psi4'" -e "'Machine:Archer2'" -e "'Memory:psimem'" -e "set:basis" -e "method:psimethod" meta.json
hpcbench collate -l sysinfo.json cpulog.json slurm.json meta.json -o "'bassan.json'"
exit 0
