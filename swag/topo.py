#!/usr/bin/env python3
"""
swag.topo — Topography processing workflow.

Three stages:
  remap_topo   — interpolate high-res RLL source topo to the target grid
                 (np4 and pg2) and to the 3km intermediate grid, using MBDA.
  smooth_topo  — apply homme_tool smoothing to the remapped topo files.
  calc_topo_sgh — compute SGH30 and SGH subgrid-scale orography variance.

Usage
-----
    python -m swag.topo path/to/project.yaml --stage remap
    python -m swag.topo path/to/project.yaml --stage smooth
    python -m swag.topo path/to/project.yaml --stage sgh
    python -m swag.topo path/to/project.yaml --stage all
"""
import os
import textwrap
from pathlib import Path

import numpy as np
import xarray as xr

from swag.config import swag_config
from swag.util import clr, print_line, run_cmd

_GRAVITY = 9.80616

# -------------------------------------------------------------------
# internal helpers


def _e3sm_env_prefix(cfg):
    """Return a bash one-liner that loads the E3SM module environment."""
    e3sm_src = cfg['paths.e3sm_src_root']
    return f'eval $({e3sm_src}/cime/CIME/Tools/get_case_env)'


def _topo_paths(cfg):
    """Return a dict of all topo (and grid) file paths derived from cfg."""
    grid_name  = cfg['grid.name']
    grid_root  = cfg['derived.grid_root']
    topo_root  = cfg['derived.topo_root']
    timestamp  = cfg['project.timestamp']
    homme_tool_root = cfg['paths.homme_tool_root']
    return {
        # grid files (inputs, created by swag.grid)
        'grid_file_np4_mbda':    f'{grid_root}/{grid_name}np4_mbda.nc',
        'grid_file_pg2_mbda':    f'{grid_root}/{grid_name}pg2_mbda.nc',
        'grid_file_3km_mbda':    f'{grid_root}/ne3000pg1_mbda.nc',
        'grid_file_exodus':      f'{grid_root}/{grid_name}.g',
        # intermediate topo files
        'topo_file_3km':         f'{topo_root}/tmp_USGS-topo_ne3000.nc',
        'topo_file_1_np4':       f'{topo_root}/tmp_USGS-topo_{grid_name}-np4.nc',
        'topo_file_1_pg2':       f'{topo_root}/tmp_USGS-topo_{grid_name}-pg2.nc',
        'topo_file_2':           f'{topo_root}/tmp_USGS-topo_{grid_name}-np4_smoothedx6t.nc',
        'topo_file_3km_1':       f'{topo_root}/tmp_3km-topo_{grid_name}-np4.nc',
        'topo_file_3km_2':       f'{topo_root}/tmp_3km-topo_{grid_name}-np4_smoothedx6t.nc',
        'topo_file_3km_pg2':     f'{topo_root}/tmp_3km-topo_{grid_name}-pg2.nc',
        # final output topo file
        'topo_file_final':       f'{topo_root}/USGS-topo_{grid_name}-np4_smoothedx6t_{timestamp}.nc',
        # homme_tool namelist files
        'nl_file_smooth':        f'{homme_tool_root}/input.grd.{grid_name}.nl',
    }


# -------------------------------------------------------------------
# remap


def remap_topo(cfg, force_new_3km_data=False):
    """
    Remap source topography to the target np4 and pg2 grids using MBDA.

    Also remaps to the 3km (ne3000) intermediate grid if it doesn't exist
    (or if force_new_3km_data is True).

    Parameters
    ----------
    cfg : swag_config
    force_new_3km_data : bool
        If True, delete and recreate the 3km topo file even if it exists.
    """
    # -------------------------------------------------------------------
    # resolve paths
    mbda_path    = cfg['paths.mbda_path']
    unified_bin  = cfg['paths.unified_bin']
    topo_file_src = cfg['paths.topo_file_src']
    env_prefix   = _e3sm_env_prefix(cfg)
    p            = _topo_paths(cfg)

    if force_new_3km_data and os.path.exists(p['topo_file_3km']):
        run_cmd(f'rm {p["topo_file_3km"]}')

    create_new_3km = not os.path.exists(p['topo_file_3km'])

    # -------------------------------------------------------------------
    # remap source → np4
    print_line()
    print(f'\n  {clr.CYAN}Remapping source topo to np4 grid{clr.END}')
    cmd = (f'{env_prefix} &&'
           f' {mbda_path}'
           f' --target {p["grid_file_np4_mbda"]}'
           f' --source {topo_file_src}'
           f' --output {p["topo_file_1_np4"]}'
           f' --fields htopo')
    run_cmd(cmd)
    if not os.path.exists(p['topo_file_1_np4']):
        raise RuntimeError(f'Remapped np4 topo creation FAILED: {p["topo_file_1_np4"]}')

    run_cmd(f'{unified_bin}/ncrename -O -v htopo,PHIS {p["topo_file_1_np4"]} {p["topo_file_1_np4"]}')
    run_cmd(f'{unified_bin}/ncap2 -O -s "PHIS=PHIS*{_GRAVITY}" {p["topo_file_1_np4"]} {p["topo_file_1_np4"]}')

    # -------------------------------------------------------------------
    # remap source → pg2 (with squared field for variance)
    print_line()
    print(f'\n  {clr.CYAN}Remapping source topo to pg2 grid{clr.END}')
    cmd = (f'{env_prefix} &&'
           f' {mbda_path}'
           f' --target {p["grid_file_pg2_mbda"]}'
           f' --source {topo_file_src}'
           f' --output {p["topo_file_1_pg2"]}'
           f' --fields htopo --square-fields htopo')
    run_cmd(cmd)
    if not os.path.exists(p['topo_file_1_pg2']):
        raise RuntimeError(f'Remapped pg2 topo creation FAILED: {p["topo_file_1_pg2"]}')

    run_cmd(f'{unified_bin}/ncrename -O -v htopo,PHIS -v htopo_squared,PHIS_squared'
            f' {p["topo_file_1_pg2"]} {p["topo_file_1_pg2"]}')
    run_cmd(f'{unified_bin}/ncap2 -O'
            f' -s "PHIS=PHIS*{_GRAVITY}; PHIS_squared=PHIS_squared*{_GRAVITY}*{_GRAVITY}"'
            f' {p["topo_file_1_pg2"]} {p["topo_file_1_pg2"]}')

    # -------------------------------------------------------------------
    # remap source → 3km grid (skipped if file already exists)
    if create_new_3km:
        print_line()
        print(f'\n  {clr.CYAN}Creating 3km topo file with MBDA{clr.END}')
        cmd = (f'{env_prefix} &&'
               f' {mbda_path}'
               f' --target {p["grid_file_3km_mbda"]}'
               f' --source {topo_file_src}'
               f' --output {p["topo_file_3km"]}'
               f' --dof-var grid_size'
               f' --fields htopo --square-fields htopo')
        run_cmd(cmd)
        if not os.path.exists(p['topo_file_3km']):
            raise RuntimeError(f'3km topo file creation FAILED: {p["topo_file_3km"]}')

        run_cmd(f'{unified_bin}/ncap2 -v -O'
                f' -s "PHIS=htopo*{_GRAVITY}; VAR30=(htopo_squared-(htopo*htopo))*{_GRAVITY}*{_GRAVITY}; lat=lat; lon=lon"'
                f' {p["topo_file_3km"]} {p["topo_file_3km"]}')
    else:
        print(f'\n  {clr.CYAN}Skipping 3km topo file creation (already exists){clr.END}')

    # -------------------------------------------------------------------
    # remap 3km → np4 and pg2 (needed for SGH calc)
    print_line()
    print(f'\n  {clr.CYAN}Mapping 3km topo to np4 with MBDA{clr.END}')
    cmd = (f'{env_prefix} &&'
           f' {mbda_path}'
           f' --target {p["grid_file_np4_mbda"]}'
           f' --source {p["topo_file_3km"]}'
           f' --output {p["topo_file_3km_1"]}'
           f' --fields PHIS')
    run_cmd(cmd)
    if not os.path.exists(p['topo_file_3km_1']):
        raise RuntimeError(f'3km→np4 remapped topo creation FAILED: {p["topo_file_3km_1"]}')

    print_line()
    print(f'\n  {clr.CYAN}Mapping 3km topo to pg2 with MBDA{clr.END}')
    cmd = (f'{env_prefix} &&'
           f' {mbda_path}'
           f' --target {p["grid_file_pg2_mbda"]}'
           f' --source {p["topo_file_3km"]}'
           f' --output {p["topo_file_3km_pg2"]}'
           f' --fields PHIS,VAR30 --square-fields PHIS')
    run_cmd(cmd)
    if not os.path.exists(p['topo_file_3km_pg2']):
        raise RuntimeError(f'3km→pg2 remapped topo creation FAILED: {p["topo_file_3km_pg2"]}')


# -------------------------------------------------------------------
# smooth


def smooth_topo(cfg):
    """
    Apply homme_tool smoothing to the remapped topography files.

    Runs homme_tool twice:
      1. Source topo (topo_file_1_np4)  → topo_file_2
      2. 3km topo   (topo_file_3km_1)   → topo_file_3km_2

    Parameters
    ----------
    cfg : swag_config
    """
    # -------------------------------------------------------------------
    # resolve paths
    homme_tool_root = cfg['paths.homme_tool_root']
    env_prefix      = _e3sm_env_prefix(cfg)
    p               = _topo_paths(cfg)

    def _run_smooth(input_file, output_file):
        nl_content = textwrap.dedent(f"""\
            &ctl_nl
            mesh_file = "{p['grid_file_exodus']}"
            smooth_phis_p2filt = 0
            smooth_phis_numcycle = 6
            smooth_phis_nudt = 4e-16
            hypervis_scaling = 2
            se_ftype = 2
            /
            &vert_nl
            /
            &analysis_nl
            tool = 'topo_pgn_to_smoothed'
            infilenames = '{input_file}', '{output_file}'
            output_type='netcdf4p'
            /
            """)
        Path(p['nl_file_smooth']).write_text(nl_content)

        cmd = (f'cd {homme_tool_root} && {env_prefix} &&'
               f' srun -n 8 {homme_tool_root}/src/tool/homme_tool < {p["nl_file_smooth"]}')
        run_cmd(cmd)

        # homme_tool appends "1.nc" to the output prefix
        produced = f'{output_file}1.nc'
        if not os.path.exists(produced):
            raise RuntimeError(f'homme_tool smoothing FAILED: {produced}')
        run_cmd(f'mv {produced} {output_file}')
        print(f'\n  {clr.GREEN}Smoothing SUCCESSFUL:{clr.END} {output_file}')

    # -------------------------------------------------------------------
    # smooth source topo
    print_line()
    print(f'\n  {clr.CYAN}Smoothing source topo (np4){clr.END}')
    _run_smooth(p['topo_file_1_np4'], p['topo_file_2'])

    # -------------------------------------------------------------------
    # smooth 3km topo
    print_line()
    print(f'\n  {clr.CYAN}Smoothing 3km topo (np4){clr.END}')
    _run_smooth(p['topo_file_3km_1'], p['topo_file_3km_2'])


# -------------------------------------------------------------------
# SGH computation (pure Python / xarray)


def _compute_variance(phis, phis_smoothed, phis_squared):
    """Compute variance: E[(X - X_smooth)^2] = X_sq + X_smooth^2 - 2*X_smooth*X."""
    return phis_squared + (phis_smoothed ** 2) - (2 * phis_smoothed * phis)


def calc_topo_sgh(cfg):
    """
    Compute SGH30 and SGH subgrid-scale orography variance and write
    the final topography output file.

    SGH30  = sqrt(min(VAR2, VAR30)) / g
    SGH    = sqrt(VAR_3km) / g

    Parameters
    ----------
    cfg : swag_config
    """
    p = _topo_paths(cfg)

    # -------------------------------------------------------------------
    # load input datasets
    print_line()
    print(f'\n  {clr.CYAN}Computing SGH30{clr.END}')

    ds_3km    = xr.open_dataset(p['topo_file_3km_pg2'])
    ds_1_pg2  = xr.open_dataset(p['topo_file_1_pg2'])
    ds_2      = xr.open_dataset(p['topo_file_2'])
    ds_3km_2  = xr.open_dataset(p['topo_file_3km_2'])
    ds_1_np4  = xr.open_dataset(p['topo_file_1_np4'])

    # -------------------------------------------------------------------
    # SGH30
    phis_smoothed = ds_2['PHIS']
    phis          = ds_1_pg2['PHIS']
    phis_squared  = ds_1_pg2['PHIS_squared']
    var2          = phis_squared - phis * phis
    var30         = ds_3km['VAR30']
    var_min       = xr.where(var30 < var2, var30, var2)
    var_min       = xr.where(var_min > 0, var_min, 0)
    sgh30         = np.sqrt(var_min) / _GRAVITY

    ds_out = xr.Dataset({'SGH30': sgh30})
    ds_out['SGH30'].attrs['units']     = 'm'
    ds_out['SGH30'].attrs['long_name'] = 'standard deviation of source elevation from 3km cube'

    # -------------------------------------------------------------------
    # SGH
    print(f'\n  {clr.CYAN}Computing SGH{clr.END}')

    phis_3km         = ds_3km['PHIS']
    phis_3km_squared = ds_3km['PHIS_squared']
    var_3km          = phis_3km_squared - phis_3km * phis_3km
    var_3km          = xr.where(var_3km > 0, var_3km, 0)
    sgh              = np.sqrt(var_3km) / _GRAVITY

    ds_out['SGH'] = sgh
    ds_out['SGH'].attrs['units']     = 'm'
    ds_out['SGH'].attrs['long_name'] = 'standard deviation of 3km cubed-sphere elevation'

    # SGH_dycore (debug: use homme_tool smoothed phi)
    phis_3km_smooth  = ds_3km_2['PHIS']
    var_3km_d        = _compute_variance(phis_3km, phis_3km_smooth, phis_3km_squared)
    var_3km_d        = xr.where(var_3km_d > 0, var_3km_d, 0)
    sgh_dycore       = np.sqrt(var_3km_d) / _GRAVITY

    ds_out['SGH_dycore'] = sgh_dycore
    ds_out['SGH_dycore'].attrs['units']     = 'm'
    ds_out['SGH_dycore'].attrs['long_name'] = 'standard deviation of 3km cubed-sphere elevation'

    # -------------------------------------------------------------------
    # add coordinate and smoothed PHIS fields
    print(f'\n  {clr.CYAN}Adding coordinate and smoothed PHIS fields{clr.END}')

    if 'lon' in ds_1_pg2 and 'lat' in ds_1_pg2:
        ds_out['lon'] = ds_1_pg2['lon']
        ds_out['lat'] = ds_1_pg2['lat']

    for coord in ('lon', 'lat'):
        if coord in ds_1_np4:
            var = ds_1_np4[coord].reset_coords(drop=True) if coord in ds_1_np4.coords else ds_1_np4[coord]
            if 'ncol' in var.dims:
                var = var.rename({'ncol': 'ncol_d'})
            ds_out[f'{coord}_d'] = var

    if 'PHIS' in ds_2:
        ds_out['PHIS'] = ds_2['PHIS']
    if 'PHIS_d' in ds_2:
        ds_out['PHIS_d'] = ds_2['PHIS_d']

    # -------------------------------------------------------------------
    # close inputs and write output
    for ds in (ds_3km, ds_1_pg2, ds_2, ds_3km_2, ds_1_np4):
        ds.close()

    print(f'\n  {clr.CYAN}Writing output: {p["topo_file_final"]}{clr.END}')
    encoding = {var: {'zlib': True, 'complevel': 1} for var in ds_out.data_vars}
    ds_out.to_netcdf(p['topo_file_final'], encoding=encoding)
    ds_out.close()

    print(f'\n  {clr.GREEN}SGH calculation SUCCESSFUL:{clr.END} {p["topo_file_final"]}')
    print('\n  The following temporary files can be deleted:')
    topo_root = cfg['derived.topo_root']
    for f in Path(topo_root).glob('tmp_*'):
        print(f'    {f}')


# -------------------------------------------------------------------
# entry point


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run a SWAG topography stage.')
    parser.add_argument('project_yaml', help='Path to project.yaml')
    parser.add_argument('--stage', choices=['remap', 'smooth', 'sgh', 'all'],
                        default='all', help='Which stage to run (default: all)')
    parser.add_argument('--force-new-3km-data', action='store_true',
                        help='Force recreation of the 3km topo file')
    parser.add_argument('--grid-name', default=None,
                        help='Grid name to process (selects from grids: list; default: base grid:)')
    args = parser.parse_args()

    cfg = swag_config(args.project_yaml)
    if args.grid_name:
        cfg = cfg.for_grid(args.grid_name)
    cfg.validate()

    if args.stage in ('remap', 'all'):
        remap_topo(cfg, force_new_3km_data=args.force_new_3km_data)
    if args.stage in ('smooth', 'all'):
        smooth_topo(cfg)
    if args.stage in ('sgh', 'all'):
        calc_topo_sgh(cfg)
