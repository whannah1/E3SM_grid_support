import xarray as xr, numpy as np
#-------------------------------------------------------------------------------

src_file = '/global/homes/w/whannah/HICCUP/files_vert/L80_for_E3SMv3.nc'

# z_top = 20e3
# z_top = 25e3
# z_top = 30e3
# z_top = 35e3
# z_top = 40e3
# z_top = 45e3
# z_top = 50e3
z_top = 55e3
# z_top = 60e3

dst_root = '/global/homes/w/whannah/E3SM/vert_grid_files'
dst_file = f'{dst_root}/E3SMv3_L80-truncated_{int(z_top/1e3)}km.nc'

#-------------------------------------------------------------------------------

ds = xr.open_dataset(src_file)

# rough estimate of height from pressure
zint = np.log(ds['ilev']/1e3) * -6740.
zmid = np.log(ds[ 'lev']/1e3) * -6740.

nlev = len(zmid)

k_top = None
for k in reversed(range(nlev)):
    if zmid[k] >= z_top:
        k_top = k
        break

nlev_dst = nlev - k_top

# for k in range(nlev):
#     print(f'  {k:4}  {zint[k].values:12.1f}  {zmid[k].values:12.1f}')

#-------------------------------------------------------------------------------
print()
print('-'*80)
print(f'src_file        = {src_file}')
print(f'dst_file        = {dst_file}'); print()
print(f'nlev src        = {nlev}')
print(f'nlev dst        = {nlev_dst}'); print()
print(f'z_top           = {z_top}')
print(f'k_top_dst       = {k_top}'); print()
print(f'zint_max_src    = {zint.max().values}')
print(f'zint_max_dst    = {zint.isel(ilev=k_top).values}')
print('-'*80)
print()
#-------------------------------------------------------------------------------

# find 1 mb level in source grid
k_sponge = None
for k in range(nlev):
    if ds.lev[k] >= 1: k_sponge = k ; break

print()
print('src sponge layer start')
print(f'k_sponge           : {k_sponge}')
print(f'sponge bot zmid    : {zmid.isel(lev=k_sponge).values/1e3} km')
print(f'sponge bot pmid    : {ds.lev.isel(lev=k_sponge).values} mb')
print(f'sponge z thickness : {(zmid.max()-zmid.isel(lev=k_sponge)).values/1e3} km')

#-------------------------------------------------------------------------------

# zint = zint.isel(ilev=slice(k_top,nlev+1))
# zmid = zmid.isel( lev=slice(k_top,nlev))
# nlev = len(zmid)
# for k in range(nlev):
#     print(f'  {k:4}  {zint[k].values:12.1f}  {zmid[k].values:12.1f}')

#-------------------------------------------------------------------------------

ds = ds.isel( ilev=slice(k_top,nlev+1), lev=slice(k_top,nlev) )

zint_new = np.log(ds['ilev']/1e3) * -6740.
zmid_new = np.log(ds[ 'lev']/1e3) * -6740.

# print()
# print(ds)
# print()

#-------------------------------------------------------------------------------
# find k that is 15 down from new top
k_sponge = None
for k in range(nlev):
    if (zmid_new.max()-zmid_new[k]) >= 15e3: k_sponge = k ; break

print()
print('dst sponge layer start')
print(f'k_sponge           : {k_sponge}')
print(f'sponge bot zmid    : {zmid.isel(lev=k_sponge).values/1e3} km')
print(f'sponge bot pmid    : {ds.lev.isel(lev=k_sponge).values} mb')
print(f'sponge z thickness : {(zmid.max()-zmid.isel(lev=k_sponge)).values/1e3} km')
# print(f'dst: {zmid}')
print()
exit()
#-------------------------------------------------------------------------------

ds.to_netcdf(dst_file)
print(f'\n{dst_file}\n')

#-------------------------------------------------------------------------------