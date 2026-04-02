#!/usr/bin/env python3
"""
run_workflow.py — Project-level orchestrator for SWAG workflows.

Edit this script to describe the pipeline for your specific project.
Submit SLURM jobs or call swag module functions directly as needed.

Usage
-----
    python run_workflow.py
"""
import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from swag import swag_config
from swag.util import run_cmd, print_line

# -------------------------------------------------------------------
# load and validate config

proj_dir  = pathlib.Path(__file__).parent
cfg       = swag_config(proj_dir / 'project.yaml')
cfg.validate()

proj_root      = cfg['derived.proj_root']
logs_root      = cfg['derived.slurm_log_root']
slurm_account  = cfg['slurm.account']
slurm_constraint = cfg.get('slurm.constraint', '')

# -------------------------------------------------------------------
# choose which grids to process

grid_name_list = []
grid_name_list.append(cfg['grid.name'])
# grid_name_list.append('ne256')

# -------------------------------------------------------------------
# choose which stages to run

topo_args = ''
# topo_args += ' --stage remap'
# topo_args += ' --stage smooth'
# topo_args += ' --stage sgh'
topo_args += ' --stage all'
# topo_args += ' --force-new-3km-data'

topo_slurm_opts = '--nodes=1 --ntasks-per-node=4 --time=0:30:00'

map_args = ''
# map_args += ' --create-maps-ocn'
# map_args += ' --create-maps-lnd'

# -------------------------------------------------------------------
# submit jobs

for grid_name in grid_name_list:
    print_line()

    sbatch = f'sbatch'
    sbatch += f' --export=ALL'
    sbatch += f' --output={logs_root}/%x-%j.slurm.main.out'
    sbatch += f' --account={slurm_account}'
    if slurm_constraint:
        sbatch += f' --constraint={slurm_constraint}'
    # sbatch += f' --mail-user={cfg["slurm.mail_user"]}'
    # sbatch += f' --mail-type={cfg["slurm.mail_type"]}'

    # --- topo pipeline -----------------------------------------------
    run_cmd(
        f'{sbatch}'
        f' --job-name=gen_topo_{grid_name}'
        f' {topo_slurm_opts}'
        f' --wrap="python -m swag.topo {proj_dir}/project.yaml {topo_args}"'
    )

    # --- maps --------------------------------------------------------
    # run_cmd(
    #     f'{sbatch}'
    #     f' --job-name=gen_maps_{grid_name}'
    #     f' --time=48:00:00'
    #     f' --wrap="python -m swag.maps {proj_dir}/project.yaml {map_args}"'
    # )

    # --- domain files ------------------------------------------------
    # run_cmd(
    #     f'{sbatch}'
    #     f' --job-name=gen_domain_{grid_name}'
    #     f' --time=6:00:00'
    #     f' --wrap="python -m swag.domain {proj_dir}/project.yaml"'
    # )

print_line()
