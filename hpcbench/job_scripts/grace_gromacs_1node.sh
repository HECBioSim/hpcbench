#!/bin/bash
###SCHEDULER
#SBATCH --account=bdhbs05  # Run job under project <project>
#SBATCH --time=1:0:0         # Run for a max of 1 hour
#SBATCH --partition=gh    # Choose either "gh" or "ghtest" node type for grace-hopper
#SBATCH --gres=gpu:1      # Request 1 GPU, and implicitly the full 72 CPUs and 100% of the nodes memory
#SBATCH --job-name=$jobname

###PREFIX
module load cuda/12.3.2
export PATH="/users/robertwelch/miniforge3/bin:£PATH"
hpcbench infolog sysinfo.json
hpcbench gpulog -p gpu.pid gpulog.json &
hpcbench cpulog -p cpu.pid "'gmx mdrun -s benchmark.tpr'" cpulog.json &
export GMX_FORCE_UPDATE_DEFAULT_GPU=true # Nvidia optimisations
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_ENABLE_DIRECT_GPU_COMM=1
hpcbench syslog -p sys.pid -i 1 -s /sys/class/hwmon/hwmon1/device/power1_average:totalpower:0.000001 -s /sys/class/hwmon/hwmon2/device/power1_average:gracepower:0.000001 -s /sys/class/hwmon/hwmon3/device/power1_average:cpupower:0.000001 -s /sys/class/hwmon/hwmon4/device/power1_average:iopower:0.000001 -t "'Total Energy (J)'" -t "'Total Grace Energy (J)'" -t "'Total CPU Energy (J)'" -t "'Total IO Energy (J)'" -o power.json &

###RUN
~/software/gromacs/bin/gmx mdrun -s benchmark.tpr -ntomp 72 -nb gpu -pme gpu -bonded gpu -dlb no -nstlist 300 -pin on -v -gpu_id 0

###POSTFIX
kill £(< gpu.pid)
kill £(< cpu.pid)
kill £(< sys.pid)
hpcbench gmxlog -a power.json md.log run.json
hpcbench slurmlog £0 slurm.json
hpcbench extra -e "'MD:GROMACS2024'" -e "'Machine:Grace Hopper Testbed'" -e "'comment:$comment'" meta.json
hpcbench gmxedr ener.edr thermo.json
hpcbench collate -l sysinfo.json gpulog.json cpulog.json thermo.json power.json run.json slurm.json meta.json -o $benchout
rm benchmark.tpr traj.trr
