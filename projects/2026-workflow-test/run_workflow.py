#!/usr/bin/env python3
"""
run_workflow.py — Project-level orchestrator for SWAG workflows.

Edit this script to describe the pipeline for your specific project.
Submit SLURM jobs or call swag module functions directly as needed.
"""
import os, sys, pathlib
from swag import swag_config
from swag.util import run_cmd, print_line
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

#-------------------------------------------------------------------------------
# load config — shared settings (paths, slurm) read once from base config

proj_dir  = pathlib.Path(__file__).parent
cfg       = swag_config(proj_dir / 'project.yaml')

logs_root      = cfg['derived.slurm_log_root']
slurm_account  = cfg['slurm.account']
slurm_constraint = cfg.get('slurm.constraint', '')

#-------------------------------------------------------------------------------
# select which grids to process - use None to process all grids in project.yaml,
# or list specific grid names to process a subset

active_grids = None
# active_grids = ['ne30']

#-------------------------------------------------------------------------------
# submit one set of jobs per grid

for grid_cfg in cfg.iter_grids():
    if active_grids is not None and grid_cfg['grid.name'] not in active_grids:
        continue
    grid_cfg.validate()
    grid_name = grid_cfg['grid.name']
    print_line()

    sbatch = f'sbatch'
    sbatch += f' --export=ALL'
    sbatch += f' --output={logs_root}/%x-%j.slurm.main.out'
    sbatch += f' --account={slurm_account}'
    if slurm_constraint:
        sbatch += f' --constraint={slurm_constraint}'
    # sbatch += f' --mail-user={cfg["slurm.mail_user"]}'
    # sbatch += f' --mail-type={cfg["slurm.mail_type"]}'

    yaml_path = proj_dir / 'project.yaml'

    #---------------------------------------------------------------------------
    # maps

    map_args = ''
    map_args += ' --create-maps-ocn'
    map_args += ' --create-maps-lnd'

    run_cmd(f'{sbatch}'
            f' --job-name=gen_maps_{grid_name}'
            f' --time=48:00:00'
            f' --wrap="python -m swag.maps {proj_dir}/project.yaml {map_args}"'
    )

    #---------------------------------------------------------------------------
    # domain files

    run_cmd(f'{sbatch}'
            f' --job-name=gen_domain_{grid_name}'
            f' --time=6:00:00'
            f' --wrap="python -m swag.domain {proj_dir}/project.yaml"'
    )

    #---------------------------------------------------------------------------
    # topography

    topo_args = ''
    # topo_args += ' --stage remap'
    # topo_args += ' --stage smooth'
    # topo_args += ' --stage sgh'
    topo_args += ' --stage all'
    # topo_args += ' --force-new-3km-data'

    run_cmd(f'{sbatch}'
            f' --job-name=gen_topo_{grid_name}'
            f' --nodes=1 --ntasks-per-node=4 --time=0:30:00 '
            f' --wrap="python -m swag.topo {proj_dir}/project.yaml {topo_args}"'
    )

print_line()
