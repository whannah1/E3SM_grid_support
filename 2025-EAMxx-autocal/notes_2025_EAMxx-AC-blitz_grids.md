
```shell
# NERSC
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
# LCRC
salloc --nodes 1 --qos interactive --time 04:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash

#-------------------------------------------------------------------------------

data_root=/global/cfs/cdirs/e3sm/whannah
grid_root=${data_root}/files_grid
maps_root=${data_root}/files_map

timestamp=20251006

e3sm_root=/pscratch/sd/w/whannah/tmp_e3sm_src
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata

NE=32 # 256 / 128 / 64 / 32

atm_grid_name=ne${NE}pg2
rof_grid_name=r025
ocn_grid_name=RRSwISC6to18E3r5

atm_grid_file=${grid_root}/${atm_grid_name}_scrip.nc

ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.nomask.scrip.20240327.nc
# ocn_grid_file=${DIN_LOC_ROOT}/ocn/mpas-o/RRSwISC6to18E3r5/ocean.RRSwISC6to18E3r5.mask.scrip.20240327.nc
rof_grid_file=${DIN_LOC_ROOT}/lnd/clm2/mappingdata/grids/SCRIPgrid_0.25x0.25_nomask_c200309.nc

#-------------------------------------------------------------------------------
# target grids:
ne256pg2_r025_RRSwISC6to18E3r5
ne128pg2_r025_RRSwISC6to18E3r5
ne64pg2_r025_RRSwISC6to18E3r5
ne32pg2_r025_RRSwISC6to18E3r5
#-------------------------------------------------------------------------------
# ALCF path
/lus/flare/projects/E3SM_Dec/whannah/HICCUP/
#-------------------------------------------------------------------------------
# files to edit:
/global/homes/w/whannah/E3SM/E3SM_SRC2/cime_config/config_grids.xml
/global/homes/w/whannah/E3SM/E3SM_SRC2/components/eam/bld/config_files/horiz_grid.xml
#-------------------------------------------------------------------------------
```

# Grid File Generation

```shell
NE=32 # 256 / 128 / 64 / 32

GenerateCSMesh --alt --res ${NE} --file ${grid_root}/ne${NE}.g
GenerateVolumetricMesh --in ${grid_root}/ne${NE}.g --out ${grid_root}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/ne${NE}pg2.g --out ${grid_root}/ne${NE}pg2_scrip.nc

ncap2 -s 'grid_imask=int(grid_imask)' ${grid_root}/ne${NE}.g           ${grid_root}/ne${NE}_tmp.g
ncap2 -s 'grid_imask=int(grid_imask)' ${grid_root}/ne${NE}pg2_scrip.nc ${grid_root}/ne${NE}pg2_scrip_tmp.nc

mv ${grid_root}/ne${NE}_tmp.g           ${grid_root}/ne${NE}.g
mv ${grid_root}/ne${NE}pg2_scrip_tmp.nc ${grid_root}/ne${NE}pg2_scrip.nc

```

# Build `homme_tool`

```shell
# mkdir -p ${E3SM_ROOT}/cmake_homme
cd ${E3SM_ROOT}/cmake_homme

eval $( ${E3SM_ROOT}/cime/CIME/Tools/get_case_env )

mach_file=${E3SM_ROOT}/components/homme/cmake/machineFiles/pm-cpu.cmake

cmake -C ${mach_file}  \
-DBUILD_HOMME_WITHOUT_PIOLIBRARY=OFF \
-DPREQX_PLEV=26  \
${E3SM_ROOT}/components/homme

make -j4 homme_tool

```

```shell
# clean up previous homme_tool build
git clean -f 
rm -rf CMakeFiles/ src/preqx/CMakeFiles/ src/preqx_acc/CMakeFiles/ src/sweqx/CMakeFiles/ src/theta-l/CMakeFiles/ src/tool/CMakeFiles/ test/unit_tests/CMakeFiles/ utils/csm_share/CMakeFiles/
rm -rf ${E3SM_ROOT}/cime
rm -rf ${E3SM_ROOT}/externals/scorpio
git submodule sync ; git submodule update --init --recursive
git status
```

# Build `cube_to_target`

```shell
# build cube_to_target
cd ${E3SM_ROOT}/components/eam/tools/topo_tool/cube_to_target
# eval $( ${E3SM_ROOT}/cime/CIME/Tools/get_case_env )
make clean
make FC=gfortran
```

# Coupler Mapping Files

# Coupler Mapping Files - OCN

```shell atm/ocn
NE=32 # 256 / 128 / 64 / 32
ulimit -s unlimited
cd ${maps_root}
time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=${ocn_grid_name} --nm_dst=${atm_grid_name} --dt_sng=${timestamp}
# nohup time ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=${ocn_grid_name} --nm_dst=${atm_grid_name} --dt_sng=${timestamp} > log.ne${NE}pg2 & 
```

https://acme-climate.atlassian.net/wiki/spaces/DOC/pages/178848194/Recommended+Mapping+Procedures+for+E3SM+Atmosphere+Grids#RecommendedMappingProceduresforE3SMAtmosphereGrids-E3SMv2withpg2

# Coupler Mapping Files - ROF

```shell




map_file_A2R=${maps_root}/map_${atm_grid_name}_to_${rof_grid_name}_trfv2.${timestamp}.nc
map_file_R2A=${maps_root}/map_${rof_grid_name}_to_${atm_grid_name}_trfv2.${timestamp}.nc
ncremap --alg_typ=trfv2 --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap --alg_typ=trfv2 --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A

# map_file_A2R=${maps_root}/map_${atm_grid_name}_to_${rof_grid_name}_mono.${timestamp}.nc
# map_file_R2A=${maps_root}/map_${rof_grid_name}_to_${atm_grid_name}_mono.${timestamp}.nc
# map_opts="--wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'"
# ncremap -a tempest --a2o --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R} ${map_opts}
# ncremap -a tempest       --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A} ${map_opts}

# map_file_A2R=${maps_root}/map_${atm_grid_name}_to_${rof_grid_name}_traave.${timestamp}.nc
# map_file_R2A=${maps_root}/map_${rof_grid_name}_to_${atm_grid_name}_traave.${timestamp}.nc
# ncremap -a tempest --a2o --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
# ncremap -a tempest       --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
# ls -l $map_file_A2R $map_file_R2A


map_file_A2R=${maps_root}/map_${atm_grid_name}_to_${rof_grid_name}_traave.${timestamp}.nc
map_file_R2A=${maps_root}/map_${rof_grid_name}_to_${atm_grid_name}_traave.${timestamp}.nc
ncremap -a traave --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap -a traave --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A


map_file_A2R=${maps_root}/map_${atm_grid_name}_to_${rof_grid_name}_trbilin.${timestamp}.nc
map_file_R2A=${maps_root}/map_${rof_grid_name}_to_${atm_grid_name}_trbilin.${timestamp}.nc
ncremap -a trbilin --src_grd=${atm_grid_file} --dst_grd=${rof_grid_file} --map_file=${map_file_A2R}
ncremap -a trbilin --src_grd=${rof_grid_file} --dst_grd=${atm_grid_file} --map_file=${map_file_R2A}
ls -l $map_file_A2R $map_file_R2A



```

--------------------------------------------------------------------------------
# fix topo data - remove shape parameters for EAMxx

```shell
ncks -x -v OC,OA,OL /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne32np4_smoothedx6t_20250904.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne32np4_smoothedx6t_20250904_no-oro-shape.nc
ncks -x -v OC,OA,OL /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne64np4_smoothedx6t_20250904.nc  /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne64np4_smoothedx6t_20250904_no-oro-shape.nc
ncks -x -v OC,OA,OL /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne128np4_smoothedx6t_20250904.nc /global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-topo_ne128np4_smoothedx6t_20250904_no-oro-shape.nc
```

--------------------------------------------------------------------------------
# SPA remap file

```shell
GRID_ROOT=/global/cfs/cdirs/e3sm/whannah/files_grid
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
ncremap --alg_typ=intbilin_se2fv --grd_src=${HOME}/grids/ne30.g  --grd_dst=${GRID_ROOT}/ne32pg2_scrip.nc  --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne32pg2_intbilin_se2fv.20251124.nc
ncremap --alg_typ=intbilin_se2fv --grd_src=${HOME}/grids/ne30.g  --grd_dst=${GRID_ROOT}/ne64pg2_scrip.nc  --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne64pg2_intbilin_se2fv.20251124.nc
ncremap --alg_typ=intbilin_se2fv --grd_src=${HOME}/grids/ne30.g  --grd_dst=${GRID_ROOT}/ne128pg2_scrip.nc --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne128pg2_intbilin_se2fv.20251124.nc

ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne32pg2_intbilin_se2fv.20251124.nc  ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne32pg2_intbilin_se2fv.20251124.nc
ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne64pg2_intbilin_se2fv.20251124.nc  ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne64pg2_intbilin_se2fv.20251124.nc
ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne128pg2_intbilin_se2fv.20251124.nc ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne128pg2_intbilin_se2fv.20251124.nc

ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne32pg2_intbilin_se2fv.20251124.nc
ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne64pg2_intbilin_se2fv.20251124.nc
ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30np4_to_ne128pg2_intbilin_se2fv.20251124.nc

```

```shell
GRID_ROOT=/global/cfs/cdirs/e3sm/whannah/files_grid
DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata
ncremap --alg_typ=traave --grd_src=${HOME}/grids/ne30pg2_scrip.nc  --grd_dst=${GRID_ROOT}/ne32pg2_scrip.nc  --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne32pg2_traave.20251124.nc
ncremap --alg_typ=traave --grd_src=${HOME}/grids/ne30pg2_scrip.nc  --grd_dst=${GRID_ROOT}/ne64pg2_scrip.nc  --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne64pg2_traave.20251124.nc
ncremap --alg_typ=traave --grd_src=${HOME}/grids/ne30pg2_scrip.nc  --grd_dst=${GRID_ROOT}/ne128pg2_scrip.nc --map_fl=${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne128pg2_traave.20251124.nc

ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne32pg2_traave.20251124.nc  ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne32pg2_traave.20251124.nc
ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne64pg2_traave.20251124.nc  ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne64pg2_traave.20251124.nc
ncks -5 -O ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne128pg2_traave.20251124.nc ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne128pg2_traave.20251124.nc

ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne32pg2_traave.20251124.nc
ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne64pg2_traave.20251124.nc
ncdump -k ${DIN_LOC_ROOT}/atm/scream/maps/map_ne30pg2_to_ne128pg2_traave.20251124.nc

```
--------------------------------------------------------------------------------
# copy initial condition files

```shell
cp /global/cfs/cdirs/m4310/whannah/files_init/v3.LR.amip_0101.eam.i.2000-01-01-00000.EAMxx-format.ne32np4.20251001.nc  /global/cfs/cdirs/e3sm/inputdata/atm/scream/init/eamxxi_ne32np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc
cp /global/cfs/cdirs/m4310/whannah/files_init/v3.LR.amip_0101.eam.i.2000-01-01-00000.EAMxx-format.ne64np4.20251001.nc  /global/cfs/cdirs/e3sm/inputdata/atm/scream/init/eamxxi_ne64np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc
cp /global/cfs/cdirs/m4310/whannah/files_init/v3.LR.amip_0101.eam.i.2000-01-01-00000.EAMxx-format.ne128np4.20251001.nc /global/cfs/cdirs/e3sm/inputdata/atm/scream/init/eamxxi_ne128np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc
```



--------------------------------------------------------------------------------

# XML grid definition - cime_config/config_grids.xml

```xml
    <!--=====================================================================-->
    <!-- 2025 SciDAC grids for multi-fidelity study  -->
    <model_grid alias="ne32pg2_r025_RRSwISC6to18E3r5">
      <grid name="atm">ne32np4.pg2</grid>
      <grid name="lnd">r025</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r025</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
    <model_grid alias="ne64pg2_r025_RRSwISC6to18E3r5">
      <grid name="atm">ne64np4.pg2</grid>
      <grid name="lnd">r025</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r025</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
    <model_grid alias="ne128pg2_r025_RRSwISC6to18E3r5">
      <grid name="atm">ne128np4.pg2</grid>
      <grid name="lnd">r025</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r025</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
    <model_grid alias="ne256pg2_r025_RRSwISC6to18E3r5">
      <grid name="atm">ne256np4.pg2</grid>
      <grid name="lnd">r025</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r025</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
    <!--=====================================================================-->
```

# XML domain specification - cime_config/config_grids.xml

```xml

    <!--=====================================================================-->
    <domain name="ne32np4.pg2">
      <nx>24576</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne32pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne32pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <desc>ne32pg2</desc>
    </domain>
    <domain name="ne64np4.pg2">
      <nx>98304</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne64pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne64pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <desc>ne64pg2</desc>
    </domain>
    <domain name="ne128np4.pg2">
      <nx>393216</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne128pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne128pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <desc>ne128pg2</desc>
    </domain>
    <domain name="ne256np4.pg2">
      <nx>1572864</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne256pg2_RRSwISC6to18E3r5.250626.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne256pg2_RRSwISC6to18E3r5.250626.nc</file>
      <desc>ne256pg2</desc>
    </domain>
```

# XML map specification - cime_config/config_grids.xml

```xml
    <!--=====================================================================-->
    <!-- ???  -->
    <!--=====================================================================-->
    <!-- ne32 -->
    <gridmap atm_grid="ne32np4.pg2" ocn_grid="RRSwISC6to18E3r5">
      <map name="ATM2OCN_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_traave.20251006.nc</map>
      <map name="ATM2OCN_VMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="ATM2OCN_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="OCN2ATM_FMAPNAME"          >cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne32pg2_traave.20251006.nc</map>
      <map name="OCN2ATM_SMAPNAME"          >cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne32pg2_traave.20251006.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne32np4.pg2" lnd_grid="r025">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trbilin.20251006.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_r025_to_ne32pg2_traave.20251006.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_r025_to_ne32pg2_traave.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne32np4.pg2" rof_grid="r025">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trbilin.20251006.nc</map>
    </gridmap>
    <!--=====================================================================-->
    <!-- ne64 -->
    <gridmap atm_grid="ne64np4.pg2" ocn_grid="RRSwISC6to18E3r5">
      <map name="ATM2OCN_FMAPNAME">cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_traave.20251006.nc</map>
      <map name="ATM2OCN_VMAPNAME">cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="ATM2OCN_SMAPNAME">cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="OCN2ATM_FMAPNAME">cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne64pg2_traave.20251006.nc</map>
      <map name="OCN2ATM_SMAPNAME">cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne64pg2_traave.20251006.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne64np4.pg2" lnd_grid="r025">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trbilin.20251006.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne64pg2/map_r025_to_ne64pg2_traave.20251006.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne64pg2/map_r025_to_ne64pg2_traave.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne64np4.pg2" rof_grid="r025">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trbilin.20251006.nc</map>
    </gridmap>
    <!--=====================================================================-->
    <!-- ne128 -->
    <gridmap atm_grid="ne128np4.pg2" ocn_grid="RRSwISC6to18E3r5">
      <map name="ATM2OCN_FMAPNAME">cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_traave.20251006.nc</map>
      <map name="ATM2OCN_VMAPNAME">cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="ATM2OCN_SMAPNAME">cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc</map>
      <map name="OCN2ATM_FMAPNAME">cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne128pg2_traave.20251006.nc</map>
      <map name="OCN2ATM_SMAPNAME">cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne128pg2_traave.20251006.nc</map>
      <map name="ATM2ICE_FMAPNAME_NONLINEAR">cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
      <map name="ATM2OCN_FMAPNAME_NONLINEAR">cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne128np4.pg2" lnd_grid="r025">
      <map name="ATM2LND_FMAPNAME"          >cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2LND_FMAPNAME_NONLINEAR">cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2LND_SMAPNAME"          >cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trbilin.20251006.nc</map>
      <map name="LND2ATM_FMAPNAME"          >cpl/gridmaps/ne128pg2/map_r025_to_ne128pg2_traave.20251006.nc</map>
      <map name="LND2ATM_SMAPNAME"          >cpl/gridmaps/ne128pg2/map_r025_to_ne128pg2_traave.20251006.nc</map>
    </gridmap>
    <gridmap atm_grid="ne128np4.pg2" rof_grid="r025">
      <map name="ATM2ROF_FMAPNAME"          >cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_traave.20251006.nc</map>
      <map name="ATM2ROF_FMAPNAME_NONLINEAR">cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trfv2.20251006.nc</map>
      <map name="ATM2ROF_SMAPNAME"          >cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trbilin.20251006.nc</map>
    </gridmap>
    <!--=====================================================================-->

```

## components/eam/bld/config_files/horiz_grid.xml

```xml
<!--=====================================================================-->
<!-- 2025 SciDAC grids for multi-fidelity study  -->
<horiz_grid dyn="se"    hgrid="ne32np4.pg2"  ncol="24576"   csne="128" csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne64np4.pg2"  ncol="98304"   csne="128" csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne128np4.pg2" ncol="393216"  csne="128" csnp="4" npg="2" />
<horiz_grid dyn="se"    hgrid="ne256np4.pg2" ncol="1572864"  csne="256"  csnp="4" npg="2" />
<!--=====================================================================-->
```