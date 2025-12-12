#!/bin/bash
#-------------------------------------------------------------------------------
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/set_project.sh
#-------------------------------------------------------------------------------
if [ -d ${data_root} ]; then echo -e "data_root => ${GRN}OK${END}"; else echo -e "data_root => ${RED}does not exist!${NC}"; fi
if [ -d ${grid_root} ]; then echo -e "grid_root => ${GRN}OK${END}"; else echo -e "grid_root => ${RED}does not exist!${NC}"; fi
if [ -d ${maps_root} ]; then echo -e "maps_root => ${GRN}OK${END}"; else echo -e "maps_root => ${RED}does not exist!${NC}"; fi
if [ -d ${topo_root} ]; then echo -e "topo_root => ${GRN}OK${END}"; else echo -e "topo_root => ${RED}does not exist!${NC}"; fi
if [ -d ${init_root} ]; then echo -e "init_root => ${GRN}OK${END}"; else echo -e "init_root => ${RED}does not exist!${NC}"; fi
if [ -d ${domn_root} ]; then echo -e "domn_root => ${GRN}OK${END}"; else echo -e "domn_root => ${RED}does not exist!${NC}"; fi
if [ -d ${atms_root} ]; then echo -e "atms_root => ${GRN}OK${END}"; else echo -e "atms_root => ${RED}does not exist!${NC}"; fi
#-------------------------------------------------------------------------------
# if [ ! -d "${data_root}" ]; then echo -e "Creating data_root => ${data_root}"; fi #mkdir -p ${data_root}
# if [ ! -d "${grid_root}" ]; then echo -e "Creating grid_root => ${grid_root}"; fi #mkdir -p ${grid_root}
# if [ ! -d "${maps_root}" ]; then echo -e "Creating maps_root => ${maps_root}"; fi #mkdir -p ${maps_root}
# if [ ! -d "${topo_root}" ]; then echo -e "Creating topo_root => ${topo_root}"; fi #mkdir -p ${topo_root}
# if [ ! -d "${init_root}" ]; then echo -e "Creating init_root => ${init_root}"; fi #mkdir -p ${init_root}
# if [ ! -d "${domn_root}" ]; then echo -e "Creating domn_root => ${domn_root}"; fi #mkdir -p ${domn_root}
# if [ ! -d "${atms_root}" ]; then echo -e "Creating atms_root => ${atms_root}"; fi #mkdir -p ${atms_root}
#-------------------------------------------------------------------------------