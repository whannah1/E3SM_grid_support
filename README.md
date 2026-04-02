# Scripted Workflow for Atmosphere Grids (SWAG)

SWAG is a workflow tool to streamline the creation of files needed to support a new atmosphere grid in E3SM. This tool is focsused on producing three types of files needed for any new atmosphere grid in E3SM:

- component coupler mapping files
- domain files
- topography data files

In the past, the process for creating these files was extremely fragmented, with multiple different approaches described across various web pages. The primary motivation for creating this tool was to standardize the methods for creating these files, while also making the whole process more approachable for new E3SM users.

Note that the process for creating each individual file type is handled by a separate tool, or multiple tools, that exist outside this repo. This is an unfortunate reality of E3SM, and other models, that cannot be addressed in any straighforward way. So, in a sense, this tool is merely a convenient orchestrator of other tools.

# How does this tool work?

Each new grid, or set of grids, needs to be associated with a dedicated directory under `projects/`. The template project `projects/template/` can be copied as a starting point.

Due to the nature of how these files are created, there are many values and paths that need to be defined. To handle all this information, each project must contain a `project.yaml` file that can be referenced throughout the workflow. This approach allows a simple, transparent, and centralized place for the user to provide the neccesary information. Additionally, it helps make modularity of the workflow a priority because the YAML file can be used to run any individual piece of the workflow.

[!CAUTION]
The supporting files for a new grid can be very large. The user must ensure that the paths specified for output and intermediate files have adequate disk space.

Each project also includes utility scripts `show_config.py` and `check_paths.py` that can help examine the project parameters and paths.

--------------------------------------------------------------------------------

# Prerequites Steps

There are several things to 

## Build `homme_tool`

```shell
e3sm_src_root=/pscratch/sd/w/whannah/tmp_e3sm_src
cd ${e3sm_src_root}
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
mkdir ${e3sm_src_root}/cmake_homme
cd ${e3sm_src_root}/cmake_homme
mach_file=${e3sm_src_root}/components/homme/cmake/machineFiles/pm-cpu.cmake
cmake -C ${mach_file} -DBUILD_HOMME_WITHOUT_PIOLIBRARY=OFF -DPREQX_PLEV=26 ${e3sm_src_root}/components/homme
make -j4 homme_tool
```

## Build `cube_to_target`

```shell
# build cube_to_target
cd ${e3sm_src_root}/components/eam/tools/topo_tool/cube_to_target
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
make FC=ifort
```

--------------------------------------------------------------------------------

# Grid Generation

## Standard Uniform Cube Sphere

The commands below provide a simple way to generate a standard cube sphere grid for a given number of elements per cube edge (i.e. NE). If these tools are not in your environment, you can find them in the E3SM unified environment.

```shell
GRID_ROOT=???
unified_bin=???
NE=30
${unified_bin}/GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
${unified_bin}/GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
${unified_bin}/ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```

## Regionally Refined Mesh (RRM)

RRM generation is a difficult thing to explain without specific context. So instead of trying explain things I've put some examples below.

### SquadGen Commands for RRM from Refinement Image

Below is an example command I've used for RRM grid generation

```shell # using a image to define refinement region
BASE_RES=128;  REFINE_LVL=4; GRID_NAME=2025-scream-conus-${BASE_RES}x${REFINE_LVL}

SQuadGen --refine_file ${HOME}/E3SM_grid_support/figs_RRM/RRM-png.2025-conus.v1.png --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist ${SDIST} --smooth_iter ${SITER} --lon_ref 260 --lat_ref 40 --output ${GRID_ROOT}/${GRID_NAME}.g ; GenerateVolumetricMesh --in ${GRID_ROOT}/${GRID_NAME}.g     --out ${GRID_ROOT}/${GRID_NAME}-pg2.g --np 2 --uniform ; ConvertMeshToSCRIP     --in ${GRID_ROOT}/${GRID_NAME}-pg2.g --out ${GRID_ROOT}/${GRID_NAME}-pg2_scrip.nc; ls -l ${GRID_ROOT}/${GRID_NAME}*
```

### SquadGen Commands for RRM Using rectangles

```shell
SQuadGen --refine_rect ${RLON1},${RLAT1},${RLON2},${RLAT2},${REFINE_LVL} --lon_ref ${LON_REF} --lat_ref ${LAT_REF} --resolution ${BASE_RES} --refine_level ${REFINE_LVL} --refine_type LOWCONN --smooth_type SPRING --smooth_dist ${SDIST} --smooth_iter ${SITER} --output ${GRID_ROOT}/${GRID_NAME}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/${GRID_NAME}.g     --out ${GRID_ROOT}/${GRID_NAME}-pg2.g --np 2 --uniform
ConvertMeshToSCRIP     --in ${GRID_ROOT}/${GRID_NAME}-pg2.g --out ${GRID_ROOT}/${GRID_NAME}-pg2_scrip.nc
```

--------------------------------------------------------------------------------

# E3SM Source Code Changes Needed to Define a New Atmosphere Grid

## XML grid definition - cime_config/config_grids.xml

```xml
    <model_grid alias="ne128pg2_r025_RRSwISC6to18E3r5">
      <grid name="atm">ne128np4.pg2</grid>
      <grid name="lnd">r025</grid>
      <grid name="ocnice">RRSwISC6to18E3r5</grid>
      <grid name="rof">r025</grid>
      <grid name="glc">null</grid>
      <grid name="wav">null</grid>
      <mask>RRSwISC6to18E3r5</mask>
    </model_grid>
```

## XML domain specification - cime_config/config_grids.xml

```xml
    <domain name="ne128np4.pg2">
      <nx>393216</nx>
      <ny>1</ny>
      <file grid="atm|lnd" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.lnd.ne128pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <file grid="ice|ocn" mask="RRSwISC6to18E3r5">$DIN_LOC_ROOT/share/domains/domain.ocn.ne128pg2_RRSwISC6to18E3r5.20251006.nc</file>
      <desc>ne128pg2</desc>
    </domain>
```

## XML map specification - cime_config/config_grids.xml

```xml
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

## horiz_grid specification => components/eam/bld/config_files/horiz_grid.xml

```xml
<horiz_grid dyn="se"    hgrid="ne128np4.pg2" ncol="393216"  csne="128" csnp="4" npg="2" />
```
