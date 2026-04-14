#!/usr/bin/env python3
"""
taos.topo — Topography processing workflow.

Four stages:
  grid         — create np4/pg2/3km SCRIP and MBDA grid files (calls taos.grid).
  remap_topo   — interpolate high-res RLL source topo to the target grid
                 (np4 and pg2) and to the 3km intermediate grid, using MBDA.
  smooth_topo  — apply homme_tool smoothing to the remapped topo files.
  calc_topo_sgh — compute SGH30 and SGH subgrid-scale orography variance.

Usage
-----
    python -m taos.topo path/to/project.yaml --stage grid
    python -m taos.topo path/to/project.yaml --stage remap
    python -m taos.topo path/to/project.yaml --stage smooth
    python -m taos.topo path/to/project.yaml --stage sgh
    python -m taos.topo path/to/project.yaml --stage all
"""
import os
from pathlib import Path

import numpy as np
import xarray as xr

from taos.config import taos_config
from taos.grid import create_grid
from taos import sem
from taos.util import clr, print_line, run_cmd, timer

_GRAVITY = 9.80616

# -------------------------------------------------------------------
# internal helpers


def _e3sm_env_prefix(cfg):
    """Return a bash one-liner that loads the E3SM module environment."""
    e3sm_src = cfg['paths.e3sm_src_root']
    return f'eval $({e3sm_src}/cime/CIME/Tools/get_case_env)'


def _topo_paths(cfg):
    """Return a dict of all topo (and grid) file paths derived from cfg."""
    grid_name = cfg['grid.name']
    grid_root = cfg['derived.grid_root']
    topo_root = cfg['derived.topo_root']
    timestamp = cfg['project.timestamp']
    np4_name  = cfg.get('grid.name_np4', grid_name + 'np4')
    pg2_name  = cfg.get('grid.name_pg2', grid_name + 'pg2')
    return {
        # grid files (inputs, created by taos.grid)
        'grid_file_np4_mbda': f'{grid_root}/{np4_name}_mbda.nc',
        'grid_file_pg2_mbda': f'{grid_root}/{pg2_name}_mbda.nc',
        'grid_file_3km_mbda': f'{grid_root}/ne3000pg1_mbda.nc',
        'grid_file_exodus':   f'{grid_root}/{grid_name}.g',
        # intermediate topo files
        'topo_file_3km':      f'{topo_root}/tmp_USGS-topo_ne3000.nc',
        'topo_file_1_np4':    f'{topo_root}/tmp_USGS-topo_{grid_name}-np4.nc',
        'topo_file_1_pg2':    f'{topo_root}/tmp_USGS-topo_{grid_name}-pg2.nc',
        'topo_file_2':        f'{topo_root}/tmp_USGS-topo_{grid_name}-np4_smoothedx6t.nc',
        'topo_file_3km_1':    f'{topo_root}/tmp_3km-topo_{grid_name}-np4.nc',
        'topo_file_3km_2':    f'{topo_root}/tmp_3km-topo_{grid_name}-np4_smoothedx6t.nc',
        'topo_file_3km_pg2':  f'{topo_root}/tmp_3km-topo_{grid_name}-pg2.nc',
        # final output topo file
        'topo_file_final':    f'{topo_root}/USGS-topo_{grid_name}-np4_smoothedx6t_{timestamp}.nc',
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
    cfg : taos_config
    force_new_3km_data : bool
        If True, delete and recreate the 3km topo file even if it exists.
    """
    with timer.time('remap_topo'):
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
        with timer.time('remap: MBDA source → np4'):
            run_cmd(cmd)
        if not os.path.exists(p['topo_file_1_np4']):
            raise RuntimeError(f'Remapped np4 topo creation FAILED: {p["topo_file_1_np4"]}')

        with timer.time('remap: ncrename np4 htopo→PHIS'):
            run_cmd(f'{unified_bin}/ncrename -O -v htopo,PHIS {p["topo_file_1_np4"]} {p["topo_file_1_np4"]}')
        with timer.time('remap: ncap2 np4 PHIS*gravity'):
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
        with timer.time('remap: MBDA source → pg2'):
            run_cmd(cmd)
        if not os.path.exists(p['topo_file_1_pg2']):
            raise RuntimeError(f'Remapped pg2 topo creation FAILED: {p["topo_file_1_pg2"]}')

        with timer.time('remap: ncrename pg2 htopo→PHIS'):
            run_cmd(f'{unified_bin}/ncrename -O -v htopo,PHIS -v htopo_squared,PHIS_squared'
                    f' {p["topo_file_1_pg2"]} {p["topo_file_1_pg2"]}')
        with timer.time('remap: ncap2 pg2 PHIS*gravity'):
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
            with timer.time('remap: MBDA source → 3km'):
                run_cmd(cmd)
            if not os.path.exists(p['topo_file_3km']):
                raise RuntimeError(f'3km topo file creation FAILED: {p["topo_file_3km"]}')

            with timer.time('remap: ncap2 3km derive PHIS/VAR30'):
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
        with timer.time('remap: MBDA 3km → np4'):
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
        with timer.time('remap: MBDA 3km → pg2'):
            run_cmd(cmd)
        if not os.path.exists(p['topo_file_3km_pg2']):
            raise RuntimeError(f'3km→pg2 remapped topo creation FAILED: {p["topo_file_3km_pg2"]}')


# -------------------------------------------------------------------
# smooth


def smooth_topo(cfg):
    """
    Apply Python SEM tensor hyperviscosity smoothing to the remapped topo files.

    Replaces homme_tool topo_pgn_to_smoothed (hypervis_scaling=2, numcycle=6,
    nudt=4e-16).  Reads the Exodus mesh once, then smooths:
      1. Source topo (topo_file_1_np4)  → topo_file_2
      2. 3km topo   (topo_file_3km_1)   → topo_file_3km_2

    Parameters
    ----------
    cfg : taos_config
    """
    with timer.time('smooth_topo'):
        p = _topo_paths(cfg)

        # -------------------------------------------------------------------
        # precompute SEM geometry from the Exodus mesh (shared by both runs)
        print_line()
        print(f'\n  {clr.CYAN}Loading Exodus mesh for SEM geometry{clr.END}')
        with timer.time('smooth: load Exodus geometry'):
            coords, connect = sem.read_exodus(p['grid_file_exodus'])
            g_det, _        = sem.element_metric(coords, connect)
            _, inverse_idx, _ = sem.unique_gll_nodes(coords, connect)
            ncol = int(np.max(inverse_idx)) + 1

        def _smooth_file(input_path, output_path, label):
            with timer.time(label):
                ds_in      = xr.open_dataset(input_path)
                phis       = ds_in['PHIS'].values.flatten()
                ds_in.close()

                phis_smooth = sem.smooth_phis(phis, g_det, inverse_idx, ncol)

                ds_out = xr.Dataset({
                    'PHIS':   xr.DataArray(phis_smooth, dims=['ncol'],
                                           attrs={'units': 'm2 s-2'}),
                    'PHIS_d': xr.DataArray(phis_smooth, dims=['ncol'],
                                           attrs={'units': 'm2 s-2'}),
                })
                ds_out.to_netcdf(output_path)
            print(f'\n  {clr.GREEN}Smoothing SUCCESSFUL:{clr.END} {output_path}')

        # -------------------------------------------------------------------
        # smooth source topo
        print_line()
        print(f'\n  {clr.CYAN}Smoothing source topo (np4){clr.END}')
        _smooth_file(p['topo_file_1_np4'], p['topo_file_2'], 'smooth: Python source np4')

        # -------------------------------------------------------------------
        # smooth 3km topo
        print_line()
        print(f'\n  {clr.CYAN}Smoothing 3km topo (np4){clr.END}')
        _smooth_file(p['topo_file_3km_1'], p['topo_file_3km_2'], 'smooth: Python 3km np4')


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
    cfg : taos_config
    """
    with timer.time('calc_topo_sgh'):
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
        # SGH30, SGH, SGH_dycore computation
        with timer.time('sgh: compute SGH30 + SGH + SGH_dycore'):
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
        with timer.time('sgh: write output file'):
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
    parser = argparse.ArgumentParser(description='Run a TAOS topography stage.')
    parser.add_argument('project_yaml', help='Path to project.yaml')
    parser.add_argument('--stage', choices=['grid', 'remap', 'smooth', 'sgh', 'all'],
                        default='all', help='Which stage to run (default: all)')
    parser.add_argument('--force-new-3km-data', action='store_true',
                        help='Force recreation of the 3km topo file')
    parser.add_argument('--grid-name', default=None,
                        help='Grid name to process (selects from grids: list; default: base grid:)')
    args = parser.parse_args()

    cfg = taos_config(args.project_yaml)
    if args.grid_name:
        cfg = cfg.for_grid(args.grid_name)
    cfg.validate()

    timer.start_total()
    if args.stage in ('grid', 'all'):
        create_grid(cfg)
    if args.stage in ('remap', 'all'):
        remap_topo(cfg, force_new_3km_data=args.force_new_3km_data)
    if args.stage in ('smooth', 'all'):
        smooth_topo(cfg)
    if args.stage in ('sgh', 'all'):
        calc_topo_sgh(cfg)
    timer.summary()
