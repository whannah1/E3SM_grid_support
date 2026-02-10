#!/bin/bash
#-------------------------------------------------------------------------------
export slurm_mail_user=hannah6@llnl.gov
export slurm_mail_type="END,FAIL"
#-------------------------------------------------------------------------------
# determine the HPC center we are logged into
host=
scratch_lcrc=/lcrc/group/e3sm/$USER
scratch_alcf=/lus/flare/projects/E3SM_Dec/$USER
scratch_olcf=/lustre/orion/cli115/proj-shared/$USER
scratch_nersc=$SCRATCH
if [ -e ${scratch_lcrc}  ]; then host=LCRC; fi
if [ -e ${scratch_alcf}  ]; then host=ALCF; fi
if [ -e ${scratch_olcf}  ]; then host=OLCF; fi
if [ -e ${scratch_nersc} ]; then host=NERSC; fi
#-------------------------------------------------------------------------------
if [ -z "$host" ]; then echo -e ${RED}ERROR - host machine not identified ; exit 1 ; fi
#-------------------------------------------------------------------------------
# NOTE - the source topography file is still a matter of debate...
# For now, we are focused on a high-res RLL source dataset that is only at NERSC,
# so we set topo_file_src as empty by default unless it has been manually copied
# for that machine
#-------------------------------------------------------------------------------
if [ ${host} == "LCRC" ]; then
  export grid_code_root=${HOME}/E3SM_grid_support
  export grid_data_root=/lcrc/group/e3sm/$USER/scratch/chrys/E3SM_grid_support
  export e3sm_src_root=/lcrc/group/e3sm/$USER/scratch/chrys/tmp_e3sm_src
  export DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
  export unified_bin=/lcrc/soft/climate/e3sm-unified/base/envs/e3sm_unified_1.11.1_login/bin
  export unified_src=/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh
  export mbda_path=/lcrc/soft/climate/moab/chrysalis/intel/bin/mbda
  export topo_file_src=/lcrc/group/e3sm/$USER/scratch/chrys/E3SM_grid_support/topo7.5s/GMTED2010_7.5_stitch_S5P_OPER_REF_DEM_15_NCL_24-3.r172800x86400.nc
fi
#-------------------------------------------------------------------------------
if [ ${host} == "NERSC" ]; then
  # export grid_code_root=/global/cfs/cdirs/e3sm/${USER}/E3SM_grid_support
  export grid_code_root=${HOME}/E3SM_grid_support
  export grid_data_root=/global/cfs/cdirs/e3sm/${USER}/E3SM_grid_support
  # export e3sm_src_root=${HOME}/codes/acme2
  export e3sm_src_root=/pscratch/sd/w/whannah/tmp_e3sm_src
  export DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
  export unified_bin=/global/common/software/e3sm/anaconda_envs/e3smu_1_12_0/pm-cpu/conda/envs/e3sm_unified_1.12.0_login/bin
  export unified_src=/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
  export mbda_path=/global/cfs/cdirs/e3sm/software/moab/intel/bin/mbda
  # export OMP_NUM_THREADS=256 # this is used by MBDA
  export topo_file_src=/global/cfs/cdirs/e3sm/zhang73/grids2/topo7.5s/GMTED2010_7.5_stitch_S5P_OPER_REF_DEM_15_NCL_24-3.r172800x86400.nc
fi
#-------------------------------------------------------------------------------
if [ ${host} == "ALCF" ]; then
  export grid_code_root=${HOME}/E3SM_grid_support
  export grid_data_root=/lus/flare/projects/E3SM_Dec/$USER/E3SM_grid_support
  export e3sm_src_root=/lus/flare/projects/E3SM_Dec/$USER/e3sm_src
  export DIN_LOC_ROOT=/lus/flare/projects/E3SMinput/data
  export unified_bin=/lus/flare/projects/E3SMinput/soft/e3sm-unified/e3smu_1_12_0/aurora/conda/envs/e3sm_unified_1.12.0_login/bin
  export unified_src=/lus/flare/projects/E3SMinput/soft/e3sm-unified/load_latest_e3sm_unified_aurora.sh
  export mbda_path=
  export topo_file_src=
fi
#-------------------------------------------------------------------------------
if [ ${host} == "OLCF" ]; then
  export grid_code_root=${HOME}/E3SM_grid_support
  export grid_data_root=
  export e3sm_src_root=
  export DIN_LOC_ROOT=
  export unified_bin=
  export unified_src=
  export mbda_path=
  export topo_file_src=
fi
#-------------------------------------------------------------------------------
error_found=false
#-------------------------------------------------------------------------------
# check if env variables are unset or empty
if [ -z "${grid_code_root}" ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} grid_code_root ; fi
if [ -z "${grid_data_root}" ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} grid_data_root ; fi
if [ -z "${e3sm_src_root}"  ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} e3sm_src_root ; fi
if [ -z "${DIN_LOC_ROOT}"   ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} DIN_LOC_ROOT ; fi
if [ -z "${unified_bin}"    ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} unified_bin ; fi
if [ -z "${unified_src}"    ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} unified_src ; fi
if [ -z "${mbda_path}"      ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} mbda_path ; fi
if [ -z "${topo_file_src}"  ]; then error_found=true; echo -e ${RED}ERROR - variable not set:${NC} topo_file_src ; fi
#-------------------------------------------------------------------------------
if [ "$error_found" = true ]; then echo "Errors occurred - see above"; exit 1; fi
#-------------------------------------------------------------------------------
# check that system paths exist
if [ ! -d ${grid_code_root} ]; then error_found=true; echo -e ${RED}ERROR - directory does not exist:${NC} grid_code_root: ${grid_code_root} ; fi
if [ ! -d ${grid_data_root} ]; then error_found=true; echo -e ${RED}ERROR - directory does not exist:${NC} grid_data_root: ${grid_data_root} ; fi
if [ ! -d ${e3sm_root}      ]; then error_found=true; echo -e ${RED}ERROR - directory does not exist:${NC} e3sm_root: ${e3sm_root} ; fi
if [ ! -d ${DIN_LOC_ROOT}   ]; then error_found=true; echo -e ${RED}ERROR - directory does not exist:${NC} DIN_LOC_ROOT: ${DIN_LOC_ROOT} ; fi
if [ ! -d ${unified_bin}    ]; then error_found=true; echo -e ${RED}ERROR - E3SM unified binaries path not exist:${NC} ${unified_bin} ; fi
if [ ! -f ${unified_src}    ]; then error_found=true; echo -e ${RED}ERROR - E3SM unified script does not exist:${NC} ${unified_src} ; fi
if [ ! -f ${topo_file_src}  ]; then error_found=true; echo -e ${RED}ERROR - source topo data does not exist:${NC} ${topo_file_src} ; fi
if [ ! -f ${mbda_path}      ]; then error_found=true; echo -e ${RED}ERROR - MBDA path does not exist:${NC} ${mbda_path} ; fi
#-------------------------------------------------------------------------------
if [ "$error_found" = true ]; then echo "Errors occurred - see above"; exit 1; fi
#-------------------------------------------------------------------------------