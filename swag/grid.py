#!/usr/bin/env python3
"""
swag.grid — Grid file creation workflow.

Generates GLL (np4) and physics (pg2) SCRIP grid files for a target
atmosphere grid, plus the ne3000 (3km) grid files needed for topography
processing.

Usage
-----
    python -m swag.grid path/to/project.yaml
"""
import os
import textwrap
from pathlib import Path

from swag.config import swag_config
from swag.util import clr, print_line, run_cmd

# -------------------------------------------------------------------
# internal helpers


def _e3sm_env_prefix(cfg):
    """Return a bash one-liner that loads the E3SM module environment."""
    e3sm_src = cfg['paths.e3sm_src_root']
    return f'eval $({e3sm_src}/cime/CIME/Tools/get_case_env)'


def _grid_paths(cfg):
    """Return a dict of all grid file paths derived from cfg."""
    grid_name = cfg['grid.name']
    grid_root = cfg['derived.grid_root']
    homme_tool_root = cfg['paths.homme_tool_root']
    return {
        'grid_file_exodus':     f'{grid_root}/{grid_name}.g',
        'grid_file_np4_scrip':  f'{grid_root}/{grid_name}np4_scrip.nc',
        'grid_file_np4_mbda':   f'{grid_root}/{grid_name}np4_mbda.nc',
        'grid_file_pg2_scrip':  f'{grid_root}/{grid_name}pg2_scrip.nc',
        'grid_file_pg2_mbda':   f'{grid_root}/{grid_name}pg2_mbda.nc',
        'grid_file_3km_exodus': f'{grid_root}/ne3000.g',
        'grid_file_3km_scrip':  f'{grid_root}/ne3000pg1_scrip.nc',
        'grid_file_3km_mbda':   f'{grid_root}/ne3000pg1_mbda.nc',
        'grid_template_file':   f'{homme_tool_root}/{grid_name}_ne0np4_tmp1.nc',
        'nl_file':              f'{homme_tool_root}/input.grd.{grid_name}.nl',
    }


# -------------------------------------------------------------------
# public API


def create_grid(cfg):
    """
    Create GLL and physics grid files for the target atmosphere grid.

    Steps
    -----
    1. Run homme_tool to produce the np4 grid template file.
    2. Convert the template to SCRIP format via HOMME2SCRIP.py.
    3. Create MBDA-format (reduced) np4 grid file.
    4. Create PG2 exodus file via GenerateVolumetricMesh.
    5. Convert PG2 exodus to SCRIP format via ConvertMeshToSCRIP.
    6. Create MBDA-format pg2 grid file.
    7. Create ne3000 (3km) grid files if they do not already exist.

    Parameters
    ----------
    cfg : swag_config
        Loaded and validated project configuration.
    """
    # -------------------------------------------------------------------
    # resolve paths
    grid_name       = cfg['grid.name']
    homme_tool_root = cfg['paths.homme_tool_root']
    unified_bin     = cfg['paths.unified_bin']
    e3sm_src_root   = cfg['paths.e3sm_src_root']
    env_prefix      = _e3sm_env_prefix(cfg)
    p               = _grid_paths(cfg)

    # -------------------------------------------------------------------
    # clear any stale homme_tool grid template file
    if os.path.exists(p['grid_template_file']):
        run_cmd(f'rm {p["grid_template_file"]}')

    # -------------------------------------------------------------------
    # write namelist for homme_tool grid template generation
    nl_content = textwrap.dedent(f"""\
        &ctl_nl
        ne = 0
        mesh_file = "{p['grid_file_exodus']}"
        /
        &vert_nl
        /
        &analysis_nl
        output_dir = "{homme_tool_root}/"
        output_prefix="{grid_name}_"
        tool = 'grid_template_tool'
        output_timeunits=1
        output_frequency=1
        output_varnames1='area','corners','cv_lat','cv_lon'
        output_type='netcdf4p'
        io_stride = 1
        /
        """)
    Path(p['nl_file']).write_text(nl_content)

    # -------------------------------------------------------------------
    # run homme_tool to create np4 grid template
    cmd = (f'cd {homme_tool_root} && {env_prefix} &&'
           f' srun -c 32 -N $SLURM_NNODES {homme_tool_root}/src/tool/homme_tool < {p["nl_file"]}')
    run_cmd(cmd)

    if not os.path.exists(p['grid_template_file']):
        raise RuntimeError(f'homme_tool grid file creation FAILED: {p["grid_template_file"]}')
    print(f'\n  {clr.GREEN}homme_tool grid file creation SUCCESSFUL:{clr.END} {p["grid_template_file"]}')

    # -------------------------------------------------------------------
    # convert np4 template to SCRIP format
    homme2scrip = f'{e3sm_src_root}/components/homme/test/tool/python/HOMME2SCRIP.py'
    cmd = (f'{env_prefix} &&'
           f' {unified_bin}/python {homme2scrip}'
           f' --src_file {p["grid_template_file"]}'
           f' --dst_file {p["grid_file_np4_scrip"]}')
    run_cmd(cmd)

    # -------------------------------------------------------------------
    # create MBDA-format np4 grid file (reduced SCRIP, cdf5)
    cmd = (f'{unified_bin}/ncap2 -v -5 -O'
           f' -s "lon=grid_center_lon;lat=grid_center_lat;area=grid_area"'
           f' {p["grid_file_np4_scrip"]} {p["grid_file_np4_mbda"]}')
    run_cmd(cmd)
    run_cmd(f'{unified_bin}/ncrename -d grid_size,ncol {p["grid_file_np4_mbda"]}')

    if not os.path.exists(p['grid_file_np4_mbda']):
        raise RuntimeError(f'MBDA np4 grid file creation FAILED: {p["grid_file_np4_mbda"]}')
    print(f'\n  {clr.GREEN}MBDA np4 grid file creation SUCCESSFUL:{clr.END} {p["grid_file_np4_mbda"]}')

    # -------------------------------------------------------------------
    # create PG2 exodus file
    cmd = (f'{env_prefix} &&'
           f' {unified_bin}/GenerateVolumetricMesh'
           f' --in {p["grid_file_exodus"]} --out {p["grid_file_pg2_mbda"]} --np 2 --uniform')
    run_cmd(cmd)

    # convert PG2 exodus to SCRIP
    cmd = (f'{env_prefix} &&'
           f' {unified_bin}/ConvertMeshToSCRIP'
           f' --in {p["grid_file_pg2_mbda"]} --out {p["grid_file_pg2_scrip"]}')
    run_cmd(cmd)

    # create MBDA-format pg2 grid file
    cmd = (f'{unified_bin}/ncap2 -v -5 -O'
           f' -s "lon=grid_center_lon;lat=grid_center_lat;area=grid_area"'
           f' {p["grid_file_pg2_scrip"]} {p["grid_file_pg2_mbda"]}')
    run_cmd(cmd)
    run_cmd(f'{unified_bin}/ncrename -d grid_size,ncol {p["grid_file_pg2_mbda"]}')

    if not os.path.exists(p['grid_file_pg2_mbda']):
        raise RuntimeError(f'MBDA pg2 grid file creation FAILED: {p["grid_file_pg2_mbda"]}')
    print(f'\n  {clr.GREEN}MBDA pg2 grid file creation SUCCESSFUL:{clr.END} {p["grid_file_pg2_mbda"]}')

    # -------------------------------------------------------------------
    # create 3km (ne3000) grid files if they don't already exist
    if not os.path.exists(p['grid_file_3km_mbda']):
        print_line()
        print(f'\n  {clr.CYAN}Creating 3km (ne3000) grid files{clr.END}')

        cmd = (f'{env_prefix} &&'
               f' {unified_bin}/GenerateCSMesh --alt --res 3000 --file {p["grid_file_3km_exodus"]}')
        run_cmd(cmd)
        if not os.path.exists(p['grid_file_3km_exodus']):
            raise RuntimeError(f'3km exodus file creation FAILED: {p["grid_file_3km_exodus"]}')

        cmd = (f'{env_prefix} &&'
               f' {unified_bin}/ConvertMeshToSCRIP'
               f' --in {p["grid_file_3km_exodus"]} --out {p["grid_file_3km_scrip"]}')
        run_cmd(cmd)
        if not os.path.exists(p['grid_file_3km_scrip']):
            raise RuntimeError(f'3km SCRIP file creation FAILED: {p["grid_file_3km_scrip"]}')

        cmd = (f'{unified_bin}/ncap2 -v -5 -O'
               f' -s "lon=grid_center_lon;lat=grid_center_lat;area=grid_area"'
               f' {p["grid_file_3km_scrip"]} {p["grid_file_3km_mbda"]}')
        run_cmd(cmd)
    else:
        print(f'\n  {clr.CYAN}Skipping 3km grid file creation (already exists){clr.END}')


# -------------------------------------------------------------------
# entry point


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create grid files for a SWAG project.')
    parser.add_argument('project_yaml', help='Path to project.yaml')
    args = parser.parse_args()
    cfg = swag_config(args.project_yaml)
    cfg.validate()
    create_grid(cfg)
