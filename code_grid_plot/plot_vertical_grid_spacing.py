import os, numpy as np, xarray as xr, ngl, copy
import hapy_common as hc
import hapy_setres as hs
home = os.getenv('HOME')

vert_file_list,name,clr,dsh = [],[],[],[]

#-------------------------------------------------------------------------------
def add_grid(grid_in,n=None,d=0,c='black'):
   global vert_file_list,name,clr,dsh
   vert_file_list.append(grid_in); name.append(n); dsh.append(d); clr.append(c)
#-------------------------------------------------------------------------------


# add_grid(f'{home}/E3SM/vert_grid_files/L80_for_E3SMv3.nc',    n='L80  (EAM)',   d=0,c='blue')
# add_grid(f'{home}/HICCUP/files_vert/vert_coord_E3SM_L128.nc', n='L128 (EAMxx)', d=0,c='red' )

grid_root = '/global/homes/w/whannah/E3SM_grid_support/2026-INCITE-CONUS-RRM'
# add_grid(f'{grid_root}/2026-INCITE-CONUS-RRM_L128_v1_c20251211.nc',n='L128v1',d=0,c='green')
# add_grid(f'{grid_root}/2026-INCITE-CONUS-RRM_L128_v2_c20251211.nc',n='L128v2',d=0,c='magenta')
# add_grid(f'{grid_root}/2026-INCITE-CONUS-RRM_L128_v3_c20251211.nc',n='L128 v3',d=0,c='cyan')
add_grid(f'{home}/E3SM/vert_grid_files/L80_for_E3SMv3.nc',         n='L80  (EAM)',   d=0,c='blue')
add_grid(f'{home}/HICCUP/files_vert/vert_coord_E3SM_L128.nc',      n='L128 (EAMxx)', d=0,c='red'  )
add_grid(f'{grid_root}/2026-INCITE-CONUS-RRM_L144_v1_c20251211.nc',n='L144 (new)',d=0,c='purple')

#-------------------------------------------------------------------------------
fig_file,fig_type = os.getenv('HOME')+'/E3SM_grid_support/figs_grid_plot/vertical_grid_spacing','png'

print_table     = True
# use_height      = True # for Y-axis, or else use pressure
# add_zoomed_plot = True
add_refine_box  = False

# set limits for second plot zoomed in on lower levels
# zoom_top_idx = -10
zoom_top_idx = -40 # 1km

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wks = ngl.open_wks(fig_type,fig_file)
plot = [None]*4
res = ngl.Resources()
res.vpWidthF = 0.5
res.nglDraw,res.nglFrame         = False,False
res.tmXTOn                       = False
res.tmXBMajorOutwardLengthF      = 0.
# res.tmXBMinorOutwardLengthF      = 0.
res.tmYLMajorOutwardLengthF      = 0.
res.tmYLMinorOutwardLengthF      = 0.
res.tmYLLabelFontHeightF         = 0.015
res.tmXBLabelFontHeightF         = 0.015
res.tiXAxisFontHeightF           = 0.015
res.tiYAxisFontHeightF           = 0.015
res.tmXBMinorOn,res.tmYLMinorOn  = True,False

res.xyLineThicknessF             = 6.

res.xyMarkLineMode = 'MarkLines'
res.xyMarkerSizeF = 0.005
res.xyMarker = 16

# res.xyYStyle = "Log"

#-------------------------------------------------------------------------------
# print stuff
#-------------------------------------------------------------------------------
if print_table:

  print('-'*100)

  mlev_list, zlev_list = [],[]
  for f,vert_file in enumerate(vert_file_list):
    ds = xr.open_dataset(vert_file)
    # mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
    mlev = ds['hyai'].values*1000 + ds['hybi'].values*1000
    zlev = np.log(mlev/1e3) * -6740.
    mlev_list.append(mlev)
    zlev_list.append(zlev)

  max_len = 0
  for mlev in mlev_list: 
    if len(mlev)>max_len: max_len = len(mlev)

  def get_msg(mlev_list,zlev_list,k):
    return f'     {mlev_list[k]:8.2f} mb   {zlev_list[k]:8.1f} m'

  msg_len = len(get_msg(mlev_list[0],zlev_list[0],0))

  for k in range(max_len):
    k2 = max_len-k-1
    msg = f'{k:3}  ({k2:3}) '
    # k2 = max_len-k-1
    # msg = f'{k:3}  ({k2:3})'
    for g in range(len(mlev_list)): 
      # if k < len(mlev_list[g]):
      #   k2 = len(mlev_list[g])-k#-1
      #   msg += f'    ({k2:3})    {mlev_list[g][k]:8.3f} mb  {zlev_list[g][k]:8.3f} m'
      # else:
      #   msg += ' '*(12+4+5)
      if k < len(mlev_list[g]): 
        msg += get_msg(mlev_list[g],zlev_list[g],k)
      else:
        msg += ' '*msg_len
    print(msg)

  print('-'*100)

  # exit()

#-------------------------------------------------------------------------------
# Load data
#-------------------------------------------------------------------------------
z_mid_lev_list = []
z_del_lev_list = []
p_mid_lev_list = []
p_del_lev_list = []

print('vertical grid height/pressure bounds:')

for f,vert_file in enumerate(vert_file_list):

  ds = xr.open_dataset(vert_file)

  mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
  ilev = ds['hyai'].values*1000 + ds['hybi'].values*1000

  # rough estimate of height from pressure
  ilevz = np.log(ilev/1e3) * -6740.
  mlevz = np.log(mlev/1e3) * -6740. / 1e3

  print()
  # hc.print_stat(mlev, name=name[f]+' mlev',stat='nxh',indent='    ',compact=True)
  # hc.print_stat(mlevz,name=name[f]+' zlev',stat='nxh',indent='    ',compact=True)

  label=f'{name[f]} mlev'; print(f'  {label:20}  min/max: {np.min(mlev ):8.2f} / {np.max(mlev ):8.2f}')
  label=f'{name[f]} zlev'; print(f'  {label:20}  min/max: {np.min(mlevz):8.2f} / {np.max(mlevz):8.2f}')

  
  dlevz = mlevz*0.
  for k in range(len(mlev)): dlevz[k] = ilevz[k] - ilevz[k+1]

  z_mid_lev_list.append(mlevz)
  z_del_lev_list.append(dlevz)
  p_mid_lev_list.append(mlev)
  p_del_lev_list.append(dlevz)

  # if use_height:
  #   mlev_list.append(mlevz)
  #   dlev_list.append(dlevz)
  # else:
  #   mlev_list.append(mlev)
  #   dlev_list.append(dlevz)

print('-'*100)

#-------------------------------------------------------------------------------
# Create plot
#-------------------------------------------------------------------------------

z_mid_lev_min = np.min([np.nanmin(d) for d in z_mid_lev_list])
z_mid_lev_max = np.max([np.nanmax(d) for d in z_mid_lev_list])
z_del_lev_min = np.min([np.nanmin(d) for d in z_del_lev_list])
z_del_lev_max = np.max([np.nanmax(d) for d in z_del_lev_list])
p_mid_lev_min = np.min([np.nanmin(d) for d in p_mid_lev_list])
p_mid_lev_max = np.max([np.nanmax(d) for d in p_mid_lev_list])
p_del_lev_min = np.min([np.nanmin(d) for d in p_del_lev_list])
p_del_lev_max = np.max([np.nanmax(d) for d in p_del_lev_list])

# set limits for second plot
z_mid_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in z_mid_lev_list])
z_mid_lev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in z_mid_lev_list])
z_del_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in z_del_lev_list])
z_del_lev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in z_del_lev_list])
p_mid_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in p_mid_lev_list])
p_mid_lev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in p_mid_lev_list])
p_del_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in p_del_lev_list])
p_del_lev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in p_del_lev_list])

#-------------------------------------------------------------------------------
# print()
# print(z_del_lev_list[0])
# print()
# print(z_del_lev_list[0][zoom_top_idx:])
# print()
#-------------------------------------------------------------------------------
print(f'  z_mid_lev_min_2: {z_mid_lev_min_2}')
print(f'  z_mid_lev_max_2: {z_mid_lev_max_2}'); print()
print(f'  z_del_lev_min_2: {z_del_lev_min_2}')
print(f'  z_del_lev_max_2: {z_del_lev_max_2}'); print()
print(f'  p_mid_lev_min_2: {p_mid_lev_min_2}')
print(f'  p_mid_lev_max_2: {p_mid_lev_max_2}'); print()
print(f'  p_del_lev_min_2: {p_del_lev_min_2}')
print(f'  p_del_lev_max_2: {p_del_lev_max_2}'); print()
# exit()
#-------------------------------------------------------------------------------

# dlev_min = np.min([np.nanmin(d) for d in dlev_list])
# dlev_max = np.max([np.nanmax(d) for d in dlev_list])
# mlev_min = np.min([np.nanmin(d) for d in mlev_list])
# mlev_max = np.max([np.nanmax(d) for d in mlev_list])

# # set limits for second plot w/ linear scale
# dlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in dlev_list])
# dlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in dlev_list])
# mlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in mlev_list])
# mlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in mlev_list])

#---------------------------------------------------------------------------------------------------
for f,vert_file in enumerate(vert_file_list):

  # mlev = mlev_list[f]
  # dlev = dlev_list[f]

  # if use_height:
  #   res.tiXAxisString = 'Grid Spacing [m]'
  #   res.tiYAxisString = 'Approx. Height [km]'
  #   res.trYReverse = False
  # else:
  #   res.tiXAxisString = 'Grid Spacing [m]'
  #   res.tiYAxisString = 'Approx. Pressure [hPa]'
  #   res.trYReverse = True

  res.xyDashPattern = dsh[f]
  res.xyLineColor   = clr[f]
  res.xyMarkerColor = clr[f]

  # tres1 = copy.deepcopy(res)
  # tres2 = copy.deepcopy(res)

  # tres1.trXMinF = dlev_min
  # tres1.trXMaxF = dlev_max + (dlev_max-dlev_min)*0.05
  # if use_height:
  #   tres1.trYMinF = mlev_min# - mlev_min/2
  #   tres1.trYMaxF = mlev_max + (mlev_max-mlev_min)*0.05
  # else:
  #   tres1.trYMinF = mlev_min - mlev_min/2
  #   tres1.trYMaxF = 1e3 #mlev_max

  #print('-'*80)
  #print('-'*80)
  #print(f'WARNING - using custom axis bounds')
  #print('-'*80)
  #print('-'*80)
  #tres1.trXMaxF = 1e3
  #tres1.trYMinF = 10
  #-----------------------------------------------------------------------------
  # tres2.trXMinF = 0 # dlev_min_2
  # tres2.trXMaxF = 300#dlev_max_2 + (dlev_max_2-dlev_min_2)*0.05
  # if use_height:
  #   tres2.trYMinF = 0
  #   tres2.trYMaxF = 4
  # else:
  #   tres2.trYMinF = mlev_min_2 #- mlev_min_2/2
  #   tres2.trYMaxF = 1e3 #mlev_max_2

  # temporary override to highlight new grid
  #tres1.trXMaxF = 800
  #tres2.trXMaxF = 100

  # if use_height: 
  #   tres1.xyYStyle = "Linear"
  #   tres2.xyYStyle = "Linear"
  # else:
  #   tres1.xyYStyle = "Log"
  #   tres2.xyYStyle = "Linear"

  # tplot1 = ngl.xy(wks, dlev, mlev, tres1)
  # tplot2 = ngl.xy(wks, dlev, mlev, tres2)

  res.trXMinF = 0
  res.xyYStyle = 'Linear'
  #-----------------------------------------------------------------------------
  res.tiXAxisString = 'Grid Spacing [m]'
  res.tiYAxisString = 'Approx. Height [km]'
  res.trYReverse = False
  tres1,tres2 = copy.deepcopy(res),copy.deepcopy(res)
  tres1.xyYStyle = 'Linear'
  tres1.trYMinF,tres2.trYMinF = 0,0
  tres2.trYMaxF = z_mid_lev_max_2
  # tres2.trXMaxF = 400
  tres2.trXMaxF = z_del_lev_max_2
  tplot1 = ngl.xy(wks, z_del_lev_list[f], z_mid_lev_list[f], tres1)
  tplot2 = ngl.xy(wks, z_del_lev_list[f], z_mid_lev_list[f], tres2)
  #-----------------------------------------------------------------------------
  res.tiXAxisString = 'Grid Spacing [m]'
  res.tiYAxisString = 'Approx. Pressure [hPa]'
  res.trYReverse = True
  tres1,tres2 = copy.deepcopy(res),copy.deepcopy(res)
  tres1.xyYStyle = 'Log'
  tres1.trYMaxF,tres2.trYMaxF = 1e3,1e3
  tres2.trYMinF = p_mid_lev_min_2
  tres2.trXMaxF = p_del_lev_max_2
  tplot3 = ngl.xy(wks, p_del_lev_list[f], p_mid_lev_list[f], tres1)
  tplot4 = ngl.xy(wks, p_del_lev_list[f], p_mid_lev_list[f], tres2)
  #-----------------------------------------------------------------------------
  fhgt = 0.012
  hs.set_subtitles(wks, tplot1, center_string='Vertical Grid Spacing vs Altitude', font_height=fhgt)
  hs.set_subtitles(wks, tplot2, center_string='Vertical Grid Spacing vs Altitude', font_height=fhgt)
  hs.set_subtitles(wks, tplot3, center_string='Vertical Grid Spacing vs Pressure', font_height=fhgt)
  hs.set_subtitles(wks, tplot4, center_string='Vertical Grid Spacing vs Pressure', font_height=fhgt)
  #-----------------------------------------------------------------------------
  # z_mid_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in z_mid_lev_list])
  # z_mid_lev_max_2 = np.max([np.nanmin(d[zoom_top_idx:]) for d in z_mid_lev_list])
  # z_del_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in z_del_lev_list])
  # z_del_lev_max_2 = np.max([np.nanmin(d[zoom_top_idx:]) for d in z_del_lev_list])
  # p_mid_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in p_mid_lev_list])
  # p_mid_lev_max_2 = np.max([np.nanmin(d[zoom_top_idx:]) for d in p_mid_lev_list])
  # p_del_lev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in p_del_lev_list])
  # p_del_lev_max_2 = np.max([np.nanmin(d[zoom_top_idx:]) for d in p_del_lev_list])
  #-----------------------------------------------------------------------------
  if f==0:
    plot[0] = tplot1
    plot[1] = tplot2
    plot[2] = tplot3
    plot[3] = tplot4
  else:
    ngl.overlay(plot[0],tplot1)
    ngl.overlay(plot[1],tplot2)
    ngl.overlay(plot[2],tplot3)
    ngl.overlay(plot[3],tplot4)

#-------------------------------------------------------------------------------
# add lines to visually see how grids line up with first case (i.e. control/default)
#-------------------------------------------------------------------------------
# if len(plot)>1:
#   tres3 = copy.deepcopy(tres2)
#   tres3.xyDashPattern = 1
#   tres3.xyLineColor = 'black'
#   tres3.xyLineThicknessF = 1.
#   mlev = mlev_list[0]
#   for k in range(10):
#     kk = len(mlev)-1-k
#     xx = np.array([ -1e5, 1e5 ])
#     yy = np.array([ mlev[kk], mlev[kk] ])
#     ngl.overlay(plot[1], ngl.xy(wks, xx, yy, tres3) )

#-------------------------------------------------------------------------------
# indicate refinement levels
#-------------------------------------------------------------------------------
# if add_refine_box:
#   pgres = ngl.Resources()
#   pgres.nglDraw                = False
#   pgres.nglFrame               = False
#   pgres.gsLineColor            = 'black'
#   pgres.gsLineThicknessF       = 10.0
#   pgres.gsFillIndex            = 0
#   pgres.gsFillColor            = 'red'
#   pgres.gsFillOpacityF         = 0.3

#   rx1,rx2 = 0,1e6
#   rx = [rx1,rx2,rx2,rx1,rx1]

#   rz1,rz2 = 10e3,45e3
#   if use_height: 
#     rk1,rk2 = rz1,rz2
#   else:
#     rk1,rk2 = rp1,rp2
#   ry = [rk1,rk1,rk2,rk2,rk1]

#   pdum = ngl.add_polygon(wks, plot[0], rx, ry, pgres)

#-------------------------------------------------------------------------------
# Add legend
#-------------------------------------------------------------------------------
lgres = ngl.Resources()
lgres.vpWidthF           = 0.1
lgres.vpHeightF          = 0.13
lgres.lgLabelFontHeightF = 0.012
lgres.lgMonoDashIndex    = True
lgres.lgLineLabelsOn     = False
lgres.lgLineThicknessF   = 20
lgres.lgLabelJust        = 'CenterLeft'
lgres.lgLineColors       = clr[::-1]

for n in range(len(name)): name[n] = ' '+name[n]

lpx, lpy = 0.27, 0.72

# if add_zoomed_plot:
#   lpx, lpy = 0.26, 0.45
#   # lpx, lpy = 0.8, 0.45
# else:
#   lpx, lpy = 0.6, 0.3

pid = ngl.legend_ndc(wks, len(name), name[::-1], lpx, lpy, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pnl_res = ngl.Resources()
pnl_res.nglPanelXWhiteSpacePercent = 5
pnl_res.nglPanelYWhiteSpacePercent = 5

# ngl.panel(wks,plot,[1,len(plot)],pnl_res); ngl.end()
ngl.panel(wks,plot,[2,2],pnl_res); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(f'{home}/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
