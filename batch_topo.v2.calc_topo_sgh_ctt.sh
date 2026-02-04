#!/bin/bash
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
#-------------------------------------------------------------------------------
# echo;echo -e "${CYN} Calculating SGH with cube_to_target ${NC}"
#-------------------------------------------------------------------------------
topo_file_3km=${DIN_LOC_ROOT}/atm/cam/hrtopo/USGS-topo-cube3000.nc
#-------------------------------------------------------------------------------
cmd="${e3sm_src_root}/components/eam/tools/topo_tool/cube_to_target/cube_to_target "
cmd="${cmd} --target-grid ${grid_file_pg2_scrip}"
cmd="${cmd} --input-topography ${topo_file_3km}"
cmd="${cmd} --smoothed-topography ${topo_file_2}"
cmd="${cmd} --output-topography ${topo_file_3}"
# cmd="${cmd} --add-oro-shape"
echo "  $cmd" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
# echo;echo -e "${CYN}Converting to 64-bit data format ${NC}"

cmd="${unified_bin}/ncks -5 ${topo_file_3} ${topo_file_3}.tmp"
echo "  $cmd" ; echo; eval "$cmd"

cmd="mv ${topo_file_3}.tmp ${topo_file_3}"
echo "  $cmd" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
echo;echo -e "${CYN} Appending GLL phi_s data to the smoothed topo file ${NC}"

cmd="${unified_bin}/ncks -A ${topo_file_2} ${topo_file_3}"
echo "  $cmd" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
