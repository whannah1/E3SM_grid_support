#!/bin/bash
#-------------------------------------------------------------------------------
# determine the HPC center we are logged into
host=NONE
scratch_lcrc=/lcrc/group/e3sm/ac.whannah
scratch_alcf=/lus/flare/projects/E3SM_Dec/whannah
scratch_olcf=
scratch_nersc=/pscratch/sd/w/whannah
if [ -e ${scratch_lcrc} ]; then host=LCRC; fi
if [ -e ${scratch_alcf} ]; then host=ALCF; fi
# if [ -e ${scratch_olcf} ]; then host=OLCF; fi
if [ -e ${scratch_nersc} ]; then host=NERSC; fi
#-------------------------------------------------------------------------------
if [ ${host} == "LCRC" ]; then
  export home=/home/ac.whannah
  export grid_data_root=/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support
  export e3sm_src_root=/lcrc/group/e3sm/ac.whannah/scratch/chrys/tmp_e3sm_src
  export DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
  export unified_bin=/lcrc/soft/climate/e3sm-unified/base/envs/e3sm_unified_1.11.1_login/bin
  export unified_src=/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
fi
#-------------------------------------------------------------------------------
if [ ${host} == "NERSC" ]; then
  export home=/global/homes/w/whannah
  export grid_data_root=/global/cfs/cdirs/e3sm/whannah
  export e3sm_src_root=/pscratch/sd/w/whannah/tmp_e3sm_src
  export DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
  export unified_bin=
  export unified_src=
fi
#-------------------------------------------------------------------------------
if [ ${host} == "ALCF" ]; then
  export home=/home/whannah
  export grid_data_root=/lus/flare/projects/E3SM_Dec/whannah/E3SM_grid_support
  export e3sm_src_root=/lus/flare/projects/E3SM_Dec/whannah/e3sm_src
  export DIN_LOC_ROOT=/lus/flare/projects/E3SMinput/data
  export unified_bin=
  export unified_src=
fi
#-------------------------------------------------------------------------------
if [ ${host} == "OLCF" ]; then
  export home=
  export grid_data_root=
  export e3sm_src_root=
  export DIN_LOC_ROOT=
  export unified_bin=
  export unified_src=
fi
#-------------------------------------------------------------------------------
# common paths
export grid_code_root=${home}/E3SM_grid_support
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
echo "   host                = $host"
echo "   grid_code_root      = $grid_code_root"
echo "   grid_data_root      = $grid_data_root"
echo "   e3sm_src_root       = $e3sm_src_root"
echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# check system paths
if [ ! -d ${home}           ]; then echo -e ${RED}ERROR directory does not exist:${NC} home: ${home} ; fi
if [ ! -d ${grid_code_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} grid_code_root: ${DIN_LOC_ROOT} ; fi
if [ ! -d ${grid_data_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} grid_data_root: ${DIN_LOC_ROOT} ; fi
if [ ! -d ${e3sm_root}      ]; then echo -e ${RED}ERROR directory does not exist:${NC} e3sm_root: ${e3sm_root} ; fi
if [ ! -d ${DIN_LOC_ROOT}   ]; then echo -e ${RED}ERROR directory does not exist:${NC} DIN_LOC_ROOT: ${DIN_LOC_ROOT} ; fi
#-------------------------------------------------------------------------------
