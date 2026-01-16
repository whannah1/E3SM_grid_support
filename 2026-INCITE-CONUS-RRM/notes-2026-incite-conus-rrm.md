

echo "OMP_PROC_BIND = ${OMP_PROC_BIND}"; echo "OMP_PLACES = ${OMP_PLACES}"; echo "HDF5_USE_FILE_LOCKING = ${HDF5_USE_FILE_LOCKING}"; echo "FI_MR_CACHE_MONITOR = ${FI_MR_CACHE_MONITOR}"; echo "MPICH_COLL_SYNC = ${MPICH_COLL_SYNC}"; echo "MPICH_SMP_SINGLE_COPY_MODE = ${MPICH_SMP_SINGLE_COPY_MODE}"

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
```

## LCRC
```shell
DIN_LOC_ROOT=/lcrc/group/e3sm/data/inputdata
E3SM_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/tmp_e3sm_src
DATA_ROOT=/lcrc/group/e3sm/ac.whannah
TOPO_ROOT=${DATA_ROOT}/files_topo
GRID_ROOT=${DATA_ROOT}/files_grid
MAPS_ROOT=${DATA_ROOT}/files_map
NE_SRC_TOPO=3000
SDIST=10; SITER=20
```

```shell
#-------------------------------------------------------------------------------
# source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
# source activate hiccup_env
# eval $(${E3SM_ROOT}/cime/CIME/Tools/get_case_env)
# cd ${DATA_ROOT}
#-------------------------------------------------------------------------------
DATESTAMP=20251111


# smaller version for testing
BASE_RES=128;  REFINE_LVL=2; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL}
BASE_RES=128;  REFINE_LVL=3; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL}
BASE_RES=128;  REFINE_LVL=4; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL}


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

# alt w/o rotation
BASE_RES=128; REFINE_LVL=2; GRID_NAME=2025-scream-conus-no-rot-${BASE_RES}x${REFINE_LVL}
# BASE_RES=1024;REFINE_LVL=2; GRID_NAME=2025-scream-conus-rect-${BASE_RES}x${REFINE_LVL}
SQuadGen --refine_file ${HOME}/E3SM_grid_support/figs_RRM/RRM-png.2025-conus.v1.png --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist ${SDIST} --smooth_iter ${SITER} --output ${GRID_ROOT}/${GRID_NAME}.g ; GenerateVolumetricMesh --in ${GRID_ROOT}/${GRID_NAME}.g     --out ${GRID_ROOT}/${GRID_NAME}-pg2.g --np 2 --uniform ; ConvertMeshToSCRIP     --in ${GRID_ROOT}/${GRID_NAME}-pg2.g --out ${GRID_ROOT}/${GRID_NAME}-pg2_scrip.nc; ls -l ${GRID_ROOT}/${GRID_NAME}*

# alt rectangule refinement for comparison
# BASE_RES=128; REFINE_LVL=2; GRID_NAME=2025-scream-conus-rect-${BASE_RES}x${REFINE_LVL}
BASE_RES=128; REFINE_LVL=4; GRID_NAME=2025-scream-conus-rect-${BASE_RES}x${REFINE_LVL}
RLAT1=20; RLAT2=50; RLON1=-130; RLON2=-50
SQuadGen --refine_rect ${RLON1},${RLAT1},${RLON2},${RLAT2},${REFINE_LVL} --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist ${SDIST} --smooth_iter ${SITER} --lon_ref 260 --lat_ref 40 --output ${GRID_ROOT}/${GRID_NAME}.g ; GenerateVolumetricMesh --in ${GRID_ROOT}/${GRID_NAME}.g     --out ${GRID_ROOT}/${GRID_NAME}-pg2.g --np 2 --uniform ; ConvertMeshToSCRIP     --in ${GRID_ROOT}/${GRID_NAME}-pg2.g --out ${GRID_ROOT}/${GRID_NAME}-pg2_scrip.nc; ls -l ${GRID_ROOT}/${GRID_NAME}*

```

```shell # Unrefined grids for comparison
NE=128
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```

--------------------------------------------------------------------------------
# MBDA

```shell
grid_name=2026-incite-conus-1024x2
grid_root=/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/files_grid
grid_file_np4_scrip=${grid_root}/${grid_name}-np4_scrip.nc
topo_file_0=/global/cfs/cdirs/e3sm/zhang73/grids2/topo15s/S5P_OPER_REF_DEM_15_24-3_cube12000.nc
topo_file_1=${topo_root}/tmp_USGS-topo_${grid_name}-np4.nc
/global/cfs/cdirs/e3sm/software/moab/gnu/bin/mbda \
    --target ${grid_file_np4_scrip} \
    --source ${topo_file_0} \
    --output ${topo_file_1} \
    --fields htopo \
    --dof-var grid_size \
    --lon-var grid_center_lon \
    --lat-var grid_center_lat \
    --area-var grid_area
```

The ncdump output below shows what the 

```shell
> ncdump -h /global/cfs/cdirs/e3sm/whannah/files_topo/tmp_USGS-topo_ne32np4.nc
netcdf tmp_USGS-topo_ne32np4 {
dimensions:
  ncol = 55298 ;
  nvar_dirOA = 1953392943 ;
  nvar_dirOL = 959328814 ;
variables:
  double PHIS(ncol) ;
    PHIS:long_name = "surface geopotential\025" ;
    PHIS:units = "m2/s2" ;
    PHIS:missing_value = 1.e+36 ;
    PHIS:_FillValue = 1.e+36 ;
  double SGH(ncol) ;
    SGH:missing_value = 1.e+36 ;
    SGH:_FillValue = 1.e+36 ;
    SGH:long_name = "standard deviation of 3km cubed-sphere elevation" ;
    SGH:units = "m" ;
  double SGH30(ncol) ;
    SGH30:missing_value = 1.e+36 ;
    SGH30:_FillValue = 1.e+36 ;
    SGH30:long_name = "standard deviation of 30s elevation from 3km cube" ;
    SGH30:units = "m" ;
  double lat(ncol) ;
    lat:long_name = "latitude" ;
    lat:units = "degrees_north" ;
  double lon(ncol) ;
    lon:long_name = "longitude" ;
    lon:units = "degrees_east" ;

// global attributes:
    :source = "USGS 30-sec dataset binned to ncube3000 (cube-sphe" ;
    :title = "30-second USGS topo data" ;
    :history = "Written on date: 20251007" ;
}
```
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
