
# Grid File Generation

```shell
NE=16

GenerateCSMesh --alt --res ${NE} --file ${grid_root}/ne${NE}.g
GenerateVolumetricMesh --in ${grid_root}/ne${NE}.g --out ${grid_root}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${grid_root}/ne${NE}pg2.g --out ${grid_root}/ne${NE}pg2_scrip.nc

# ncap2 -s 'grid_imask=int(grid_imask)' ${grid_root}/ne${NE}.g           ${grid_root}/ne${NE}_tmp.g
# mv ${grid_root}/ne${NE}_tmp.g           ${grid_root}/ne${NE}.g

ncap2 -s 'grid_imask=int(grid_imask)' ${grid_root}/ne${NE}pg2_scrip.nc ${grid_root}/ne${NE}pg2_scrip_tmp.nc
mv ${grid_root}/ne${NE}pg2_scrip_tmp.nc ${grid_root}/ne${NE}pg2_scrip.nc

```
