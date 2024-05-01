#!/bin/bash
###SCHEDULER
#SBATCH --account=bdhbs05  # Run job under project <project>
#SBATCH --time=1:0:0         # Run for a max of 1 hour
#SBATCH --partition=gh    # Choose either "gh" or "ghtest" node type for grace-hopper
#SBATCH --gres=gpu:1      # Request 1 GPU, and implicitly the full 72 CPUs and 100% of the nodes memory
#SBATCH --job-name=$jobname

###PREFIX
module load cuda/12.3.2 gcc/13.2
module load openmpi
export PATH="/users/robertwelch/miniforge3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid gpulog.json &
hpcbench cpulog -p cpu.pid "'lmp'" cpulog.json &
hpcbench syslog -p sys.pid -i 1 -s /sys/class/hwmon/hwmon1/device/power1_average:totalpower:0.000001 -s /sys/class/hwmon/hwmon2/device/power1_average:gracepower:0.000001 -s /sys/class/hwmon/hwmon3/device/power1_average:cpupower:0.000001 -s /sys/class/hwmon/hwmon4/device/power1_average:iopower:0.000001 -t "'Total Energy (J)'" -t "'Total Grace Energy (J)'" -t "'Total CPU Energy (J)'" -t "'Total IO Energy (J)'" -o power.json &

###RUN
mpirun -np 72 ~/software/lammps-2Aug2023/build/lmp -sf gpu -pk gpu 1 -in benchmark.in

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
kill £(< sys.pid)
hpcbench lmplog -a power.json log.lammps run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'MD:GROMACS2024'" -e "'Machine:Grace Hopper Testbed'" -e "'comment:$comment'" meta.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json power.json thermo.json run.json slurm.json meta.json -o $benchout
rm restart.* benchmark.dcd
