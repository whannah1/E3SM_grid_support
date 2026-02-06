#!/bin/bash
#-------------------------------------------------------------------------------
skip_mkdir=false
#-------------------------------------------------------------------------------
for arg in "$@"; do
  case $arg in
    --skip_mkdir) skip_mkdir=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done
#-------------------------------------------------------------------------------
# ANSI color codes for highlighting terminal output
export RED='\033[0;31m'
export GRN='\033[0;32m'
export YLW='\e[33m'
export CYN='\033[0;36m'
export BLD='\033[1m'
export NC='\033[0m'
#-------------------------------------------------------------------------------
export proj_root=${grid_code_root}/${proj}
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
# export homme_tool_root=$SCRATCH/hommetool
#-------------------------------------------------------------------------------
echo    "--------------------------------------------------------------------------------"
echo -e "${BLD}MACHINE SPECIFIC PATHS:${NC}"
echo    "  host              = $host"
echo    "  grid_code_root    = $grid_code_root"
echo    "  grid_data_root    = $grid_data_root"
echo    "  e3sm_src_root     = $e3sm_src_root"
echo    "  homme_tool_root   = ${homme_tool_root}"
echo    "  DIN_LOC_ROOT      = $DIN_LOC_ROOT"; echo
echo    "  unified_src       = $unified_src"
echo    "  unified_bin       = $unified_bin"; echo
echo    "  topo_file_src     = $topo_file_src"
echo    "  mbda_path         = $mbda_path"
echo    "--------------------------------------------------------------------------------"
echo -e "${BLD}PROJECT SPECIFIC PATHS:${NC}"
echo    "  proj              = ${proj}"
echo    "  timestamp         = ${timestamp}"; echo
echo    "  data_root         = ${data_root}"
echo    "  grid_root         = ${grid_root}"
echo    "  maps_root         = ${maps_root}"
echo    "  topo_root         = ${topo_root}"
echo    "  init_root         = ${init_root}"
echo    "  domn_root         = ${domn_root}"; echo
# echo    "  atms_root         = ${atms_root}"; echo
echo    "  slurm_log_root    = ${slurm_log_root}"
echo    "  hiccup_log_root   = ${hiccup_log_root}"
echo    "--------------------------------------------------------------------------------"
echo -e "${BLD}USER SPECIFIC SLURM VARIABLES:${NC}"
echo    "  slurm_mail_user   = $slurm_mail_user"
echo    "  slurm_mail_type   = $slurm_mail_type"
echo    "--------------------------------------------------------------------------------"
#-------------------------------------------------------------------------------
if ! $skip_mkdir; then
  if [ ! -d ${grid_root} ]; then mkdir -p ${grid_root}; fi
  if [ ! -d ${maps_root} ]; then mkdir -p ${maps_root}; fi
  if [ ! -d ${topo_root} ]; then mkdir -p ${topo_root}; fi
  if [ ! -d ${init_root} ]; then mkdir -p ${init_root}; fi
  if [ ! -d ${domn_root} ]; then mkdir -p ${domn_root}; fi
  # if [ ! -d ${atms_root} ]; then mkdir -p ${atms_root}; fi
  if [ ! -d ${slurm_log_root} ];  then mkdir -p ${slurm_log_root}; fi
  if [ ! -d ${hiccup_log_root} ]; then mkdir -p ${hiccup_log_root}; fi
fi
#-------------------------------------------------------------------------------
ulimit -s unlimited # required for larger grids
#-------------------------------------------------------------------------------
