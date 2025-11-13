#!/bin/bash
#SBATCH --account=e3sm
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=EAMxx-AC-blitz_gen_maps
#SBATCH --output=/global/homes/w/whannah/E3SM/logs_slurm/EAMxx-AC-blitz_slurm_%x_%j.out
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# NE=256 ; sbatch --job-name=gen_maps_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_maps.sh
# NE=128 ; sbatch --job-name=gen_maps_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_maps.sh
# NE=64  ; sbatch --job-name=gen_maps_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_maps.sh
# NE=32  ; sbatch --job-name=gen_maps_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_maps.sh
# export NE=256 ; ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_grid_files.sh
# export NE=128 ; ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_grid_files.sh
# export NE=64  ; ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_grid_files.sh
# export NE=32  ; ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_grid_files.sh
#-------------------------------------------------------------------------------
create_grid=false
create_maps_ocn=false
create_maps_lnd=true
#-------------------------------------------------------------------------------
timestamp=20251006

slurm_log_root=/global/homes/w/whannah/E3SM/logs_slurm
slurm_log_create_grid=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID_slurm.create_grid.out
slurm_log_create_maps_ocn=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID_slurm.create_maps_ocn.out
slurm_log_create_maps_lnd=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID_slurm.create_maps_lnd.out


data_root=/global/cfs/cdirs/e3sm/whannah
grid_root=${data_root}/files_grid
maps_root=${data_root}/files_map

DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata

atm_grid_name=ne${NE}pg2
lnd_grid_name=r025
ocn_grid_name=RRSwISC6to18E3r5

atm_grid_file=${grid_root}/${atm_grid_name}_scrip.nc

# /lcrc/group/e3sm/data/inputdata/share/meshes/rof/SCRIPgrid_0.25x0.25_nomask_c200309.nc
# /global/cfs/cdirs/e3sm/inputdata/share/meshes/rof/SCRIPgrid_0.25x0.25_nomask_c200309.nc
lnd_grid_file=${DIN_LOC_ROOT}/share/meshes/rof/SCRIPgrid_0.25x0.25_nomask_c200309.nc
ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.nomask.scrip.20240327.nc
# ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.mask.scrip.20240327.nc
rof_grid_file=${DIN_LOC_ROOT}/lnd/clm2/mappingdata/grids/SCRIPgrid_0.25x0.25_nomask_c200309.nc

#-------------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------; echo
echo "   NE                  = ${NE}"; echo
echo "   grid_root           = $grid_root"
echo "   maps_root           = $maps_root"
# echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"; echo
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if [ -z "${NE}" ]; then echo -e ${RED}ERROR: NE is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
# Make sure paths exist
if [ ! -d ${DIN_LOC_ROOT} ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${DIN_LOC_ROOT} ; fi
if [ ! -d ${e3sm_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${e3sm_root} ; fi
if [ ! -d ${grid_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${grid_root} ; fi
if [ ! -d ${maps_root}    ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${maps_root} ; fi
#-------------------------------------------------------------------------------
# ANSI color codes for highlighting terminal output
RED='\033[0;31m' ; GRN='\033[0;32m' CYN='\033[0;36m' ; NC='\033[0m'
# start timer for entire script
start=`date +%s`
# Stop script execution on error
set -e
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
#-------------------------------------------------------------------------------
unified_bin=/global/common/software/e3sm/anaconda_envs/base/envs/e3sm_unified_1.11.1_login/bin
module load python
source activate hiccup_env
# eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
ulimit -s unlimited # required for larger grids
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if $create_grid; then
  echo
  echo -e ${GRN} Creating grid files with TempestRemap ${NC} $slurm_log_create_grid
  echo
  GenerateCSMesh --alt --res ${NE} --file ${grid_root}/ne${NE}.g >> $slurm_log_create_grid 2>&1
  GenerateVolumetricMesh --in ${grid_root}/ne${NE}.g --out ${grid_root}/ne${NE}pg2.g --np 2 --uniform >> $slurm_log_create_grid 2>&1
  ConvertMeshToSCRIP --in ${grid_root}/ne${NE}pg2.g --out ${grid_root}/ne${NE}pg2_scrip.nc >> $slurm_log_create_grid 2>&1
else
  echo
  echo -e ${CYN} Skipping grid generation ${NC}
  echo
fi
#-------------------------------------------------------------------------------
# Check that grid files were created
chk_file1=${grid_root}/ne${NE}pg2_scrip.nc
if [ ! -f ${chk_file1} ]; then
  echo
  echo -e ${RED} Failed to create domain file - Errors ocurred ${NC}
  echo
fi
#-------------------------------------------------------------------------------
if $create_maps_ocn; then
  echo
  echo -e ${GRN} Creating ocn map files with TempestRemap ${NC} $slurm_log_create_maps
  echo
  cd ${maps_root}
  time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file \
  --nm_src=${ocn_grid_name} --nm_dst=${atm_grid_name} \
  --dt_sng=${timestamp}  >> $slurm_log_create_maps_ocn 2>&1
else
  echo
  echo -e ${CYN} Skipping ocn map generation ${NC}
  echo
fi
#-------------------------------------------------------------------------------
if $create_maps_lnd; then
  echo
  echo -e ${GRN} Creating lnd map files with TempestRemap ${NC} $slurm_log_create_maps
  echo
  cd ${maps_root}
  time ncremap -P mwf -s $lnd_grid_file -g $atm_grid_file \
  --nm_src=${lnd_grid_name} --nm_dst=${atm_grid_name} \
  --dt_sng=${timestamp}  >> $slurm_log_create_maps_lnd 2>&1
else
  echo
  echo -e ${CYN} Skipping lnd map generation ${NC}
  echo
fi
#-------------------------------------------------------------------------------
# Check that grid files were created
chk_file1=${maps_root}/map_${atm_grid_name}_to_${ocn_grid_name}_trintbilin.${timestamp}.nc
if [ ! -f ${chk_file1} ]; then
  echo
  echo -e ${RED} Failed to create map files - Errors ocurred ${NC}
  echo
fi
#-------------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#-------------------------------------------------------------------------------
