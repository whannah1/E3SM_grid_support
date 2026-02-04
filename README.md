# E3SM_grid_support

This repository is a place for scripts and notes on supporting new grids in E3SM.

# Build Notes

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

# Grid Generation

## Standard Uniform Cube Sphere

The commands below provide a simple way to generate a standard cube sphere grid for a given number of elements per cube edge (i.e. NE). If these tools are not in your environment, you can find them in the E3SM unified environment.

```shell
GRID_ROOT=???
NE=30
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```

## Regionally Refined Mesh (RRM)

(need to flesh this out)