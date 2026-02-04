#!/bin/bash
#-------------------------------------------------------------------------------
export slurm_mail_user=hannah6@llnl.gov
export slurm_mail_type="END,FAIL"
#-------------------------------------------------------------------------------
# determine the HPC center we are logged into
host=NONE
scratch_lcrc=/lcrc/group/e3sm/$USER
scratch_alcf=/lus/flare/projects/E3SM_Dec/$USER
scratch_olcf=/lustre/orion/cli115/proj-shared/$USER
scratch_nersc=/pscratch/sd/w/$USER
if [ -e ${scratch_lcrc}  ]; then host=LCRC; fi
if [ -e ${scratch_alcf}  ]; then host=ALCF; fi
if [ -e ${scratch_olcf}  ]; then host=OLCF; fi
if [ -e ${scratch_nersc} ]; then host=NERSC; fi
#-------------------------------------------------------------------------------
# NOTE - the source topography file is still a matter of debate...
# For now, we are focused on a high-res RLL source dataset that is only at NERSC,
# so we set the topo_file_src=NONE by default unless it has been manually copied
# for that machine
#-------------------------------------------------------------------------------
if [ ${host} == "LCRC" ]; then
  export home=/home/$USER
  export grid_code_root=${home}/E3SM_grid_support
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
  export home=$HOME
  export grid_code_root=${CFS}/e3sm/${USER}/E3SM_grid_support
  export grid_data_root=${CFS}/e3sm/${USER}/E3SM_grid_support
  export e3sm_src_root=${home}/codes/acme2
  export DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
  export unified_bin=/global/common/software/e3sm/anaconda_envs/e3smu_1_12_0/pm-cpu/conda/envs/e3sm_unified_1.12.0_login/bin
  export unified_src=/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
  export mbda_path=/global/cfs/cdirs/e3sm/software/moab/intel/bin/mbda
  # export OMP_NUM_THREADS=256 # this is used by MBDA
  export topo_file_src=/global/cfs/cdirs/e3sm/zhang73/grids2/topo7.5s/GMTED2010_7.5_stitch_S5P_OPER_REF_DEM_15_NCL_24-3.r172800x86400.nc
fi
#-------------------------------------------------------------------------------
if [ ${host} == "ALCF" ]; then
  export home=/home/$USER
  export grid_code_root=${home}/E3SM_grid_support
  export grid_data_root=/lus/flare/projects/E3SM_Dec/$USER/E3SM_grid_support
  export e3sm_src_root=/lus/flare/projects/E3SM_Dec/$USER/e3sm_src
  export DIN_LOC_ROOT=/lus/flare/projects/E3SMinput/data
  export unified_bin=/lus/flare/projects/E3SMinput/soft/e3sm-unified/e3smu_1_12_0/aurora/conda/envs/e3sm_unified_1.12.0_login/bin
  export unified_src=/lus/flare/projects/E3SMinput/soft/e3sm-unified/load_latest_e3sm_unified_aurora.sh
  export mbda_path=NONE
  export topo_file_src=NONE
fi
#-------------------------------------------------------------------------------
if [ ${host} == "OLCF" ]; then
  export home=
  export grid_code_root=${home}/E3SM_grid_support
  export grid_data_root=NONE
  export e3sm_src_root=NONE
  export DIN_LOC_ROOT=NONE
  export unified_bin=NONE
  export unified_src=NONE
  export mbda_path=NONE
  export topo_file_src=NONE
fi
#-------------------------------------------------------------------------------
# echo --------------------------------------------------------------------------------
# echo "   host                = $host"
# echo "   grid_code_root      = $grid_code_root"
# echo "   grid_data_root      = $grid_data_root"
# echo "   e3sm_src_root       = $e3sm_src_root"
# echo "   DIN_LOC_ROOT        = $DIN_LOC_ROOT"
# echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# check system paths
if [ ! -d ${home}           ]; then echo -e ${RED}ERROR directory does not exist:${NC} home: ${home} ; fi
if [ ! -d ${grid_code_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} grid_code_root: ${grid_code_root} ; fi
if [ ! -d ${grid_data_root} ]; then echo -e ${RED}ERROR directory does not exist:${NC} grid_data_root: ${grid_data_root} ; fi
if [ ! -d ${e3sm_root}      ]; then echo -e ${RED}ERROR directory does not exist:${NC} e3sm_root: ${e3sm_root} ; fi
if [ ! -d ${DIN_LOC_ROOT}   ]; then echo -e ${RED}ERROR directory does not exist:${NC} DIN_LOC_ROOT: ${DIN_LOC_ROOT} ; fi
#-------------------------------------------------------------------------------
# check other important variables
if [ ! -f ${topo_file_src} ];  then echo -e ${RED}ERROR source topo data does not exist:${NC} ${topo_file_src} ; fi
if [ ! -f ${mbda_path}     ];  then echo -e ${RED}ERROR MBDA path does not exist:${NC} ${mbda_path} ; fi
#-------------------------------------------------------------------------------
