# 2026 Workflow Testing

```shell
GRID_ROOT=/global/cfs/cdirs/e3sm/whannah/E3SM_grid_support/2026-workflow-test/files_grid
unified_bin=/global/common/software/e3sm/anaconda_envs/e3smu_1_12_0/pm-cpu/conda/envs/e3sm_unified_1.12.0_login/bin

NE=256
${unified_bin}/GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
${unified_bin}/GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
${unified_bin}/ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
```