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
if $force_new_3km_data; then eval "rm ${topo_file_3km}" ; fi
create_new_3km=false
if [ ! -f ${topo_file_3km} ]; then create_new_3km=true; fi
# if $force_new_3km_data; then
#   create_new_3km=true;
# fi




#===============================================================================
# remap source topo to target grid (np4 and pg2)
# the np4 data is used to apply dycore smoothing
# the pg2 data is only needed to compute SGH30
#===============================================================================
cmd="${mbda_path}"
cmd="${cmd} --target ${grid_file_np4_mbda}"
cmd="${cmd} --source ${topo_file_src}"
cmd="${cmd} --output ${topo_file_1}"
cmd="${cmd} --fields   htopo"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
chk_file=${topo_file_1}
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-------------------------------------------------------------------------------
# rename stuff
cmd="${unified_bin}/ncrename -O -d grid_size,ncol -v htopo,PHIS ${topo_file_1} ${topo_file_1}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
# Compute phi_s on the target np4 grid
cmd="${unified_bin}/ncap2 -O -s 'PHIS=PHIS*9.80616' ${topo_file_1} ${topo_file_1}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"

cmd="${mbda_path}"
cmd="${cmd} --target ${grid_file_pg2_mbda}"
cmd="${cmd} --source ${topo_file_src}"
cmd="${cmd} --output ${topo_file_1_pg2}"
cmd="${cmd} --fields   htopo --square-fields htopo"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
chk_file=${topo_file_1_pg2}
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-------------------------------------------------------------------------------
# rename stuff
cmd="${unified_bin}/ncrename -O -d grid_size,ncol -v htopo,PHIS -v htopo_squared,PHIS_squared  ${topo_file_1_pg2} ${topo_file_1_pg2}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
# Compute phi_s on the target np4 grid
cmd="${unified_bin}/ncap2 -O -s 'PHIS=PHIS*9.80616; PHIS_squared=PHIS_squared*9.80616*9.80616' ${topo_file_1_pg2} ${topo_file_1_pg2}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"


#===============================================================================
# remap source topo to 3km/ne3000 grid
#===============================================================================
# create 3km/ne3000 topo data file only if it does not exist
if $create_new_3km; then
  echo;echo -e "${CYN}Creating 3km topo data file with mbda${NC}"
  #-----------------------------------------------------------------------------
  cmd="${mbda_path}"
  cmd="${cmd} --target ${grid_file_3km_mbda}"
  cmd="${cmd} --source ${topo_file_src}"
  cmd="${cmd} --output ${topo_file_3km}"
  cmd="${cmd} --fields   htopo --square-fields htopo"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  chk_file=${topo_file_3km_tmp}
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
  #-----------------------------------------------------------------------------
  # Compute varience and phi in new file
  cmd="${unified_bin}/ncap2 -v -O -s \
     'PHIS=htopo*9.80616; VAR30=(htopo_squared-(htopo*htopo))*9.80616*9.80616; grid_center_lat=grid_center_lat; grid_center_lon=grid_center_lon' \
     ${topo_file_3km} ${topo_file_3km}"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
else
  echo;echo -e "${CYN}Skipping 3km topo data file creation${NC}"
fi

#===============================================================================
# remap topo and topo^2 from 3km/ne3000 to target grid
# np4 topo is needed by SGH calc
# pg2 topo and topo squared is needed by SGH calc
#===============================================================================
echo;echo -e "${CYN}Mapping 3km topo data to np4 with mbda${NC}"
#-----------------------------------------------------------------------------
cmd="${mbda_path}"
cmd="${cmd} --target ${grid_file_np4_mbda}"
cmd="${cmd} --source ${topo_file_3km}"
cmd="${cmd} --output ${topo_file_3km_1}"
cmd="${cmd} --fields PHIS"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
chk_file=${topo_file_3km_1}
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-----------------------------------------------------------------------------
# rename stuff
cmd="${unified_bin}/ncrename -O -d grid_size,ncol ${topo_file_3km_1} ${topo_file_3km_1}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------

echo;echo -e "${CYN}Mapping 3km topo data to pg2 with mbda${NC}"
#-----------------------------------------------------------------------------
cmd="${mbda_path}"
cmd="${cmd} --target ${grid_file_pg2_mbda}"
cmd="${cmd} --source ${topo_file_3km}"
cmd="${cmd} --output ${topo_file_3km_pg2}"
cmd="${cmd} --fields PHIS,VAR30 --square-fields PHIS"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
chk_file=${topo_file_3km_pg2}
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-----------------------------------------------------------------------------
# rename stuff
cmd="${unified_bin}/ncrename -O -d grid_size,ncol ${topo_file_3km_pg2} ${topo_file_3km_pg2}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------


#===============================================================================
#===============================================================================
