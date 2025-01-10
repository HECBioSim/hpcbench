#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=1:00:00
#SBATCH --job-name=relion
#$BATCH -e XXXerrfileXXX
#$BATCH -o XXXoutfileXXX
#$BATCH -l dedicated=XXXdedicatedXXX
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --cpus-per-task=XXXthreadsXXX
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --account=c01-bio
#SBATCH --exclusive

module use --append /work/c01/c01/rwelch/software/modules
module load PrgEnv-gnu cray-fftw cray-mpich/8.1.23 cray-mpixlate
#module load ctffind4
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/c01/c01/rwelch/anaconda3/envs/wxwidgets/lib
export TORCH_HOME=/work/c01/c01/rwelch/torch/torch/hub/

__conda_setup="$('/work/c01/c01/rwelch/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/work/c01/c01/rwelch/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/work/c01/c01/rwelch/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/work/c01/c01/rwelch/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup

hpcbench infolog sysinfo.json
hpcbench cpulog -p cpu.pid "'relion'" cpulog.json &

# srun --cpu-freq=2250000 --unbuffered --cpu-bind=cores --distribution=block:block
export PATH=$PATH:/work/c01/c01/rwelch/software/relion/build/bin
export PATH=$PATH:/work/c01/c01/rwelch/software/modules/ctffind/bin
#which ctffind

XXXcommandXXX

kill $(< cpu.pid)
hpcbench slurmlog $0 slurm.json
hpcbench extra -e "'EM:Relion 5'" -e "'Machine:ARCHER2'" -e "'Dataset:relion3tutorial'" meta.json
hpcbench collate -l sysinfo.json cpulog.json slurm.json meta.json -o benchout.json
mv benchout.json XXXnameXXXbenchout.json
