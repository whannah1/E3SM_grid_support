#!/bin/bash
#-------------------------------------------------------------------------------
# chrysalis
#SBATCH --account=e3sm
#SBATCH --job-name=EAMxx-AC_gen_domain
#SBATCH --output=/home/ac.whannah/E3SM_grid_support/2025-EAMxx-autocal/logs_slurm/EAMxx-AC_gen_domain_slurm_%x-%j.out
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# NE=256 ; sbatch --job-name=gen_domain_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_domain.sh
# NE=128 ; sbatch --job-name=gen_domain_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_domain.sh
# NE=64  ; sbatch --job-name=gen_domain_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_domain.sh
# NE=32  ; sbatch --job-name=gen_domain_ne$NE --export=ALL,NE=$NE ${HOME}/E3SM/batch_scripts/2025_EAMxx-AC-blitz_batch_domain.sh
#-------------------------------------------------------------------------------
# LCRC paths
home=/home/ac.whannah
data_root=/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2025-EAMxx-autocal
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
e3sm_root=/lcrc/group/e3sm/ac.whannah/scratch/chrys/tmp_e3sm_src
#-------------------------------------------------------------------------------
# NERSC paths
# e3sm_root=/pscratch/sd/w/whannah/tmp_e3sm_src
# data_root=/global/cfs/cdirs/e3sm/whannah
# DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
#-------------------------------------------------------------------------------
timestamp=20251006

grid_root=${data_root}/files_grid
maps_root=${data_root}/files_map
domain_root=${data_root}/files_domain

atm_grid_file=${grid_root}/ne${NE}pg2_scrip.nc
# ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/ICOS10/ocean.ICOS10.scrip.211015.nc
# ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.mask.scrip.20240327.nc
ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.nomask.scrip.20240327.nc
map_file=${maps_root}/map_RRSwISC6to18E3r5_to_ne${NE}pg2_traave.${timestamp}.nc


#-------------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------; echo
echo "   NE                  = ${NE}"; echo
echo "   e3sm_root           = $e3sm_root"
echo "   grid_root           = $grid_root"
echo "   maps_root           = $maps_root"
echo "   domain_root         = $domain_root"
echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"; echo
echo "   atm_file            = $atm_grid_file";
echo "   ocn_file            = $ocn_grid_file";
echo "   MAP_FILE            = $map_file"; echo
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
if [ ! -d ${domain_root}  ]; then echo -e ${RED}ERROR directory does not exist:${NC} ${domain_root} ; fi
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
unified_bin=/lcrc/soft/climate/e3sm-unified/base/envs/e3sm_unified_1.11.1_login/bin
source ${home}/.bashrc
source activate hiccup_env
# eval $(${e3sm_root}/cime/CIME/Tools/get_case_env)
# ulimit -s unlimited # required for larger grids
echo --------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# ncremap -a traave --src_grd=${ocn_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file}

python ${e3sm_root}/tools/generate_domain_files/generate_domain_files_E3SM.py \
-m ${map_file} -o RRSwISC6to18E3r5 -l ne${NE}pg2 --date-stamp=${timestamp} --output-root=${domain_root}

#-------------------------------------------------------------------------------
# # Check that files were created
# chk_file1=${domain_root}/domain.ocn.${grid_name}_ICOS10.${timestamp}.nc
# chk_file2=${domain_root}/domain.lnd.${grid_name}_ICOS10.${timestamp}.nc
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
