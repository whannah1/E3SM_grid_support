#!/bin/bash
#-------------------------------------------------------------------------------
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/set_project.sh --skip_mkdir
#-------------------------------------------------------------------------------
if [ -d ${data_root} ]; then echo -e "data_root => ${GRN}OK${NC}"; else echo -e "data_root => ${RED}does not exist!${NC}"; fi
if [ -d ${grid_root} ]; then echo -e "grid_root => ${GRN}OK${NC}"; else echo -e "grid_root => ${RED}does not exist!${NC}"; fi
if [ -d ${maps_root} ]; then echo -e "maps_root => ${GRN}OK${NC}"; else echo -e "maps_root => ${RED}does not exist!${NC}"; fi
if [ -d ${topo_root} ]; then echo -e "topo_root => ${GRN}OK${NC}"; else echo -e "topo_root => ${RED}does not exist!${NC}"; fi
if [ -d ${init_root} ]; then echo -e "init_root => ${GRN}OK${NC}"; else echo -e "init_root => ${RED}does not exist!${NC}"; fi
if [ -d ${domn_root} ]; then echo -e "domn_root => ${GRN}OK${NC}"; else echo -e "domn_root => ${RED}does not exist!${NC}"; fi
# if [ -d ${atms_root} ]; then echo -e "atms_root => ${GRN}OK${NC}"; else echo -e "atms_root => ${RED}does not exist!${NC}"; fi
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# check other important variables
if [ -f ${topo_file_src} ]; then echo -e "topo_file_src => ${GRN}OK${NC}"; else echo -e "topo_file_src => ${RED}does not exist!${NC}"; fi
if [ -f ${mbda_path}     ]; then echo -e "mbda_path     => ${GRN}OK${NC}"; else echo -e "mbda_path     => ${RED}does not exist!${NC}"; fi
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
