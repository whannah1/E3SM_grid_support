#!/bin/bash
#-------------------------------------------------------------------------------
export proj_root=${home}/E3SM_grid_support/${proj}
export data_root=${grid_data_root}/${proj}
export slurm_log_root=${proj_root}/logs_slurm
export hiccup_log_root=${proj_root}/logs_hiccup
#-------------------------------------------------------------------------------
export grid_root=${data_root}/files_grid
export maps_root=${data_root}/files_map
export topo_root=${data_root}/files_topo
export init_root=${data_root}/files_init
export domn_root=${data_root}/files_domain
# export atms_root=${data_root}/files_atmsrf
#-------------------------------------------------------------------------------
export homme_tool_root=${e3sm_src_root}/cmake_homme
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo "MACHINE SPECIFIC PATHS:"
echo "  host              = $host"
echo "  grid_code_root    = $grid_code_root"
echo "  grid_data_root    = $grid_data_root"
echo "  e3sm_src_root     = $e3sm_src_root"
echo "  homme_tool_root   = ${homme_tool_root}"
echo "  DIN_LOC_ROOT      = $DIN_LOC_ROOT"; echo
#-------------------------------------------------------------------------------
echo "PROJECT SPECIFIC PATHS:"
echo "  proj              = ${proj}"
echo "  data_root         = ${data_root}"; echo
echo "  grid_root         = ${grid_root}"
echo "  maps_root         = ${maps_root}"
echo "  topo_root         = ${topo_root}"
echo "  init_root         = ${init_root}"
echo "  domn_root         = ${domn_root}"; echo
# echo "  atms_root         = ${atms_root}"; echo
echo "  slurm_log_root    = ${slurm_log_root}"
echo "  hiccup_log_root   = ${hiccup_log_root}"; echo
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if [ ! -d ${grid_root} ]; then mkdir -p ${grid_root}; fi
if [ ! -d ${maps_root} ]; then mkdir -p ${maps_root}; fi
if [ ! -d ${topo_root} ]; then mkdir -p ${topo_root}; fi
if [ ! -d ${init_root} ]; then mkdir -p ${init_root}; fi
if [ ! -d ${domn_root} ]; then mkdir -p ${domn_root}; fi
# if [ ! -d ${atms_root} ]; then mkdir -p ${atms_root}; fi
#-------------------------------------------------------------------------------
ulimit -s unlimited # required for larger grids
#-------------------------------------------------------------------------------
# ANSI color codes for highlighting terminal output
export RED='\033[0;31m'
export GRN='\033[0;32m'
export YLW='\e[33m'
export CYN='\033[0;36m'
export NC='\033[0m'
#-------------------------------------------------------------------------------