# v2 is a simplified version of v1, and only shades the approx grid length (no topo viz)
#---------------------------------------------------------------------------------------------------
import os, numpy as np, xarray as xr, ngl, copy, cmocean
import hapy_setres as hs, hapy_common as hc
home = os.getenv('HOME')
#---------------------------------------------------------------------------------------------------
scratch_dir = '/global/cfs/cdirs/e3sm/inputdata'
topo_dir = f'{scratch_dir}/atm/cam/topo'
#---------------------------------------------------------------------------------------------------
grid_file_list = []
grid_name_list = []
clat_list,clon_list = [],[]
slat_list,slon_list = [],[]
xlat_list,xlon_list = [],[]
def add_grid(file,name,clat=0,clon=0,slat=None, slon=None, xlat=None, xlon=None):
  grid_file_list.append(file)
  grid_name_list.append(name)
  clat_list.append(clat); clon_list.append(clon)
  slat_list.append(slat); slon_list.append(slon)
  xlat_list.append(xlat); xlon_list.append(xlon)
#---------------------------------------------------------------------------------------------------

grid_root = '/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/files_grid'
# add_grid(f'{grid_root}/2026-incite-conus-128x2-pg2_scrip.nc','conus-128x2', clat=40,clon=-105)
# add_grid(f'{grid_root}/2026-incite-conus-128x3-pg2_scrip.nc','conus-128x3', clat=40,clon=-105)
# add_grid(f'{grid_root}/2026-incite-conus-128x4-pg2_scrip.nc','conus-128x4', clat=40,clon=-105)
# add_grid(f'{grid_root}/2026-incite-conus-1024x2-pg2_scrip.nc','conus-1024x2', clat=40,clon=360-105)
# add_grid(f'{grid_root}/2026-incite-conus-1024x3-pg2_scrip.nc','conus-1024x3', clat=40,clon=360-105)
add_grid(f'{grid_root}/2026-incite-conus-1024x4-pg2_scrip.nc','conus-1024x4', clat=40,clon=360-105)
num_plot_col = 1


# dx_min,dx_max = 2.0,45.0 # good for ne128 RRM
dx_min,dx_max = 0.2, 6.0 # good for ne1024 RRM

#---------------------------------------------------------------------------------------------------

fig_file,fig_type = f'{home}/E3SM_grid_support/figs_grid_plot/grid.scrip.v2','png'
# fig_file,fig_type = f'figs_grid_plot/grid.scrip.v1','png'

num_grid = len(grid_file_list)


# if num_plot_col not in locals(): num_plot_col = 1
if num_plot_col not in locals(): num_plot_col = num_grid

#---------------------------------------------------------------------------------------------------
# debug section - just print stuff and exit
print()
for f,grid_file in enumerate(grid_file_list):
  ds_grid = xr.open_dataset(grid_file)
  hc.print_stat( ds_grid['grid_area']*1e3, name=f'{grid_name_list[f]:30}', compact=True, indent=' '*2 )
  # print('  area sum = '+str(np.sum(ds_grid['grid_area'].values)) )

#---------------------------------------------------------------------------------------------------
# Set up workstation
wkres = ngl.Resources()
npix = 2048; wkres.wkWidth,wkres.wkHeight=npix,npix # 1024 / 2048 / 4096
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = [None]*num_grid
res = ngl.Resources()
res.nglDraw,res.nglFrame        = False,False
res.tmXTOn                      = False
res.tmYROn                      = False
res.tmXBMajorOutwardLengthF     = 0.
res.tmXBMinorOutwardLengthF     = 0.
res.tmYLMajorOutwardLengthF     = 0.
res.tmYLMinorOutwardLengthF     = 0.
res.tmYLLabelFontHeightF        = 0.015
res.tmXBLabelFontHeightF        = 0.015
res.tmXBMinorOn,res.tmYLMinorOn = False,False
res.tmXBOn,res.tmYLOn           = False,False
res.tiXAxisFontHeightF          = 0.015
res.tiYAxisFontHeightF          = 0.015
# res.tiXAxisString               = ''
# res.tiYAxisString               = ''
res.cnFillOn                    = True
res.cnLinesOn                   = False
res.cnLineLabelsOn              = False
res.cnInfoLabelOn               = False
res.lbOrientation               = 'Horizontal'
res.lbLabelFontHeightF          = 0.008
res.lbLabelBarOn                = True
res.lbTitleString               = 'approx. grid spacing [km]'
res.cnFillMode                  = 'CellFill'
# res.mpGridAndLimbOn             = True
# res.mpOutlineBoundarySets       = 'NoBoundaries'
# res.mpOutlineBoundarySets       = 'GeophysicalAndUSStates'
# res.mpPerimOn                   = False
# res.pmTickMarkDisplayMode       = 'Never'
# res.mpGeophysicalLineColor      = 'white'
# res.mpGeophysicalLineThicknessF = 6
# res.mpDataBaseVersion           = 'MediumRes' # LowRes / MediumRes / HighRes

# res.mpLimitMode     = 'LatLon'
# res.mpMinLatF,res.mpMaxLatF,res.mpMinLonF,res.mpMaxLonF =  0, 60, -150, -45 # CONUS

mres = ngl.Resources()
mres.nglDraw,mres.nglFrame         = False,False
mres.xyMarkLineMode = 'Markers'
mres.xyMarkerColor = 'red'
mres.xyMarkerSizeF = 0.008
#---------------------------------------------------------------------------------------------------
# define function to add subtitles to the top of plot
#---------------------------------------------------------------------------------------------------
def set_subtitles(wks, plot, left_string='', center_string='', right_string='', font_height=0.01):
  ttres         = ngl.Resources()
  ttres.nglDraw = False

  ### Use plot extent to call ngl.text(), otherwise you will see this error:
  ### GKS ERROR NUMBER   51 ISSUED FROM SUBROUTINE GSVP  : --RECTANGLE DEFINITION IS INVALID
  strx = ngl.get_float(plot,'trXMinF')
  stry = ngl.get_float(plot,'trYMinF')
  ttres.txFontHeightF = font_height

  ### Set annotation resources to describe how close text is to be attached to plot
  amres = ngl.Resources()
  if not hasattr(ttres,'amOrthogonalPosF'):
    amres.amOrthogonalPosF = -0.52   # Top of plot plus a little extra to stay off the border
  else:
    amres.amOrthogonalPosF = ttres.amOrthogonalPosF

  ### Add left string
  amres.amJust,amres.amParallelPosF = 'BottomLeft', -0.5   # Left-justified
  tx_id_l   = ngl.text(wks, plot, left_string, strx, stry, ttres)
  anno_id_l = ngl.add_annotation(plot, tx_id_l, amres)
  # Add center string
  amres.amJust,amres.amParallelPosF = 'BottomCenter', 0.0   # Centered
  tx_id_c   = ngl.text(wks, plot, center_string, strx, stry, ttres)
  anno_id_c = ngl.add_annotation(plot, tx_id_c, amres)
  # Add right string
  amres.amJust,amres.amParallelPosF = 'BottomRight', 0.5   # Right-justified
  tx_id_r   = ngl.text(wks, plot, right_string, strx, stry, ttres)
  anno_id_r = ngl.add_annotation(plot, tx_id_r, amres)

  return
#---------------------------------------------------------------------------------------------------
# Load data and create plot
grid_data_list = []
for f in range(num_grid):
  grid_file = grid_file_list[f]
  ds_grid = xr.open_dataset(grid_file)
  #-----------------------------------------------------------------------------  
  re = 6.37122e06  # radius of earth
  approx_grid_length = np.sqrt( ds_grid['grid_area'].values ) * re / 1e3
  grid_data_list.append(approx_grid_length) 
#---------------------------------------------------------------------------------------------------
# determine min/max area for all grids
if 'dx_min' not in locals() and 'dx_max' not in locals():
  dx_min,dx_max = 1e3,0
  for f in range(num_grid):
    dx_min = np.min([dx_min,np.nanmin(grid_data_list[f])])
    dx_max = np.max([dx_max,np.nanmax(grid_data_list[f])])

#---------------------------------------------------------------------------------------------------
print()
print(f' dx_min: {dx_min}')
print(f' dx_max: {dx_max}')
print()
#---------------------------------------------------------------------------------------------------
num_grid_cols = [None]*num_grid
for f in range(num_grid):
  grid_file = grid_file_list[f]
  ds_grid = xr.open_dataset(grid_file)
  topo = grid_data_list[f]
  #-----------------------------------------------------------------------------
  num_grid_cols[f] = len(ds_grid['grid_area'])
  #-----------------------------------------------------------------------------
  # ds_grid['grid_center_lon'] = ds_grid['grid_center_lon'].assign_attrs(units='degrees_east')
  # ds_grid['grid_center_lat'] = ds_grid['grid_center_lat'].assign_attrs(units='degrees_north')
  # ds_grid['grid_corner_lon'] = ds_grid['grid_corner_lon'].assign_attrs(units='degrees_east')
  # ds_grid['grid_corner_lat'] = ds_grid['grid_corner_lat'].assign_attrs(units='degrees_north')
  #-----------------------------------------------------------------------------
  tres = copy.deepcopy(res)  
  tres.sfXArray      = ds_grid['grid_center_lon'].values
  tres.sfYArray      = ds_grid['grid_center_lat'].values
  tres.sfXCellBounds = ds_grid['grid_corner_lon'].values
  tres.sfYCellBounds = ds_grid['grid_corner_lat'].values

  tres.cnFillPalette = np.array( cmocean.cm.curl(np.linspace(0,1,256)) )
  tres.cnLevelSelectionMode = "ExplicitLevels"
  # tres.cnLevels = np.linspace(dx_min,dx_max,num=60)
  tres.cnLevels = np.logspace(np.log10(dx_min),np.log10(dx_max),num=60)

  # tres.mpProjection = 'Robinson'
  tres.mpProjection = 'Orthographic'
  tres.mpCenterLonF = clon_list[f]
  tres.mpCenterLatF = clat_list[f]

  plot[f] = ngl.contour_map(wks, topo, tres)

  #-----------------------------------------------------------------------------
  set_subtitles(wks, plot[f], grid_name_list[f], '', f'# pg2 cells: {num_grid_cols[f]}', font_height=0.015)
  
#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pres = ngl.Resources()
# pres.nglPanelLabelBar = True
# nglPanelLabelBarLabelFontHeightF
# pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
# pres.nglPanelFigureStringsJust        = "TopLeft"
# pres.nglPanelFigureStringsFontHeightF = 0.015
pres.nglPanelYWhiteSpacePercent = 5

layout = [int(np.ceil(len(plot)/float(num_plot_col))),num_plot_col]

ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(os.getenv('HOME')+'/E3SM_grid_support/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
