import os, ngl, numpy as np, xarray as xr
#-------------------------------------------------------------------------------
# Create the PNG file necessary for Squadgen - refinment area should be white
# export PYNGL_RANGS=~/.conda/envs/pyn_env/lib/ncarg/database/rangs
#-------------------------------------------------------------------------------

fig_file,fig_type = f'figs_RRM/RRM-png.2025-conus.v1','png'

#-------------------------------------------------------------------------------
wkres = ngl.Resources()
npix = 4096; wkres.wkWidth,wkres.wkHeight=npix,npix
# wkres.wkForegroundColor = [1.,1.,1.]
# wkres.wkBackgroundColor = [1.,1.,1.]#*0

wks = ngl.open_wks(fig_type,fig_file,wkres)

res = ngl.Resources()
res.nglDraw               = False
res.nglFrame              = False
res.tmXTOn                = False
res.tmXBOn                = False
res.tmYLOn                = False
res.tmYROn                = False

res.mpGridAndLimbOn       = False
res.mpPerimOn             = False
res.mpOutlineOn           = False

# res.mpDataBaseVersion = 'MediumRes' # LowRes / MediumRes / HighRes

# res.mpOutlineOn           = True
# res.mpOutlineBoundarySets = 'Geophysical'
# res.mpGeophysicalLineColor  = 'white'

# res.mpOutlineBoundarySets = 'NoBoundaries'
# res.lbLabelBarOn          = False
# res.cnFillPalette         = "gsdtol"
# res.cnFillPalette         = clr
# res.tfPolyDrawOrder = 'PreDraw'

res.mpFillOn              = True
res.mpInlandWaterFillColor= 'black'#'Background'
res.mpOceanFillColor      = 'black'#'Background'
res.mpLandFillColor       = 'black'#'Background'
res.mpOutlineBoundarySets = 'National'
res.mpFillAreaSpecifiers  = ['AllUSStates']
res.mpSpecifiedFillColors = ['white']


# res.mpSpecifiedFillColors = ['green']


#-------------------------------------------------------------------------------

plot = ngl.map(wks,res) 
# plot = ngl.contour_map(wks,data,res)

# overlay black box to hide weird puple region in Flores sea
pgres = ngl.Resources()
pgres.nglDraw,pgres.nglFrame = False,False
pgres.gsFillColor = 'black'
ulx,uly = 100,0
lrx,lry = 135,-15
bx = [ulx,ulx,lrx,lrx,ulx]
by = [uly,lry,lry,uly,uly]
pdum = ngl.add_polygon(wks,plot,bx,by,pgres)
# ngl.overlay(plot, ngl.xy(wks,data,res) 

# ### use pre-draw polygon to fill in white areas near poles
# gsres             = ngl.Resources()
# gsres.gsFillColor = 'black'
# gsres.gsEdgesOn   = False
# py = [ -89.9,  89.9, 89.9,-89.9, -89.9]
# px = [ 360. , 360. ,  0. ,  0. , 360. ]
# ngl.polygon(wks, plot, px, py, gsres)


ngl.draw(plot)
ngl.frame(wks)
ngl.end()

#-------------------------------------------------------------------------------
### crop white space from png file
if os.path.isfile(f'{fig_file}.{fig_type}') :
  cmd = f'convert -trim +repage {fig_file}.{fig_type} {fig_file}.{fig_type}'
  os.system(cmd)
  # subsequent calls help remove gray lines at edge
  os.system(cmd)
  # os.system(cmd) 
else:
  raise FileNotFoundError(f'\n{fig_file}.{fig_type} does not exist?!\n')

print(); print(f'  {fig_file}.{fig_type}'); print()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
   
