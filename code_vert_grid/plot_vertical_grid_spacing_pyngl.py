import os, numpy as np, xarray as xr, copy, hapy
import ngl
home = os.getenv('HOME')
#---------------------------------------------------------------------------------------------------
vert_file_list,name,clr,dsh = [],[],[],[]
def add_grid(grid_in,n=None,d=0,c='black'):
    global vert_file_list,name,clr,dsh
    vert_file_list.append(grid_in); name.append(n); dsh.append(d); clr.append(c)
#---------------------------------------------------------------------------------------------------

add_grid(f'{home}/HICCUP/files_vert/L80_for_E3SMv3.nc', n='L80 EAMv3 default',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_20km.nc', n='L55 top~20km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_25km.nc', n='L63 top~25km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_30km.nc', n='L67 top~30km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_35km.nc', n='L70 top~35km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_40km.nc', n='L72 top~40km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_45km.nc', n='L74 top~45km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_50km.nc', n='L76 top~50km',d=0, c='black')
add_grid(f'{home}/E3SM/vert_grid_files/E3SMv3_L80-truncated_55km.nc', n='L78 top~55km',d=0, c='black')

#---------------------------------------------------------------------------------------------------

fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/vertical_grid_spacing'

print_table     = True
use_height      = True # for Y-axis, or else use pressure
add_zoomed_plot = True
add_refine_box  = False

# set limits for second plot zoomed in on lower levels
# zoom_top_idx = -10
zoom_top_idx = -30

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wks = ngl.open_wks(fig_type,fig_file)
plot = []
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

if use_height:
    res.trYReverse = False
else:
    res.trYReverse = True

# res.xyYStyle = "Log"

#-------------------------------------------------------------------------------
# print stuff
#-------------------------------------------------------------------------------
if print_table:

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
                msg += f'     {mlev_list[g][k]:8.2f} mb   {zlev_list[g][k]:8.1f} m'
        print(msg)

    # exit()

#-------------------------------------------------------------------------------
# Load data
#-------------------------------------------------------------------------------
mlev_list = []
dlev_list = []
for f,vert_file in enumerate(vert_file_list):

    ds = xr.open_dataset(vert_file)

    mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
    ilev = ds['hyai'].values*1000 + ds['hybi'].values*1000

    # rough estimate of height from pressure
    ilevz = np.log(ilev/1e3) * -6740.
    mlevz = np.log(mlev/1e3) * -6740. / 1e3

    print()
    hapy.print_stat(mlev, name=name[f]+' mlev',stat='nxh',indent='    ',compact=True)
    hapy.print_stat(mlevz,name=name[f]+' zlev',stat='nxh',indent='    ',compact=True)

    
    dlevz = mlevz*0.
    for k in range(len(mlev)): dlevz[k] = ilevz[k] - ilevz[k+1]

    if use_height:
        mlev_list.append(mlevz)
        dlev_list.append(dlevz)
    else:
        mlev_list.append(mlev)
        dlev_list.append(dlevz)

#-------------------------------------------------------------------------------
# Create plot
#-------------------------------------------------------------------------------
dlev_min = np.min([np.nanmin(d) for d in dlev_list])
dlev_max = np.max([np.nanmax(d) for d in dlev_list])

mlev_min = np.min([np.nanmin(d) for d in mlev_list])
mlev_max = np.max([np.nanmax(d) for d in mlev_list])

# set limits for second plot w/ linear scale
dlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in dlev_list])
dlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in dlev_list])
mlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in mlev_list])
mlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in mlev_list])


for f,vert_file in enumerate(vert_file_list):

    mlev = mlev_list[f]
    dlev = dlev_list[f]

    if use_height:
        res.tiXAxisString = 'Grid Spacing [m]'
        res.tiYAxisString = 'Approx. Height [km]'
    else:
        res.tiXAxisString = 'Grid Spacing [m]'
        res.tiYAxisString = 'Approx. Pressure [hPa]'

    res.xyDashPattern = dsh[f]
    res.xyLineColor = clr[f]
    res.xyMarkerColor = clr[f]

    tres1 = copy.deepcopy(res)
    tres2 = copy.deepcopy(res)

    tres1.trXMinF = dlev_min
    tres1.trXMaxF = dlev_max + (dlev_max-dlev_min)*0.05
    if use_height:
        tres1.trYMinF = mlev_min# - mlev_min/2
        tres1.trYMaxF = mlev_max + (mlev_max-mlev_min)*0.05
    else:
        tres1.trYMinF = mlev_min - mlev_min/2
        tres1.trYMaxF = 1e3 #mlev_max

    #print('-'*80)
    #print('-'*80)
    #print(f'WARNING - using custom axis bounds')
    #print('-'*80)
    #print('-'*80)
    #tres1.trXMaxF = 1e3
    #tres1.trYMinF = 10

    tres2.trXMinF = 0 # dlev_min_2
    tres2.trXMaxF = 100#dlev_max_2 + (dlev_max_2-dlev_min_2)*0.05
    if use_height:
        tres2.trYMinF = 0
        tres2.trYMaxF = 1
    else:
        tres2.trYMinF = mlev_min_2 #- mlev_min_2/2
        tres2.trYMaxF = 1e3 #mlev_max_2

    # temporary override to highlight new grid
    #tres1.trXMaxF = 800
    #tres2.trXMaxF = 100

    if use_height: 
        tres1.xyYStyle = "Linear"
        tres2.xyYStyle = "Linear"
    else:
        tres1.xyYStyle = "Log"
        tres2.xyYStyle = "Linear"

    tplot1 = ngl.xy(wks, dlev, mlev, tres1)
    
    ### add plot zoomed in on lowest levels
    if add_zoomed_plot: 
        tplot2 = ngl.xy(wks, dlev, mlev, tres2)

    if f==0:
        plot.append(tplot1)
        if add_zoomed_plot: plot.append(tplot2)
    else:
        ngl.overlay(plot[0],tplot1)
        # if len(plot)>=2: ngl.overlay(plot[1],tplot2)
        if add_zoomed_plot: ngl.overlay(plot[1],tplot2)

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

if add_zoomed_plot:
    lpx, lpy = 0.26, 0.45
    # lpx, lpy = 0.8, 0.45
else:
    lpx, lpy = 0.6, 0.3

pid = ngl.legend_ndc(wks, len(name), name[::-1], lpx, lpy, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pnl_res = ngl.Resources()
pnl_res.nglPanelXWhiteSpacePercent = 5
pnl_res.nglPanelYWhiteSpacePercent = 5
ngl.panel(wks,plot[0:len(plot)],[1,len(plot)],pnl_res); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(f'{home}/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
