# hpcbench
A set of benchmarks for biomolecular simulation tools.
## Features
- [X] Log and scrape data from running simulations
- [X] Analyse performance, scaling, system utilisation, temperature, etc
- [ ] Automatically generate and run benchmarks for different HPC systems and molecular simulation packages
- [ ] Built-in tests for correctness of benchmarked systems

## Current support
* Supported simulations
    - [X] GROMACS
    - [ ] AMBER
    - [ ] OpenMM
    - [ ] NAMD
    - [ ] LAMMPS
    - [ ] QM software (eventually!)
    - [ ] AI (eventually!)
    - [ ] At least one multiscale workflow (eventually!)
* Supported HPC systems
    - [X] JADE
    - [ ] ARCHER2
    - [ ] COSMA
    - [ ] TURSA
    - [ ] ISAMBARD

## How to use
* Download or clone this repo
* Run `python setup.py install`
* Run `hpcbench` in the terminal for a list of tools. Run `hpcbench <toolname>` to run that tool.
* `import hpcbench` in python for the API.

### Example: hpcbench loggers to an existing simulation script
The following HPC submission script has been modified to create cpu and gpu logs, as well as dump the sytem information, slurm parameters and gromacs log to json files. The call to `collate` merges all the json files together.
```bash
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
```

### Example: plot results
The following script 

```bash
# Plot scaling across number of GPUs
hpcbench scaling \
--matching "'meta:Machine=JADE'" \
--x "'slurm:gres'" \
--y "'gromacs:Totals:Wall time (s)'" \
--l "'gromacs:Totals:Atoms'" \
--d "'/path/to/hpcbench/json/files'" \
--outside \
--outfile ~/Downloads/gpu_scaling.pdf

# Plot scaling with system size
hpcbench scaling \
--matching "'meta:Machine=JADE'" \
--l "'slurm:gres'" \
--y "'gromacs:Totals:Wall time (s)'" \
--x "'gromacs:Totals:Atoms'" \
--d "'/path/to/hpcbench/json/files'" \
--outfile ~/Downloads/atoms_scaling.pdf

# Make a stackplot
hpcbench scaling \
--matching "'meta:Machine=JADE'" \
--matching "'slurm:gres=gpu:1'" \
--y "'gromacs:Cycles:?:Wall time (s)'" \
--x "'gromacs:Totals:Atoms'" \
--d "'/path/to/hpcbench/json/files'" \
--outfile ~/Downloads/atoms_stack.pdf

# Plot GPU utilisation, with one log for each system size
hpcbench logs \
--matching "'meta:extra:Machine=JADE'" \
--matching "'meta:slurm:gres=gpu:1'" \
--l "'gromacs:Totals:Atoms'" \
--y "'gpulog:?:utilization.gpu [%]'" \
--x "'gpulog:?:timestamp'" \
--d "'/path/to/hpcbench/json/files'" \
--outfile ~/Downloads/atoms_usage.pdf

# Plot GPU utilisation, with one log for every number of GPUs
hpcbench logs \
--matching "'meta:extra:Machine=JADE'" \
--matching "'gromacs:Totals:Atoms=2997924'" \
--l "'slurm:gres'" \
--y "'gpulog:?:utilization.gpu [%]'" \
--x "'gpulog:?:timestamp'" \
--d "'/path/to/hpcbench/json/files'" \
--avgy \
--outfile ~/Downloads/avg_gpu_usage.pdf
```

### Example outputs
todo

### License
AGPLv3