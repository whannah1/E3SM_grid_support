#!/usr/bin/env python3
#-------------------------------------------------------------------------------
"""
Compute SGH30 and SGH (subgrid-scale orography standard deviation)
for atmospheric model topography files.

SGH30 - Combined variance from source data and 3km intermediate grid
SGH   - Variance from 3km grid to target grid only

SGH30 Procedure:
    VAR30:  variance between SRC and cube3000, computed during remap step
    VAR2:   variance between SRC and target (computed below)
    SGH30 = sqrt(min(VAR2,VAR30)

SGH Procedure:
    H_3 = topo on cube3000
    H3_pg2   =   H_3 mapped to target grid       file:  $topo_file_3km_pg2
    H3SQ_pg2 =  (H_3)^2 mapped to target grid    file:  $topo_file_3km_pg2
    H3_d_pg2 =   H_3 after dycore smoothing      file:  $topo_file_3km_2.nc
    VAR = MPDA((H_3-H3_d_pg2)^2) = H3SQ_pg2 + H3_d_pg2^2  - 2 * H3_d_pg2 * H3_pg2        
    SGH = sqrt(VAR)

Notes:
  - For target grid regions with resolution << 3km, VAR2 will always be less than VAR30
    and we could skip the min() operation.
  - For target grid regions with resolution >> 3km, we need to reduce the variance by using VAR2.
  - For regions with resolution >= source grid, VAR2=0

"""
#-------------------------------------------------------------------------------
import argparse
import numpy as np
import xarray as xr
from pathlib import Path

gravity = 9.80616  # gravitational acceleration
verbose_indent = ' '*2

#-------------------------------------------------------------------------------
def compute_variance(phis, phis_smoothed, phis_squared):
    """
    Compute variance: VAR = PHIS_squared + PHIS_smoothed^2 - 2*PHIS_smoothed*PHIS
    This is mathematically equivalent to E[(X - X_smooth)^2]
    """
    return phis_squared + (phis_smoothed ** 2) - (2 * phis_smoothed * phis)
#-------------------------------------------------------------------------------
def compute_sgh30(topo_3km_pg2_file, topo_1_pg2_file, topo_2_file, output_file):
    """
    SGH30 is the topography variance between the source data and cube3000
    sqrt(min(VAR2, VAR30)) / g
    Parameters:
    -----------
    topo_3km_pg2_file : str  File with VAR30 (variance on cube3000 mapped to target grid)
    topo_1_pg2_file   : str  File with PHIS and PHIS_squared on target grid
    topo_2_file       : str  File with smoothed PHIS on target grid
    output_file       : str  Output file for SGH30
    """
    global gravity
    
    # Load necessary variables from each file
    ds_3km = xr.open_dataset(topo_3km_pg2_file)
    ds_1 = xr.open_dataset(topo_1_pg2_file)
    ds_2 = xr.open_dataset(topo_2_file)
    
    # Get smoothed PHIS from topo_file_2
    phis_smoothed = ds_2['PHIS']
    
    # Get PHIS and PHIS_squared from topo_file_1_pg2
    phis = ds_1['PHIS']
    phis_squared = ds_1['PHIS_squared']
    
    # Compute VAR2: variance between source and smoothed on target grid
    var2 = compute_variance(phis, phis_smoothed, phis_squared)
    
    # Get VAR30 from 3km file
    var30 = ds_3km['VAR30']
    
    # SGH30 = sqrt(min(VAR2, VAR30)) / g
    # NCO uses << for min and >> for max
    var_min = xr.where(var30 < var2, var30, var2)
    var_min = xr.where(var_min > 0, var_min, 0)  # Ensure non-negative before sqrt
    sgh30 = np.sqrt(var_min) / gravity
    
    # Create output dataset with SGH30
    ds_out = xr.Dataset({'SGH30': sgh30})
    
    # Close input datasets
    ds_3km.close()
    ds_1.close()
    ds_2.close()
    
    return ds_out
#-------------------------------------------------------------------------------
def compute_sgh(topo_3km_pg2_file, topo_3km_2_file):
    """
    SGH is the variance from cube3000 to target grid after dycore smoothing

    Parameters:
    -----------
    topo_3km_pg2_file   : str   File with PHIS and PHIS_squared from cube3000 mapped to target
    topo_3km_2_file     : str   File with smoothed PHIS (after dycore smoothing)
    """
    global gravity
    
    ds_3km_pg2 = xr.open_dataset(topo_3km_pg2_file)
    ds_3km_2 = xr.open_dataset(topo_3km_2_file)
    
    # Get smoothed PHIS (H3_d_pg2)
    phis_smoothed = ds_3km_2['PHIS']
    
    # Get PHIS and PHIS_squared from cube3000 mapped to target
    phis = ds_3km_pg2['PHIS']
    phis_squared = ds_3km_pg2['PHIS_squared']
    
    # Compute variance
    var = compute_variance(phis, phis_smoothed, phis_squared)
    
    # SGH = sqrt(max(VAR, 0)) / g
    var = xr.where(var > 0, var, 0)
    sgh = np.sqrt(var) / gravity
    
    ds_3km_pg2.close()
    ds_3km_2.close()
    
    return sgh
#-------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Compute SGH30 and SGH for atmospheric model topography',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--topo-3km-pg2',required=True,help='Topo file with VAR30, PHIS, PHIS_squared from cube3000 on target grid')
    parser.add_argument('--topo-1-pg2',  required=True,help='Topo file with PHIS on target grid from source')
    parser.add_argument('--topo-1-np4',  required=True,help='Topo file with np4 grid coordinates')
    parser.add_argument('--topo-2',      required=True,help='Topo file with smoothed PHIS and PHIS_d')
    parser.add_argument('--topo-3km-2',  required=True,help='Topo file with smoothed PHIS from cube3000')
    parser.add_argument('--output',      required=True,help='Output file for final topography with SGH30 and SGH')
    args = parser.parse_args()
    
    print(f"{verbose_indent}Computing SGH30...")
    ds_out = compute_sgh30(
        args.topo_3km_pg2,
        args.topo_1_pg2,
        args.topo_2,
        args.output
    )
    
    print(f"{verbose_indent}Computing SGH...")
    sgh = compute_sgh(args.topo_3km_pg2, args.topo_3km_2)
    ds_out['SGH'] = sgh
    
    print(f"{verbose_indent}Adding coordinate and smoothed PHIS fields...")
    
    # Add physical grid lat/lon from topo_1_pg2
    ds_1_pg2 = xr.open_dataset(args.topo_1_pg2)
    if 'lon' in ds_1_pg2 and 'lat' in ds_1_pg2:
        ds_out['lon'] = ds_1_pg2['lon']
        ds_out['lat'] = ds_1_pg2['lat']
    ds_1_pg2.close()
    
    # Add np4 grid lat/lon from topo_1 (renamed to lon_d, lat_d)
    ds_1 = xr.open_dataset(args.topo_1_np4)
    if 'lon' in ds_1:
        lon_var = ds_1['lon'].reset_coords(drop=True) if 'lon' in ds_1.coords else ds_1['lon']
        if 'ncol' in lon_var.dims:
            lon_var = lon_var.rename({'ncol': 'ncol_d'})
        ds_out['lon_d'] = lon_var
    if 'lat' in ds_1:
        lat_var = ds_1['lat'].reset_coords(drop=True) if 'lat' in ds_1.coords else ds_1['lat']
        if 'ncol' in lat_var.dims:
            lat_var = lat_var.rename({'ncol': 'ncol_d'})
        ds_out['lat_d'] = lat_var
    ds_1.close()
    
    # Add smoothed PHIS and PHIS_d from topo_2
    ds_2 = xr.open_dataset(args.topo_2)
    if 'PHIS' in ds_2:
        ds_out['PHIS'] = ds_2['PHIS']
    if 'PHIS_d' in ds_2:
        ds_out['PHIS_d'] = ds_2['PHIS_d']
    ds_2.close()
    
    # Write output
    print(f"Writing output to {args.output}...")
    # Set encoding to match typical E3SM conventions
    encoding = {var: {'zlib': True, 'complevel': 1} for var in ds_out.data_vars}
    ds_out.to_netcdf(args.output, encoding=encoding)
    ds_out.close()
    
    print(f"{verbose_indent}Done!")
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------