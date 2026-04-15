# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

TAOS (Topography for Atmosphere Orchestration System) generates the files needed to support a new atmosphere grid in E3SM: topography data files, component coupler mapping files, and domain files.

## Running Tests

```shell
python -m pytest tests/ -v          # all tests
python -m pytest tests/test_config.py -v    # single file
```

Tests use `unittest.mock.patch` to stub `taos.config._MACHINES_YAML` and filesystem probes — no HPC environment needed.

## Running Workflows

Each project lives under `projects/<year>-<name>/`. Copy `projects/template/` to start a new project, fill in `project.yaml`, then edit `run_workflow.py` to configure which stages to run:

```shell
python run_workflow.py          # submits configured SLURM jobs
```

Individual pipeline stages can also be invoked directly as Python modules (useful for testing or re-running a single stage):

```shell
python -m taos.grid   path/to/project.yaml
python -m taos.topo   path/to/project.yaml --stage all   # or remap|smooth|sgh
python -m taos.maps   path/to/project.yaml --create-maps-ocn --create-maps-lnd
python -m taos.domain path/to/project.yaml
```

Helper scripts in each project directory:

```shell
python check_config.py   # print all resolved config values
python check_paths.py    # color-coded check of which paths exist on disk
python check_grids.py    # color-coded check of grid/topo/map file existence
```

## Building Required Tools

### `homme_tool` (topography smoothing)

```shell
e3sm_src_root=/path/to/e3sm
cd ${e3sm_src_root}
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
mkdir ${e3sm_src_root}/cmake_homme && cd ${e3sm_src_root}/cmake_homme
mach_file=${e3sm_src_root}/components/homme/cmake/machineFiles/pm-cpu.cmake
cmake -C ${mach_file} -DBUILD_HOMME_WITHOUT_PIOLIBRARY=OFF -DPREQX_PLEV=26 ${e3sm_src_root}/components/homme
make -j4 homme_tool
```

### `cube_to_target`

```shell
cd ${e3sm_src_root}/components/eam/tools/topo_tool/cube_to_target
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
make FC=ifort
```

## Architecture

### `taos/` Package

The core Python package. All workflow logic lives here:

- **`config.py`** — `taos_config` class: loads `project.yaml`, merges with `machines.yaml` defaults, validates, and exposes values via dot-notation (`cfg['derived.grid_root']`). Also `taos_config_error`.
- **`grid.py`** — `create_grid()`: runs `homme_tool` + `HOMME2SCRIP.py` + `GenerateVolumetricMesh` + `ConvertMeshToSCRIP` to produce np4 and pg2 SCRIP/MBDA grid files.
- **`topo.py`** — `remap_topo()`, `smooth_topo()`, `calc_topo_sgh()`: the three-stage topography pipeline using MBDA, `homme_tool` smoothing, and SGH variance calculation.
- **`maps.py`** — `create_maps_ocn()`, `create_maps_lnd()`, `create_maps_spa()`: atmosphere↔ocean/land/SPA coupling maps via `ncremap`/TempestRemap.
- **`domain.py`** — `create_domain()`: E3SM domain files via `generate_domain_files_E3SM.py` from the E3SM source tree.
- **`util.py`** — `clr` (terminal colors), `print_line()`, `run_cmd()`, `get_env_var()` (deprecated).
- **`machines.yaml`** — Per-machine path and SLURM defaults (NERSC, LCRC, ALCF, OLCF). Auto-detected by probing known filesystem paths; last match wins.

### `taos_config` Key Details

```python
from taos import taos_config, taos_config_error

cfg = taos_config('path/to/project.yaml')   # or taos_config.from_project_dir(dir)
cfg.validate()                              # raises taos_config_error listing all missing fields
cfg['derived.grid_root']                    # dot-notation; raises KeyError if blank
cfg.get('paths.mbda_path', '')              # dot-notation with default
cfg.to_env_dict()                           # flat dict of legacy bash variable names
```

Merge rule: project.yaml values win over machine defaults only if non-blank (not `None`, `""`, `"UNSET"`, `"YYYYMMDD"`, etc.). Derived paths (`grid_root`, `maps_root`, `topo_root`, `init_root`, `domn_root`) are computed from `grid_data_root + project.name`. Logs go in `<proj_dir>/logs_batch/` and `<proj_dir>/logs_hiccup/`.

### Workflow Pipeline Sequence

1. **Create grid** (`taos.grid`) — np4 GLL and pg2 physics SCRIP/MBDA grid files, plus ne3000 (3km) files for topography processing.
2. **Remap topo** (`taos.topo --stage remap`) — MBDA interpolates high-res RLL source topography to target np4, pg2, and 3km grids.
3. **Smooth topo** (`taos.topo --stage smooth`) — `homme_tool` applies smoothing.
4. **Calc SGH** (`taos.topo --stage sgh`) — subgrid-scale orography variance computed from the 3km intermediate files.
5. **Maps** (`taos.maps`) — atmosphere↔ocean, atmosphere↔land, SPA coupling maps.
6. **Domain** (`taos.domain`) — E3SM domain files.

### Grid Types

- **Uniform cube-sphere** — `ne${NE}` (spectral element, np4), `ne${NE}pg2` (physics grid, 2×2 GLL points)
- **Regionally Refined Mesh (RRM)** — generated with SQuadGen; uses a refinement image or rectangle spec

### Data Formats

- **Exodus II (`.g`)** — native mesh format
- **SCRIP (`.nc`)** — NetCDF used by coupling/remapping tools
- **MBDA (`.nc`, cdf5)** — reduced SCRIP with `lon`, `lat`, `area` only; `ncol` dimension

### Project Directory Layout

```
projects/
  template/          ← copy this to start a new project
    project.yaml     ← all configuration (machine auto-detected)
    run_workflow.py  ← edit to select which stages/grids to run
    check_config.py
    check_paths.py
    check_grids.py
  <year>-<name>/     ← active projects
  archive/           ← completed/old projects (bash-based set_project.sh style)
```

### Other Directories

- **`code_vert_grid/`** — Standalone scripts for vertical (pressure-hybrid) grid generation; not part of the TAOS package.
- **`code_grid_plot/`** — Grid visualization scripts (SCRIP format, vertical spacing).
- **`tests/`** — pytest unit tests for the `taos` package.


## Code style

### Python comment separators
Always separate section dividers from descriptive comments. Use a
dashed line followed by the description on its own line:
```python
#-------------------------------------------------------------------------------
# section description here
```
and make sure section dviders end at column 80
