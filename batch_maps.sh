#!/bin/bash
#-------------------------------------------------------------------------------
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if [ -z "${proj_root}" ]; then echo -e ${RED}ERROR: proj_root is not defined${NC}; exit ; fi
if [ -z "${grid_name}" ]; then echo -e ${RED}ERROR: grid_name is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
source ${proj_root}/set_project.sh
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo "   proj_root           = ${proj_root}"
echo "   grid_name           = ${grid_name}"
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
start=`date +%s` # start timer for entire script
set -e  # Stop script execution on error
#-------------------------------------------------------------------------------
create_maps_ocn=false
create_maps_lnd=false
create_maps_spa=false
#-------------------------------------------------------------------------------
for arg in "$@"; do
  case $arg in
    --create_maps_ocn) create_maps_ocn=true ;;
    --create_maps_lnd) create_maps_lnd=true ;;
    --create_maps_spa) create_maps_spa=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done
#-------------------------------------------------------------------------------
slurm_log_create_maps_ocn=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.create_maps_ocn.out
slurm_log_create_maps_lnd=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.create_maps_lnd.out
slurm_log_create_maps_spa=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.create_maps_spa.out
#-------------------------------------------------------------------------------
# atm_grid_name=ne${NE}pg2
atm_grid_name=${grid_name}-pg2
atm_grid_file=${grid_root}/${atm_grid_name}_scrip.nc
#---------------------------------------------------------------------------------------------------
# SPA map file - typically src grid is ne30pg2 - this should be changed to an input argument
spa_grid_name=ne30pg2
spa_grid_file=${grid_root}/${spa_grid_name}_scrip.nc
#---------------------------------------------------------------------------------------------------
# alg_list_arg="--alg_lst=esmfaave,esmfbilin,ncoaave,ncoidw,traave,trbilin,trfv2,trintbilin" # default
# alg_list_arg="--alg_lst=traave,trbilin,trfv2,trintbilin"
#---------------------------------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo "   atm_grid_name       = ${atm_grid_name}"
echo "   lnd_grid_name       = ${lnd_grid_name}"
echo "   rof_grid_name       = ${rof_grid_name}"
echo "   ocn_grid_name       = ${ocn_grid_name}"
echo "   spa_grid_name       = ${spa_grid_name}"; echo
echo "   atm_grid_file       = ${atm_grid_file}"
echo "   lnd_grid_file       = ${lnd_grid_file}"
echo "   rof_grid_file       = ${rof_grid_file}"
echo "   ocn_grid_file       = ${ocn_grid_file}"
echo "   spa_grid_file       = ${spa_grid_file}"
echo --------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# if [ -z "${NE}" ]; then echo -e ${RED}ERROR: NE is not defined${NC}; exit ; fi
if [ -z "${grid_name}" ]; then echo -e ${RED}ERROR: grid_name is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
#-------------------------------------------------------------------------------
source ${unified_src}
# eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# The command below are consistent with the commands called by "ncremap -P mwf"
#---------------------------------------------------------------------------------------------------
if $create_maps_ocn; then
  echo; echo -e ${GRN} Creating ocn map files with TempestRemap ${NC} $slurm_log_create_maps; echo
  cd ${maps_root}
  #-----------------------------------------------------------------------------
  map1=${maps_root}/map_${ocn_grid_name}_to_${atm_grid_name}_traave.${timestamp}.nc
  map2=${maps_root}/map_${ocn_grid_name}_to_${atm_grid_name}_trbilin.${timestamp}.nc
  map3=${maps_root}/map_${ocn_grid_name}_to_${atm_grid_name}_trfv2.${timestamp}.nc
  map4=${maps_root}/map_${ocn_grid_name}_to_${atm_grid_name}_trintbilin.${timestamp}.nc
  map5=${maps_root}/map_${atm_grid_name}_to_${ocn_grid_name}_traave.${timestamp}.nc
  map6=${maps_root}/map_${atm_grid_name}_to_${ocn_grid_name}_trbilin.${timestamp}.nc
  map7=${maps_root}/map_${atm_grid_name}_to_${ocn_grid_name}_trfv2.${timestamp}.nc
  map8=${maps_root}/map_${atm_grid_name}_to_${ocn_grid_name}_trintbilin.${timestamp}.nc
  #-----------------------------------------------------------------------------
  cmd1='ncremap --alg_typ=traave           --grd_src="${ocn_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map1}" '
  cmd2='ncremap --alg_typ=trbilin          --grd_src="${ocn_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map2}" '
  cmd3='ncremap --alg_typ=trfv2            --grd_src="${ocn_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map3}" '
  cmd4='ncremap --alg_typ=trintbilin       --grd_src="${ocn_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map4}" '
  cmd5='ncremap --a2o --alg_typ=traave     --grd_src="${atm_grid_file}" --grd_dst="${ocn_grid_file}" --map_fl="${map5}" '
  cmd6='ncremap --a2o --alg_typ=trbilin    --grd_src="${atm_grid_file}" --grd_dst="${ocn_grid_file}" --map_fl="${map6}" '
  cmd7='ncremap --a2o --alg_typ=trfv2      --grd_src="${atm_grid_file}" --grd_dst="${ocn_grid_file}" --map_fl="${map7}" '
  cmd8='ncremap --a2o --alg_typ=trintbilin --grd_src="${atm_grid_file}" --grd_dst="${ocn_grid_file}" --map_fl="${map8}" '
  #-----------------------------------------------------------------------------
  # run commands and check that each map file was created
  echo; echo $cmd1 ; echo; eval "$cmd1"; if [ ! -f ${map1} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map1}; echo; exit 1; fi
  echo; echo $cmd2 ; echo; eval "$cmd2"; if [ ! -f ${map2} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map2}; echo; exit 1; fi
  echo; echo $cmd3 ; echo; eval "$cmd3"; if [ ! -f ${map3} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map3}; echo; exit 1; fi
  echo; echo $cmd4 ; echo; eval "$cmd4"; if [ ! -f ${map4} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map4}; echo; exit 1; fi
  echo; echo $cmd5 ; echo; eval "$cmd5"; if [ ! -f ${map5} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map5}; echo; exit 1; fi
  echo; echo $cmd6 ; echo; eval "$cmd6"; if [ ! -f ${map6} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map6}; echo; exit 1; fi
  echo; echo $cmd7 ; echo; eval "$cmd7"; if [ ! -f ${map7} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map7}; echo; exit 1; fi
  echo; echo $cmd8 ; echo; eval "$cmd8"; if [ ! -f ${map8} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map8}; echo; exit 1; fi
  #-----------------------------------------------------------------------------
else
  echo; echo -e ${CYN} Skipping ocn map generation ${NC}; echo
fi
#---------------------------------------------------------------------------------------------------
if $create_maps_lnd; then
  echo; echo -e ${GRN} Creating lnd map files with TempestRemap ${NC} $slurm_log_create_maps; echo
  cd ${maps_root}
  #-----------------------------------------------------------------------------
  map1=${maps_root}/map_${lnd_grid_name}_to_${atm_grid_name}_traave.${timestamp}.nc
  map2=${maps_root}/map_${lnd_grid_name}_to_${atm_grid_name}_trbilin.${timestamp}.nc
  map3=${maps_root}/map_${lnd_grid_name}_to_${atm_grid_name}_trfv2.${timestamp}.nc
  map4=${maps_root}/map_${lnd_grid_name}_to_${atm_grid_name}_trintbilin.${timestamp}.nc
  map5=${maps_root}/map_${atm_grid_name}_to_${lnd_grid_name}_traave.${timestamp}.nc
  map6=${maps_root}/map_${atm_grid_name}_to_${lnd_grid_name}_trbilin.${timestamp}.nc
  map7=${maps_root}/map_${atm_grid_name}_to_${lnd_grid_name}_trfv2.${timestamp}.nc
  map8=${maps_root}/map_${atm_grid_name}_to_${lnd_grid_name}_trintbilin.${timestamp}.nc
  #-----------------------------------------------------------------------------
  cmd1='ncremap --alg_typ=traave           --grd_src="${lnd_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map1}" '
  cmd2='ncremap --alg_typ=trbilin          --grd_src="${lnd_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map2}" '
  cmd3='ncremap --alg_typ=trfv2            --grd_src="${lnd_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map3}" '
  cmd4='ncremap --alg_typ=trintbilin       --grd_src="${lnd_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${map4}" '
  cmd5='ncremap --a2o --alg_typ=traave     --grd_src="${atm_grid_file}" --grd_dst="${lnd_grid_file}" --map_fl="${map5}" '
  cmd6='ncremap --a2o --alg_typ=trbilin    --grd_src="${atm_grid_file}" --grd_dst="${lnd_grid_file}" --map_fl="${map6}" '
  cmd7='ncremap --a2o --alg_typ=trfv2      --grd_src="${atm_grid_file}" --grd_dst="${lnd_grid_file}" --map_fl="${map7}" '
  cmd8='ncremap --a2o --alg_typ=trintbilin --grd_src="${atm_grid_file}" --grd_dst="${lnd_grid_file}" --map_fl="${map8}" '
  #-----------------------------------------------------------------------------
  # run commands and check that each map file was created
  echo; echo $cmd1 ; echo; eval "$cmd1"; if [ ! -f ${map1} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map1}; echo; exit 1; fi
  echo; echo $cmd2 ; echo; eval "$cmd2"; if [ ! -f ${map2} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map2}; echo; exit 1; fi
  echo; echo $cmd3 ; echo; eval "$cmd3"; if [ ! -f ${map3} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map3}; echo; exit 1; fi
  echo; echo $cmd4 ; echo; eval "$cmd4"; if [ ! -f ${map4} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map4}; echo; exit 1; fi
  echo; echo $cmd5 ; echo; eval "$cmd5"; if [ ! -f ${map5} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map5}; echo; exit 1; fi
  echo; echo $cmd6 ; echo; eval "$cmd6"; if [ ! -f ${map6} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map6}; echo; exit 1; fi
  echo; echo $cmd7 ; echo; eval "$cmd7"; if [ ! -f ${map7} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map7}; echo; exit 1; fi
  echo; echo $cmd8 ; echo; eval "$cmd8"; if [ ! -f ${map8} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${map8}; echo; exit 1; fi
  #-----------------------------------------------------------------------------
else
  echo; echo -e ${CYN} Skipping lnd map generation ${NC}; echo
fi
#---------------------------------------------------------------------------------------------------
if $create_maps_spa; then
  # SPA map files are only for EAMxx
  spa_map=${maps_root}/map_${spa_grid_name}_to_${atm_grid_name}_traave.${timestamp}.nc
  cmd_spa='ncremap --alg_typ=traave --grd_src="${spa_grid_file}" --grd_dst="${atm_grid_file}" --map_fl="${spa_map}" '
  echo; echo $cmd_spa ; echo; eval "$cmd_spa"; if [ ! -f ${spa_map} ]; then echo; echo -e ${RED} Failed to create map file: ${NC} ${spa_map}; echo; exit 1; fi
else
  echo; echo -e ${CYN} Skipping SPA map generation ${NC}; echo
fi
#---------------------------------------------------------------------------------------------------
echo
echo -e ${GRN} Finished creating map files ${NC}
echo
#---------------------------------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#-------------------------------------------------------------------------------