#!/usr/bin/env python
# ==================================================================================================
# HICCUP - Hindcast Initial Condition Creation Utility/Processor
# This tool automates the creation of atmospheric initial condition files for 
# E3SM using user supplied file for atmospheric and sea surface conditions.
# ==================================================================================================
'''
# add PHIS from topo file to old IC file

DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
src_root=${DIN_LOC_ROOT}/atm/cam/inic/homme
dst_root=/global/cfs/cdirs/m4310/whannah/files_init
old_IC_file=${src_root}/eami_mam4_Linoz_ne30np4_L80_c20231010.nc
new_IC_file=${dst_root}/eami_mam4_Linoz_ne30np4_L80_c20231010_w-topo-16xdel2.nc
src_topo=${DIN_LOC_ROOT}/atm/cam/topo/USGS-gtopo30_ne30np4pg2_16xdel2.c20200108.nc

DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
src_root=/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000
dst_root=/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000
old_IC_file=${src_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc
new_IC_file=${dst_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000_w-topo-x6t-SGH.nc
src_topo=${DIN_LOC_ROOT}/atm/cam/topo/USGS-gtopo30_ne30np4pg2_x6t-SGH.c20210614.nc

cp ${old_IC_file}  ${new_IC_file}
ncks -A ${src_topo} ${new_IC_file} -v PHIS_d
ncrename -v PHIS_d,PHIS  ${new_IC_file}
echo ; echo ${new_IC_file} ; echo

new_IC_file=${dst_root}/eami_mam4_Linoz_ne30np4_L80_c20231010_w-topo-x6t.nc
src_topo=${DIN_LOC_ROOT}/atm/cam/topo/USGS-gtopo30_ne30np4pg2_x6t-SGH.c20210614.nc

cp ${old_IC_file}  ${new_IC_file}
ncks -A ${src_topo} ${new_IC_file} -v PHIS_d
ncrename -v PHIS_d,PHIS  ${new_IC_file}
echo ; echo ${new_IC_file} ; echo


DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
src_topo=${DIN_LOC_ROOT}/atm/cam/topo/USGS-gtopo30_ne30np4pg2_16xdel2.c20200108.nc

'''
# ==================================================================================================
import os, optparse, datetime
from hiccup import hiccup
# ------------------------------------------------------------------------------
# # Parse the command line options
# parser = optparse.OptionParser()
# parser.add_option('--hgrid',dest='horz_grid',default=None,help='Sets the output horizontal grid')
# parser.add_option('--vgrid',dest='vert_grid',default=None,help='Sets the output vertical grid')
# (opts, args) = parser.parse_args()
# ------------------------------------------------------------------------------
# Logical flags for controlling what this script will do (comment out to disable)
create_map_file = True
remap_data_horz = True
do_sfc_adjust   = True
remap_data_vert = True
### do_state_adjust = True    # this is problematic for this case - not sure why
combine_files   = True
# ------------------------------------------------------------------------------
output_root   = '/global/cfs/cdirs/e3sm/whannah/E3SM_grid_support/2025-ne16-revival' # root path for data output
# din_loc_root  = '/global/cfs/cdirs/e3sm/inputdata' # path for supported E3SM input data
timestamp     = '20251210' # time stamp for output
dst_horz_grid = 'ne16np4' # output horizontal atmosphere grid

# output vertical grid for atmosphere
tgt_mdl,dst_vert_grid,dst_vert_file = 'EAMXX','L128','/global/homes/w/whannah/HICCUP/files_vert/vert_coord_E3SM_L128.nc'
# tgt_mdl,dst_vert_grid,dst_vert_file = 'EAM',  'L80', '/global/homes/w/whannah/HICCUP/files_vert/L80_for_E3SMv3.nc'

if tgt_mdl=='EAM': remap_data_vert = False

# specify input file name
eami_file = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000/v3.LR.amip_0101.eam.i.2000-01-01-00000_w-topo-x6t-SGH.nc'

# output file path
if tgt_mdl=='EAM'  :output_atm_file_name = f'{output_root}/files_init/v3.LR.amip_0101.eam.i.2000-01-01-00000.{dst_horz_grid}.{timestamp}.nc'
if tgt_mdl=='EAMXX':output_atm_file_name = f'{output_root}/files_init/v3.LR.amip_0101.eam.i.2000-01-01-00000.{dst_horz_grid}.{timestamp}.EAMxx-format.nc'

# topo files
src_topo_file_name = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne30np4_smoothedx6t_20250513.nc'
dst_topo_file_name = '/global/cfs/cdirs/e3sm/whannah/E3SM_grid_support/2025-ne16-revival/files_topo/USGS-topo_ne16-np4_smoothedx6t_20251210.nc'

# ------------------------------------------------------------------------------
# Create HICCUP data class instance

hiccup_data = hiccup.create_hiccup_data(src_data_name='EAM',
                                        target_model=tgt_mdl,
                                        dst_horz_grid=dst_horz_grid,
                                        dst_vert_grid=dst_vert_grid,
                                        atm_file=eami_file,
                                        sfc_file=eami_file,
                                        # sfc_file=src_topo_file_name,
                                        topo_file=dst_topo_file_name,
                                        output_dir=f'{output_root}/files_init',
                                        grid_dir=f'{output_root}/files_grid',
                                        map_dir=f'{output_root}/files_map',
                                        tmp_dir=f'{output_root}/files_hiccup_tmp',
                                        verbose=True,)
# ------------------------------------------------------------------------------
# Print some informative stuff
print('\n  Input Files')
print(f'    input atm file:  {hiccup_data.atm_file}')
print(f'    input topo file: {hiccup_data.topo_file}')
print('\n  Output files')
print(f'    output atm file: {output_atm_file_name}')
# ------------------------------------------------------------------------------
# create file name dictionaries for np4 and pg2 data (both are needed)

dst_horz_grid_pg = dst_horz_grid.replace('np4','pg2')

# use separate timestamp for temporary files to ensure these files 
# are distinct from other instances of HICCUP that might be running.
# The routine to generate the multifile dict will generate it's own
# timestamp, but it wil use minutes and seconds, which can become a 
# problem when iteratively debugging a HICCUP script

# ------------------------------------------------------------------------------
# print(hiccup_data)
# exit()
# ------------------------------------------------------------------------------
# Get dict of temporary files for each variable

file_dict = hiccup_data.get_multifile_dict(timestamp=f'{tgt_mdl}.{timestamp}')

# ------------------------------------------------------------------------------
# Create grid and mapping files
if 'create_map_file' not in locals(): create_map_file = False
if create_map_file :

    # Create grid description files needed for the mapping file
    hiccup_data.create_src_grid_file()
    hiccup_data.create_dst_grid_file()

    # Create mapping files
    hiccup_data.create_map_file()

# ------------------------------------------------------------------------------
# perform multi-file horizontal remap
if 'remap_data_horz' not in locals(): remap_data_horz = False
if remap_data_horz :

    # Horizontally regrid np4 data
    hiccup_data.map_file = hiccup_data.map_file_np
    hiccup_data.remap_horizontal_multifile(file_dict=file_dict)

    # Rename variables to match what the model expects
    hiccup_data.rename_vars_multifile(file_dict=file_dict)

    # Add time/date information
    hiccup_data.add_time_date_variables_multifile_eam(file_dict=file_dict)
# ------------------------------------------------------------------------------
# Do surface adjustments
if 'do_sfc_adjust' not in locals(): do_sfc_adjust = False
if do_sfc_adjust:

    hiccup_data.surface_adjustment_multifile(file_dict=file_dict,
                                             adj_TS=False,
                                             adj_PS=True,
                                             adj_T_eam=True)

# ------------------------------------------------------------------------------
# Vertically remap the data
if 'remap_data_vert' not in locals(): remap_data_vert = False
if remap_data_vert :

  hiccup_data.remap_vertical_multifile(file_dict=file_dict,
                                       vert_file_name=dst_vert_file)

# ------------------------------------------------------------------------------
# Perform final state adjustments on interpolated data and add additional data
if 'do_state_adjust' not in locals(): do_state_adjust = False
if do_state_adjust :

    # only need to adjust data on np4 grid
    hiccup_data.atmos_state_adjustment_multifile(file_dict=file_dict)

# ------------------------------------------------------------------------------
# Combine files
if 'combine_files' not in locals(): combine_files = False
if combine_files :

    # Combine and delete temporary files
    hiccup_data.combine_files(file_dict=file_dict,
                              delete_files=True,
                              output_file_name=output_atm_file_name)

    # Clean up the global attributes of the file
    hiccup_data.clean_global_attributes(file_name=output_atm_file_name)

# ------------------------------------------------------------------------------
# Print final output file name

print()
print(f'output_atm_file_name: {output_atm_file_name}')
print()

# Print summary of timer info
hiccup_data.print_timer_summary()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
