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
fig_file = 'map-comparison.png'
#-------------------------------------------------------------------------------


scrip_file_np4='/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2026-ne30-test/files_grid/ne30np4_scrip.nc'
scrip_file_pg2='/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2026-ne30-test/files_grid/ne30pg2_scrip.nc'

topo_root1 = '/lcrc/group/e3sm/data/inputdata/atm/cam/topo'
topo_root2 = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/E3SM_grid_support/2026-ne30-test/files_topo'

add_file(f'{topo_root1}/USGS-gtopo30_ne30np4pg2_x6t-SGH.c20210614.nc',name='default topo')
add_file(f'{topo_root2}/USGS-topo_ne30-np4_smoothedx6t_20260204-nc.nc',name='bash+NCO topo')
# add_file(f'{topo_root2}/USGS-topo_ne30-np4_smoothedx6t_20260204-py.nc',name='python topo')

#-------------------------------------------------------------------------------

# add_var('PHIS')
add_var('SGH')
add_var('SGH30')


#-------------------------------------------------------------------------------

plot_diff = False
# add_diff  = False

print_stats          = True
var_x_case           = True

num_plot_col         = 1#len(var)

use_common_label_bar = False

if 'use_snapshot' not in locals(): use_snapshot,ss_t = False,-1

#---------------------------------------------------------------------------------------------------
# Set up plot resources
num_var = len(var)
num_file = len(file_list)

if 'subtitle_font_height' not in locals(): subtitle_font_height = 0.01

#---------------------------------------------------------------------------------------------------
# set up figure objects
subplot_kwargs = {}
subplot_kwargs['projection'] = ccrs.Robinson(central_longitude=180)
# subplot_kwargs['projection'] = ccrs.PlateCarree(central_longitude=180)
# lat_min, lat_max = -90, -60
# subplot_kwargs['projection'] = ccrs.Orthographic(central_latitude=-85)
(d1,d2) = (num_var,num_file) if var_x_case else (num_file,num_var)
# dx=10;figsize = (dx*num_var,dx*num_file) if var_x_case else (dx*num_file,dx*num_var)

fdx,fdy=15,10;figsize = (fdx*num_file,fdy*num_var) if var_x_case else (fdx*num_var,fdy*num_file)
title_fontsize,lable_fontsize = 20,18

# figsize = (30,30); title_fontsize,lable_fontsize = 25,15

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
      ds = ux.open_mfdataset(scrip_file_pg2, file_list[f], data_vars='minimal')
      data = ds[var[v]]
      #-------------------------------------------------------------------------
      # print(); print(data)
      #-------------------------------------------------------------------------
      if print_stats: hapy.print_stat(data,name=var[v],stat='naxsh',indent='    ',compact=True)
      #-------------------------------------------------------------------------
      data_list.append( data )
      #-------------------------------------------------------------------------
      # save baseline for diff map
      if plot_diff and f==0: data_baseline = data.copy()
   #----------------------------------------------------------------------------
   # calculate common limits for consistent contour levels
   data_min = np.min([np.nanmin(d) for d in data_list])
   data_max = np.max([np.nanmax(d) for d in data_list])
   if plot_diff:
      tmp_data = copy.deepcopy(data_list)
      for f in range(num_file): tmp_data[f] = data_list[f] - data_list[0]
      # diff_data_max = np.max([np.nanmax(d) for d in tmp_data])
      # diff_data_min = np.min([np.nanmin(d) for d in tmp_data])
      diff_data_max = np.max([np.nanmax(np.absolute(d)) for d in tmp_data])
      diff_data_min = -1*diff_data_max
      for f in range(num_file):
         if f>0:
            data_list[f] = data_list[f] - data_list[0]
   #----------------------------------------------------------------------------
   # set color bar levels
   clev = None
   # if var[v]=='': clev = np.logspace( -5, -1, num=40)
   # if var[v]=='': clev = np.linspace( 800e2, 1020e2, num=40)
   # if var[v]=='': clev = np.arange(600e2,1040e2+2e2,10e2)
   #----------------------------------------------------------------------------
   # set color map
   cmap = 'viridis'
   # cmap = cmocean.cm.rain
   #----------------------------------------------------------------------------
   for f in range(num_file):
      img_kwargs = {}
      img_kwargs['origin'] = 'lower'
      img_kwargs['cmap']   = cmap
      if plot_diff and f>0:
         img_kwargs['cmap'] = cmocean.cm.balance
         img_kwargs['vmin'] = diff_data_min
         img_kwargs['vmax'] = diff_data_max
         clev = None

      if clev is not None: img_kwargs['norm'] = mcolors.BoundaryNorm(clev, ncolors=256)

      ax = axs[v,f] if var_x_case else axs[f,v]
      ax.coastlines(linewidth=0.2,edgecolor='white')
      ax.set_title(name_list[f],fontsize=title_fontsize, loc='left')
      ax.set_title(var_str[v],  fontsize=title_fontsize, loc='right')
      ax.set_global()

      img = ax.imshow(data_list[f].to_raster(ax=ax), extent=ax.get_xlim() + ax.get_ylim(), **img_kwargs)

      cbar = fig.colorbar(img, ax=ax, fraction=0.02, orientation='vertical')
      cbar.ax.tick_params(labelsize=lable_fontsize)

#---------------------------------------------------------------------------------------------------
# Finalize plot
fig.savefig(fig_file, dpi=100, bbox_inches='tight')
plt.close(fig)

print(f'\n{fig_file}\n')

#---------------------------------------------------------------------------------------------------
