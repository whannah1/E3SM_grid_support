import os, subprocess as sp, numpy as np, xarray as xr, dask, copy, string, cmocean, glob, uxarray as ux
import cartopy.crs as ccrs; import matplotlib.pyplot as plt; import matplotlib.colors as mcolors
import hapy
#-------------------------------------------------------------------------------
file_list,name_list = [],[]
def add_file(file,name=None):
   file_list.append(file)
   name_list.append(name)
#-------------------------------------------------------------------------------
var,lev_list,var_str = [],[],[]
htype_list = []
def add_var(var_name,lev=0,s=None,htype=None): 
   var.append(var_name); lev_list.append(lev); 
   if s is None:
      var_str.append(var_name)
   else:
      var_str.append(s)
   htype_list.append(htype)
#-------------------------------------------------------------------------------
fig_file = 'topo-comparison.png'
#-------------------------------------------------------------------------------

# grid_root = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2026-ne30-test/files_grid'
# topo_root1 = '/lcrc/group/e3sm/data/inputdata/atm/cam/topo'
# topo_root2 = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2026-ne30-test/files_topo'

grid_root = '/global/cfs/cdirs/e3sm/whannah/E3SM_grid_support/2026-ne30-test/files_grid'
topo_root1 = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo'
topo_root2 = '/global/cfs/cdirs/e3sm/whannah/E3SM_grid_support/2026-ne30-test/files_topo/'

# scrip_file = f'{grid_root}/ne30np4_scrip.nc'

scrip_file = f'{grid_root}/ne30pg2_scrip.nc'
# add_file(f'{topo_root1}/USGS-gtopo30_ne30np4pg2_x6t-SGH.c20210614.nc',name='default ne30 topo')
add_file(f'{topo_root2}/USGS-topo_ne30-np4_smoothedx6t_20260204-nc.nc',name='bash+NCO SGH workflow')
add_file(f'{topo_root2}/USGS-topo_ne30-np4_smoothedx6t_20260204-py.nc',name='python SGH workflow')

# scrip_file = f'{topo_root2}/../files_grid/ne3000pg1_scrip.nc'
# topo_root1 = f'{topo_root1}/../hrtopo'
# add_file(f'{topo_root1}/USGS-topo-cube3000.nc',  name='ne3000 old')
# add_file(f'{topo_root2}/tmp_USGS-topo_ne3000.nc',name='ne3000 new')

# scrip_file = f'{grid_root}/ne30pg2_scrip.nc'
# add_file(f'{topo_root2}/tmp_USGS-topo_ne30-pg2.nc',name='SRC=>ne30pg2  tmp_USGS-topo_ne30-pg2.nc')
# add_file(f'{topo_root2}/tmp_3km-topo_ne30-pg2.nc',name='3km=>ne30pg2  tmp_3km-topo_ne30-pg2.nc')
# # add_file(f'{topo_root2}/tmp_3km-topo_ne30-pg2.old.nc',name='3km=>ne30pg2  tmp_3km-topo_ne30-pg2.old.nc')

# add_file(f'{topo_root2}/USGS-topo_ne30-np4_smoothedx6t_20260204-nc.nc',name='bash+NCO topo')

#-------------------------------------------------------------------------------

# add_var('PHIS')
add_var('SGH')
add_var('SGH30')

#-------------------------------------------------------------------------------

# plot_diff = False
add_diff  = True

print_stats          = True
var_x_case           = True

# num_plot_col         = 1#len(var)

use_common_label_bar = False

if 'use_snapshot' not in locals(): use_snapshot,ss_t = False,-1

#---------------------------------------------------------------------------------------------------
num_var = len(var)
num_file = len(file_list)
if 'plot_diff' not in locals(): plot_diff = False
if 'add_diff'  not in locals(): add_diff = False
#---------------------------------------------------------------------------------------------------
# set up figure objects
subplot_kwargs = {}
subplot_kwargs['projection'] = ccrs.Robinson(central_longitude=180)
# subplot_kwargs['projection'] = ccrs.PlateCarree(central_longitude=180)
# lat_min, lat_max = -90, -60
# subplot_kwargs['projection'] = ccrs.Orthographic(central_latitude=-85)

fdx,fdy=15,8
if add_diff:
   (d1,d2) = (num_var,num_file+1) if var_x_case else (num_file+1,num_var)
   figsize = (fdx*num_file+1,fdy*num_var) if var_x_case else (fdx*num_var,fdy*num_file+1)
else:
   (d1,d2) = (num_var,num_file) if var_x_case else (num_file,num_var)
   figsize = (fdx*num_file,fdy*num_var) if var_x_case else (fdx*num_var,fdy*num_file)

title_fontsize,lable_fontsize = 16,16

fig, axs = plt.subplots(d1,d2, subplot_kw=subplot_kwargs, figsize=figsize, squeeze=False )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
for v in range(num_var):
   hapy.print_line()
   print(' '*2+'var: '+hapy.tclr.MAGENTA+var[v]+hapy.tclr.END)
   data_list = []
   glb_avg_list = []
   lat_list,lon_list = [],[]
   if 'lev_list' in locals(): lev = lev_list[v]
   for f in range(num_file):
      print(' '*4+'file: '+hapy.tclr.GREEN+file_list[f]+hapy.tclr.END)
      #-------------------------------------------------------------------------
      ds = ux.open_dataset(scrip_file, file_list[f])
      if var[v]=='PHIS' and 'terr' in ds: 
         data = ds['terr']*9.81
      else:
         data = ds[var[v]]
      #-------------------------------------------------------------------------
      # print(); print(data)
      #-------------------------------------------------------------------------
      if print_stats: hapy.print_stat(data,name=var[v],stat='naxsh',indent='    ',compact=True)
      #-------------------------------------------------------------------------
      data_list.append( data )
      #-------------------------------------------------------------------------
      # # save baseline for diff map
      # if plot_diff and f==0: data_baseline = data.copy()
   #----------------------------------------------------------------------------
   # calculate common limits for consistent contour levels
   data_min = np.min([np.nanmin(d) for d in data_list])
   data_max = np.max([np.nanmax(d) for d in data_list])
   if plot_diff or add_diff:
      tmp_data = copy.deepcopy(data_list)
      for f in range(num_file): tmp_data[f] = data_list[f] - data_list[0]
      # diff_data_max = np.max([np.nanmax(d) for d in tmp_data])
      # diff_data_min = np.min([np.nanmin(d) for d in tmp_data])
      diff_data_max = np.max([np.nanmax(np.absolute(d)) for d in tmp_data])
      diff_data_min = -1*diff_data_max
   if plot_diff and not add_diff:
      for f in range(num_file):
         if f>0:
            data_list[f] = data_list[f] - data_list[0]
   if add_diff and not plot_diff:
      diff = copy.deepcopy(data_list[1])
      diff = diff - data_list[0]
      hapy.print_stat(diff,name=f'{var[v]} diff',stat='naxsh',indent='    ',compact=True)
   #----------------------------------------------------------------------------
   # set color bar levels
   clev = None
   # if var[v]=='': clev = np.logspace( -5, -1, num=40)
   # if var[v]=='': clev = np.linspace( 800e2, 1020e2, num=40)
   # if var[v]=='': clev = np.arange(600e2,1040e2+2e2,10e2)
   # if var[v]=='PHIS': clev = np.linspace( 0, 5000e1, num=100)
   #----------------------------------------------------------------------------
   # set color map
   cmap = 'viridis'
   # cmap = cmocean.cm.rain
   #----------------------------------------------------------------------------
   num_file_alt = (num_file+1) if add_diff else num_file
   for f in range(num_file_alt):
      img_kwargs = {}
      img_kwargs['origin'] = 'lower'
      img_kwargs['cmap']   = cmap

      if var[v]=='PHIS': img_kwargs['vmin'],img_kwargs['vmax'] = 0,5000e1

      # if plot_diff and f>0:
      #    img_kwargs['cmap'] = cmocean.cm.balance
      #    img_kwargs['vmin'] = diff_data_min
      #    img_kwargs['vmax'] = diff_data_max
      #    clev = None

      ax = axs[v,f] if var_x_case else axs[f,v]
      ax.coastlines(linewidth=0.2,edgecolor='white')
      ax.set_global()

      if add_diff and f==num_file:
         img_kwargs['cmap'] = cmocean.cm.balance
         # if var[v]=='PHIS': img_kwargs['vmin'],img_kwargs['vmax'] = -1000e1,1000e1
         img_kwargs['vmin'],img_kwargs['vmax'] = diff_data_min,diff_data_max
         clev = None
         ax.set_title('diff',      fontsize=title_fontsize, loc='left')
         ax.set_title(var_str[v],  fontsize=title_fontsize, loc='right')
         raster = diff.to_raster(ax=ax)
      else:
         ax.set_title(name_list[f],fontsize=title_fontsize, loc='left')
         ax.set_title(var_str[v],  fontsize=title_fontsize, loc='right')
         raster = data_list[f].to_raster(ax=ax)

      if clev is not None: img_kwargs['norm'] = mcolors.BoundaryNorm(clev, ncolors=256)
      img = ax.imshow(raster, extent=ax.get_xlim() + ax.get_ylim(), **img_kwargs)

      cbar = fig.colorbar(img, ax=ax, fraction=0.02, orientation='vertical')
      cbar.ax.tick_params(labelsize=lable_fontsize)

#---------------------------------------------------------------------------------------------------
# Finalize plot
# fig.savefig(fig_file, dpi=100, bbox_inches='tight')
fig.savefig(fig_file, dpi=400, bbox_inches='tight')
plt.close(fig)

print(f'\n{fig_file}\n')

#---------------------------------------------------------------------------------------------------
