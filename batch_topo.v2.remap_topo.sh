#!/bin/bash
#===============================================================================
force_new_3km_data=false
for arg in "$@"; do
  case $arg in
    --force_new_3km_data)   force_new_3km_data=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done
#===============================================================================
if $force_new_3km_data; then eval "rm ${topo_file_3km} ${topo_file_3sq}" ; fi
create_new_3km=false
create_new_3sq=false
if [ ! -f ${topo_file_3km} ]; then create_new_3km=true; fi
if [ ! -f ${topo_file_3sq} ]; then create_new_3sq=true; fi
# if $force_new_3km_data; then
#   create_new_3km=true;
#   create_new_3sq=true;
# fi
#===============================================================================
# remap source topo to target grid
#===============================================================================
cmd="${mbda_path}"
cmd="${cmd} --target ${grid_file_np4_scrip}"
cmd="${cmd} --source ${topo_file_src}"
cmd="${cmd} --output ${topo_file_1}"
cmd="${cmd} --fields   htopo"
cmd="${cmd} --dof-var  grid_size"
cmd="${cmd} --lon-var  grid_center_lon"
cmd="${cmd} --lat-var  grid_center_lat"
cmd="${cmd} --area-var grid_area"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
chk_file=${topo_file_1}
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-------------------------------------------------------------------------------
# rename stuff
cmd="${unified_bin}/ncrename -O -d grid_size,ncol ${topo_file_1} ${topo_file_1}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
# Compute phi_s on the target np4 grid
cmd="${unified_bin}/ncap2 -O -s 'PHIS=htopo*9.80616' ${topo_file_1} ${topo_file_1}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#===============================================================================
# remap source topo to 3km/ne3000 grid
#===============================================================================
# create 3km/ne3000 topo data file only if it does not exist
if $create_new_3km; then
  echo;echo -e "${CYN}Creating 3km topo data file with mbda${NC}"
  #-----------------------------------------------------------------------------
  cmd="${mbda_path}"
  cmd="${cmd} --target ${grid_file_3km_scrip}"
  cmd="${cmd} --source ${topo_file_src}"
  cmd="${cmd} --output ${topo_file_3km}"
  cmd="${cmd} --fields   htopo"
  cmd="${cmd} --dof-var  grid_size"
  cmd="${cmd} --lon-var  grid_center_lon"
  cmd="${cmd} --lat-var  grid_center_lat"
  cmd="${cmd} --area-var grid_area"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  chk_file=${topo_file_3km}
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
  #-----------------------------------------------------------------------------
  # # rename stuff
  # cmd="${unified_bin}/ncrename -O -d grid_size,ncol ${topo_file_3km} ${topo_file_3km}"
  # echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  # Compute phi_s on the target np4 grid
  cmd="${unified_bin}/ncap2 -O -s 'PHIS=htopo*9.80616' ${topo_file_3km} ${topo_file_3km}"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
else
  echo;echo -e "${CYN}Skipping 3km topo data file creation${NC}"
fi
#===============================================================================
# remap the square of the topo from 3km/ne3000 to target grid
#===============================================================================
# create 3km/ne3000 topo data file only if it does not exist
if $create_new_3sq; then
  echo;echo -e "${CYN}Creating 3km topo data file with mbda${NC}"
  #-----------------------------------------------------------------------------
  cmd="${mbda_path}"
  cmd="${cmd} --target ${grid_file_np4_scrip}"
  cmd="${cmd} --source ${topo_file_3km}"
  cmd="${cmd} --output ${topo_file_3sq}"
  # cmd="${cmd} --fields   htopo"
  cmd="${cmd} --square-fields PHIS"
  cmd="${cmd} --dof-var  grid_size"
  cmd="${cmd} --lon-var  grid_center_lon"
  cmd="${cmd} --lat-var  grid_center_lat"
  cmd="${cmd} --area-var grid_area"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  chk_file=${topo_file_3sq}
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
  #-----------------------------------------------------------------------------
  # rename stuff
  cmd="${unified_bin}/ncrename -O -d grid_size,ncol ${topo_file_3sq} ${topo_file_3sq}"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  # # Compute phi_s on the target np4 grid
  # cmd="${unified_bin}/ncap2 -O -s 'PHIS=htopo*9.80616' ${topo_file_3sq} ${topo_file_3sq}"
  # echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
else
  echo;echo -e "${CYN}Skipping 3km topo data file creation${NC}"
fi
#===============================================================================
#===============================================================================
