#!/bin/bash
#-------------------------------------------------------------------------------
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#-------------------------------------------------------------------------------
if [ -z "${proj_root}" ]; then echo -e ${RED}ERROR: proj_root is not defined${NC}; exit ; fi
if [ -z "${grid_name}" ]; then echo -e ${RED}ERROR: grid_name is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
source ${proj_root}/set_project.sh
#-------------------------------------------------------------------------------
create_domain_map=false
#-------------------------------------------------------------------------------
for arg in "$@"; do
  case $arg in
    --create_domain_map) create_domain_map=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done
#-------------------------------------------------------------------------------
if [ -z "${ocn_grid_name}" ]; then echo -e ${RED}ERROR: ocn_grid_name is not defined${NC}; exit ; fi
# if [ -z "${ocn_grid_file}" ]; then echo -e ${RED}ERROR: ocn_grid_file is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
atm_grid_file=${grid_root}/${grid_name_pg2}_scrip.nc
map_file=${maps_root}/map_${ocn_grid_name}_to_${grid_name}-pg2_traave.${timestamp}.nc
domn_tool=${e3sm_src_root}/tools/generate_domain_files/generate_domain_files_E3SM.py
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo "   proj_root           = ${proj_root}"
echo "   grid_name           = ${grid_name}"
echo "   atm_grid_file       = ${atm_grid_file}"
echo "   ocn_grid_name       = ${ocn_grid_name}"
echo "   ocn_grid_file       = ${ocn_grid_file}"
echo "   map_file            = ${map_file}"
echo "   domn_root           = ${domn_root}"
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if [ ! -f ${map_file} ]; then echo -e ${RED}ERROR map_file does not exist:${NC} ${map_file} ; fi
#-------------------------------------------------------------------------------
start=`date +%s` # start timer for entire script
set -e  # Stop script execution on error
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
#-------------------------------------------------------------------------------
source ${unified_src}
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if $create_domain_map; then
  ncremap -a traave --src_grd=${ocn_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file}
fi
#-------------------------------------------------------------------------------
cmd="python ${domn_tool} -m ${map_file} -o ${ocn_grid_name} -l ${grid_name} --date-stamp=${timestamp} --output-root=${domn_root}"
echo $cmd ; echo
eval "$cmd"
#-------------------------------------------------------------------------------
# # Check that files were created
# chk_file1=${domn_root}/domain.ocn.${grid_name}_ICOS10.${timestamp}.nc
# chk_file2=${domn_root}/domain.lnd.${grid_name}_ICOS10.${timestamp}.nc
# if [ ! -f ${map_file} ]; then
#   echo
#   echo -e ${RED} Failed to create map file - Errors ocurred ${NC}
#   echo
# elif [ ! -f ${chk_file1} ]; then
#   echo
#   echo -e ${RED} Failed to create domain file - Errors ocurred ${NC}
#   echo
# fi
#-------------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#-------------------------------------------------------------------------------
