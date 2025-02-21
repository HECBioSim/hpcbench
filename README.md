# hpcbench
A set of benchmarking utilities for biomolecular simulation tools.

## Features
* [X] Automatically generate and run benchmarks for different HPC systems and molecular simulation packages
* [X] Log and scrape data from running simulations
* [X] Analyse performance, scaling, system utilisation, temperature, energy conservation, etc

## Current support
* Supported simulations
    * GROMACS
    * AMBER
    * OpenMM
    * NAMD
    * LAMMPS
    * Psi4
    * Relion 5
* Supported HPC systems
    * JADE
    * ARCHER2
    * BEDE-GH
    * ISAMBARD-AI

## Getting started
* Download or clone this repo
* Run `python setup.py install`
* Run `hpcbench` in the terminal for a list of tools. Run `hpcbench <toolname>` to run that tool.
* `import hpcbench` in python for the API.

### Example: attach hpcbench loggers to an existing simulation script
The following HPC submission script has been modified to create cpu and gpu logs, as well as dump the sytem information, slurm parameters and gromacs log to json files. The call to `collate` merges all the json files together.
```bash
#!/bin/bash
#SBATCH --nodes=1 
#SBATCH --time=00:30:00
#SBATCH --job-name=benchmark
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --partition=devel

module load gromacs
conda init
hpcbench infolog sysinfo.json # log system info
hpcbench gpulog gpulog.json & gpuid=$! # log GPU utilisation
hpcbench cpulog "'gmx mdrun -s benchmark.tpr'" cpulog.json & cpuid=$! # log gromacs CPU usage

# Nvidia optimisations
export GMX_FORCE_UPDATE_DEFAULT_GPU=true 
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true

gmx mdrun -s benchmark.tpr -ntomp 10 -nb gpu -pme gpu -bonded gpu -dlb no -nstlist 300 -pin on -v -gpu_id 0

kill $gpuid
kill $cpuid

hpcbench sacct $SLURM_JOB_ID accounting.json # log slurm accounting data
hpcbench gmxlog md.log run.json # parse gromacs log file and log relevant performance data
hpcbench slurmlog $0 slurm.json # log slurm variables
hpcbench extra -e "'Software:GROMACS'" -e "'Machine:JADE2'" meta.json # any other useful info
hpcbench collate -l sysinfo.json gpulog.json cpulog.json accounting.json run.json slurm.json meta.json -o output.json # merge all json files together
```

### Example: create and submit a large set of benchmark scripts from a template
hpcbench can create many jobs at once using a job template, which is similar to the above job, but with certain variables (like the number of cpus and gpus) replaced with $-based substitutions. Specifying multiple values will lead hpcbench to generate all possible combinations of those values. Running makejobs -h will list out all the built-in templates.
```bash
hpcbench makejobs \
-s jobname=test \
-s num_gpus=gres:1,gres:2,gres:4,gres:8 \
-s partition=small \
-s benchmarkfile=benchmark.tpr \
-s comment=exmple \
-s machine=JADE \
-s benchout=output \
-e /home/rob/benchmarks/gromacs/20k-atoms/benchmark.tpr \
-t jade_gromacs_gpu.sh \
-o testgmgpu \
```

### Example: plot results
The following script searches through a directory for hpcbench output files matching the specified criteria, and plots the results. The values on the x and y axes are determined by the x and y parameters. The 'label' parameter works like the 'matching' parameters, but it will accept all values of that field, and assign each one a label on the resulting plot.

```bash
# Plot scaling across number of GPUs
hpcbench scaling \
--matching "'meta:Machine=JADE2'" \
--x "'slurm:gres'" \
--y "'run:Totals:Wall time (s)'" \
--l "'run:Totals:Atoms'" \
--d "'/path/to/hpcbench/json/files'" \
--outside \
--outfile jade_gpu_scaling.pdf

# Plot scaling with system size
hpcbench scaling \
--matching "'meta:Machine=JADE2'" \
--x "'run:Totals:Number of atoms'" \
--y "'run:Totals:ns/day'" \
--l "'slurm:program'" \
--d "'/path/to/hpcbench/json/files'" \
-- outside \
--outfile jade_nsday.pdf

# Make a stackplot
hpcbench scaling \
--matching "'meta:Machine=JADE2'" \
--matching "'slurm:gres=gpu:1'" \
--y "'run:Cycles:?:Wall time (s)'" \
--x "'run:Totals:Number of atoms'" \
--d "'/path/to/hpcbench/json/files'" \
-- outside \
--outfile atoms_stack.pdf

# Plot GPU utilisation, with one log for each system size
hpcbench logs \
--matching "'meta:Machine=JADE2'" \
--matching "'slurm:gres=gpu:1'" \
--l "'gromacs:Totals:Atoms'" \
--y "'gpulog:?:utilization.gpu [%]'" \
--x "'gpulog:?:timestamp'" \
--d "'/path/to/hpcbench/json/files'" \
--outfile atoms_usage.pdf

# Plot GPU utilisation, with one log for every number of GPUs
hpcbench logs \
--matching "'meta:Machine=JADE2'" \
--matching "'run:Totals:Number of atoms=2997924'" \
--l "'slurm:gres'" \
--y "'gpulog:?:utilization.gpu [%]'" \
--x "'gpulog:?:timestamp'" \
--d "'/path/to/hpcbench/json/files'" \
--avgy \
--outfile ~/Downloads/avg_gpu_usage.pdf
```

## Example outputs

### ns/day on JADE2
![jade_nsday](https://github.com/HECBioSim/hpcbench/assets/1513223/de74583d-fac4-46e0-bc86-af8836363243)

### Energy usage on JADE2
![jade_energy](https://github.com/HECBioSim/hpcbench/assets/1513223/4daa5208-375f-4a71-b211-25a6e5913384)

### GPU utilisation on JADE2
![jade_utilisation](https://github.com/HECBioSim/hpcbench/assets/1513223/c4e9a1d1-bc1c-4362-af62-30474bf853a1)

### GROMACS stackplot on JADE2
![stackplot](https://github.com/HECBioSim/hpcbench/assets/1513223/497284ef-c569-4df5-85b1-b5436b12c95a)

## License
AGPLv3
