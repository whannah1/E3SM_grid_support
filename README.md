# Streamlined Workflow for Atmosphere Grids (SWAG)

SWAG is a workflow tool to streamline the creation of files needed to support a new atmosphere grid in E3SM. This tool is focused on producing three types of files needed for any new atmosphere grid in E3SM:

- component coupler mapping files
- domain files
- topography data files

In the past, the process for creating these files was extremely fragmented, with multiple different approaches described across various web pages. The primary motivation for creating this tool was to standardize the methods for creating these files, while also making the whole process more approachable for new E3SM users.

Note that the process for creating each individual file type is handled by a separate tool, or multiple tools, that exist outside this repo. This is an unfortunate reality of E3SM, and other models, that cannot be addressed in any straightforward way. So, in a sense, this tool is merely a convenient orchestrator of other tools.

--------------------------------------------------------------------------------

# How does this tool work?

Each new grid, or set of grids, needs to be associated with a dedicated directory under `projects/`. The template project `projects/template/` can be copied as a starting point.

Due to the nature of how these files are created, there are many values and paths that need to be defined. To handle all this information, each project must contain a `project.yaml` file that can be referenced throughout the workflow. This approach allows a simple, transparent, and centralized place for the user to provide the necessary information. Additionally, it helps make modularity of the workflow a priority because the YAML file can be used to run any individual piece of the workflow.

> [!CAUTION]
> The supporting files for a new grid can be very large. The user must ensure that the paths specified for output and intermediate files have adequate disk space.

Each project also includes utility scripts `show_config.py` and `check_paths.py` that can help examine the project parameters and paths.

## Quick Start Guide

Below is a list of steps to get started on a new SWAG project.

1. Generate the grid files (see [Grid Generation Guidance](#grid-generation-guidance))
2. Verify that other [prerequisites](#prerequite-steps) have been satisfied
3. Copy the template project and give it a descriptive name
4. Edit `project.yaml` to specify the new grids
5. Verify the project configuration by running `show_config.py` and `check_paths.py`
6. Edit `run_workflow.py` to specify which grids and steps will be handled
7. Run `run_workflow.py`

> [!WARNING]
> The batch job parameters in `run_workflow.py` (number of nodes, tasks per node, wall time) are not tuned for any particular machine or grid resolution. Users should expect some trial and error when finding a configuration that works — especially for larger or regionally refined grids where memory and runtime requirements can vary significantly.

--------------------------------------------------------------------------------

# Grid Generation Guidance

This section is meant to provide advice for anyone who is not familiar with the process of generating an atmosphere grid file from scratch.

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

```shell
# using an image to define refinement region
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

# Prerequite Steps

There are several things to consider when starting a new project.

## Verify MBDA Path

MBDA is a relatively new mapping tool that has not been integrated into E3SM unified. Currently it is manually built by the developer (Vijay Mahadevan). Ensure that the machine you are running has a version of MBDA and that the path is correctly specified in the `project.yaml` associated with your project.

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

<!-- ## Build `cube_to_target`

```shell
# build cube_to_target
cd ${e3sm_src_root}/components/eam/tools/topo_tool/cube_to_target
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
make FC=ifort
``` -->

--------------------------------------------------------------------------------

# Handling Multiple Grids

A single project can process multiple grids by adding a `grids:` list to `project.yaml`. Each entry specifies a grid name and optionally overrides any field from the base `grid:` section — fields not listed are inherited from the base. `run_workflow.py` then submits one set of jobs per grid automatically.

```yaml
grid:
  # Shared settings inherited by all grids unless overridden below
  ocn_name: "oEC60to30v3"
  ocn_file:  "/path/to/oEC60to30v3_scrip.nc"
  lnd_name: "r05"
  lnd_file:  "/path/to/r05_scrip.nc"

grids:
  - name: "ne30"
  - name: "ne120"
  - name: "ne256"
    ocn_name: "oRRS18to6v3"       # this resolution uses a finer ocean grid
    ocn_file:  "/path/to/oRRS18to6v3_scrip.nc"
```

If `grids:` is absent the single `grid:` section is used as-is, so existing single-grid projects need no changes.

--------------------------------------------------------------------------------

# Multi-User Collaboration

When multiple users want to work on the same project, but need to write to different paths — for example, iterating on a grid design — a single shared `project.yaml` can accommodate everyone without requiring separate copies of the file.

## Option 1: Environment variable expansion (simplest)

All path values in `project.yaml` support shell-style variable expansion. If your paths follow a predictable per-user pattern you can use `$USER`, `$HOME`, or `$SCRATCH` directly:

```yaml
paths:
  grid_data_root: "/global/cfs/cdirs/e3sm/shared_project/grid_data"  # same for everyone
  e3sm_src_root:  "$SCRATCH/tmp_e3sm_src"                            # expands per user
```

This requires no special configuration — the variables are expanded automatically at load time.

## Option 2: `users:` section (for paths that can't be expressed with env vars)

When users have different path structures that `$USER` or `$SCRATCH` can't express, add a `users:` section keyed by Unix username. Each user's entry overrides only the fields that differ; everything else falls back to the project or machine defaults.

```yaml
project:
  name:      "2026-shared-topo-test"
  timestamp: "20260204"

paths:
  grid_data_root: "/global/cfs/cdirs/e3sm/e3sm_group/shared_topo_test"  # shared output location

users:
  whannah:
    paths:
      e3sm_src_root: "/pscratch/sd/w/whannah/tmp_e3sm_src"
  jdoe:
    paths:
      e3sm_src_root:   "/global/homes/j/jdoe/e3sm"
      homme_tool_root: "/global/homes/j/jdoe/builds/homme"
```

The merge priority is: machine defaults → project `paths:` → `users.<username>` overrides. The `users:` section also accepts a `slurm:` sub-key for overriding SLURM settings per user (e.g., `account`, `mail_user`).

A user with no entry in `users:` simply gets the project and machine defaults — no action required on their part.

--------------------------------------------------------------------------------

# E3SM Source Code Changes Needed to Define a New Atmosphere Grid

After the files to support a new grid are generated, the E3SM source code need to be modified to register this new grid and specify where to find the new files. These files will often end up under the `$DIN_LOC_ROOT` path that is used for all E3SM input data. For experimental grids that are not expected to be reused the files can be staged outside of the standard input data path.

When a new grid is meant to be supported across different machines the user must create a github pull request to update the E3SM master branch, and upload the new files to the server where all other input data is housed. More information on staging new input data files can be found here:
[E3SM Input Data Servers](https://e3sm.atlassian.net/wiki/spaces/ED/pages/707002387/E3SM+Input+Data+Servers)

Below are some examples of how to define a new grid in the E3SM source code.

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
