

----------------------------------------------------------------------------------------------------
# Start Here to setup environment

## NERSC
```shell
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
E3SM_ROOT=/pscratch/sd/w/whannah/tmp_e3sm_src
DATA_ROOT=/global/cfs/cdirs/e3sm/whannah
TOPO_ROOT=${DATA_ROOT}/files_topo
GRID_ROOT=${DATA_ROOT}/files_grid
MAPS_ROOT=${DATA_ROOT}/files_map
NE_SRC_TOPO=3000
SDIST=10; SITER=20
#-------------------------------------------------------------------------------
# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
# source activate hiccup_env
# eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)
# cd ${DATA_ROOT}
#-------------------------------------------------------------------------------
DATESTAMP=20251111


BASE_RES=128;  REFINE_LVL=2; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL} # smaller version for testing
BASE_RES=1024; REFINE_LVL=2; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL}



#-------------------------------------------------------------------------------
echo -e "\n"\
"  DIN_LOC_ROOT : $DIN_LOC_ROOT \n"\
"  E3SM_ROOT    : $E3SM_ROOT \n"\
"  DATA_ROOT    : $DATA_ROOT \n"\
"  TOPO_ROOT    : $TOPO_ROOT \n"\
"  GRID_ROOT    : $GRID_ROOT \n"\
"  MAPS_ROOT    : $MAPS_ROOT \n"\
"\n"\
"  GRID_NAME : ${GRID_NAME} \n ";
#-------------------------------------------------------------------------------
```


--------------------------------------------------------------------------------

# SquadGen

```shell

SQuadGen --refine_file ${HOME}/E3SM_grid_support/figs_RRM/RRM-png.2025-conus.v1.png --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist ${SDIST} --smooth_iter ${SITER} --lon_ref 260 --lat_ref 40 --output ${GRID_ROOT}/${GRID_NAME}.g ; GenerateVolumetricMesh --in ${GRID_ROOT}/${GRID_NAME}.g     --out ${GRID_ROOT}/${GRID_NAME}-pg2.g --np 2 --uniform ; ConvertMeshToSCRIP     --in ${GRID_ROOT}/${GRID_NAME}-pg2.g --out ${GRID_ROOT}/${GRID_NAME}-pg2_scrip.nc; ls -l ${GRID_ROOT}/${GRID_NAME}*

```

```shell # Unrefined grids for comparison
NE=128
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
