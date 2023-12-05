~/anaconda3/bin/python scaling.py \
--matching "meta:extra:Machine=JADE" \
--x "meta:slurm:gres" \
--y "gromacs:Totals:Wall time (s)" \
--l "gromacs:Totals:Atoms" \
--d "/home/rob/Downloads/testdata2/test2" \
--outside \
--outfile ~/Downloads/gpu_scaling.pdf

~/anaconda3/bin/python scaling.py \
--matching "meta:extra:Machine=JADE" \
--l "meta:slurm:gres" \
--y "gromacs:Totals:Wall time (s)" \
--x "gromacs:Totals:Atoms" \
--d "/home/rob/Downloads/testdata2/test2" \
--outfile ~/Downloads/atoms_scaling.pdf

~/anaconda3/bin/python scaling.py \
--matching "meta:extra:Machine=JADE" \
--matching "meta:slurm:gres=gpu:1" \
--y "gromacs:Cycles:?:Wall time (s)" \
--x "gromacs:Totals:Atoms" \
--d "/home/rob/Downloads/testdata2/test2" \
--outfile ~/Downloads/atoms_stack.pdf

~/anaconda3/bin/python logs.py \
--matching "meta:extra:Machine=JADE" \
--matching "meta:slurm:gres=gpu:1" \
--l "gromacs:Totals:Atoms" \
--y "gpulog:?:utilization.gpu [%]" \
--x "gpulog:?:timestamp" \
--d "/home/rob/Downloads/testdata2/test2" \
--outfile ~/Downloads/atoms_usage.pdf

~/anaconda3/bin/python logs.py \
--matching "meta:extra:Machine=JADE" \
--matching "gromacs:Totals:Atoms=2997924" \
--l "meta:slurm:gres" \
--y "gpulog:?:utilization.gpu [%]" \
--x "gpulog:?:timestamp" \
--d "/home/rob/Downloads/testdata2/test2" \
--avgy \
--outfile ~/Downloads/avg_gpu_usage.pdf

# note: in the newest version of the log maker, slurm is now in its own entry, and not in meta, and meta is now the contetns of what used to be meta:extra.
