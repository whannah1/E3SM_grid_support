#!/bin/bash
#-------------------------------------------------------------------------------
# echo;echo -e "${CYN} Calculating SGH30 with MBDA ${NC}"
#-------------------------------------------------------------------------------
# Compute SGH30
#   VAR30:  variance between SRC and cube3000, computed during remap step
#   VAR2:   variance between SRC and target (computed below)
#   SGH30 = sqrt(min(VAR2,VAR30)
# For target grid regions with resolution << 3km, VAR2 will always be less than VAR30
# and we could skip the min() operation
# For target grid regions with resolution >> 3km, we need to reduce the variance
# by using VAR2.  for regions with resolution >= source grid, VAR2=0
#-------------------------------------------------------------------------------
# step 1: get PHIS_smoothed and PHIS (coming from USGS src data)  in the same file
#  ${topo_file_3km_pg2}  # VAR30 computed on cube3000, mapped to target grid
#  ${topo_file_1_pg2}"   # PHIS on target grid
#  ${topo_file_2}"       # has smoothed versions of PHIS and PHIS_d on target grid

# collect  PHIS (smoothed), PHIS and PHIS_squared into tmp file:
cmd="${unified_bin}/ncap2 -O -v -s 'PHIS_smoothed=PHIS' ${topo_file_2} ${topo_root}/tmp-phis.nc"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
cmd="${unified_bin}/ncks -A -v PHIS,PHIS_squared ${topo_file_1_pg2} ${topo_root}/tmp-phis.nc"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"



# computes variance between SRC and PHIS_SMOOTHED on target grid
cmd="${unified_bin}/ncap2 -O -v -s 'VAR2=PHIS_squared+(PHIS_smoothed*PHIS_smoothed)-(2*PHIS_smoothed*PHIS)'  \
      ${topo_root}/tmp-phis.nc  ${topo_root}/tmp-VAR.nc"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"

# collect VAR30 and VAR2 in one file, so we can take the min
cmd="${unified_bin}/ncks -A -v VAR30 ${topo_file_3km_pg2}  ${topo_root}/tmp-VAR.nc"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"

cmd="${unified_bin}/ncap2 -O -v -s 'VAR = VAR30 << VAR2' ${topo_root}/tmp-VAR.nc  ${topo_root}/tmp-MINVAR.nc"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
cmd="${unified_bin}/ncap2 -O -v -s 'SGH30 = sqrt( VAR >> 0)/9.80616'  ${topo_root}/tmp-MINVAR.nc  ${topo_file_3}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"


# Compute SGH
#   SGH is the variance between cube3000 and the target grid
#   Computed from topo derived from cube3000 - so that there is no variance
#   from scales in the target grid topo finer than 3km
#
# H_3 = topo on cube3000
# H3_pg2   =   H_3 mapped to target grid       file:  $topo_file_3km_pg2
# H3SQ_pg2 =  (H_3)^2 mapped to target grid    file:  $topo_file_3km_pg2
# H3_d_pg2 =   H_3 after dycore smoothing      file:  $topo_file_3km_2.nc
# VAR = MPDA((H_3-H3_d_pg2)^2) = H3SQ_pg2 + H3_d_pg2^2  - 2 * H3_d_pg2 * H3_pg2        
# SGH = sqrt(VAR)

ncap2 -O -v -s 'PHIS_smoothed=PHIS' ${topo_file_3km_2} ${topo_root}/tmp-phis.nc
ncks -A -v PHIS,PHIS_squared ${topo_file_3km_pg2} ${topo_root}/tmp-phis.nc
ncap2 -O -v -s 'VAR=PHIS_squared+(PHIS_smoothed*PHIS_smoothed)-(2*PHIS_smoothed*PHIS)'  \
      ${topo_root}/tmp-phis.nc  ${topo_root}/tmp-SGH.nc
ncap2 -A -v -s 'SGH = sqrt( VAR >> 0)/9.80616' \
      ${topo_root}/tmp-SGH.nc  ${topo_file_3}


# add phys grid lat,lon
cmd="${unified_bin}/ncks -A -v lon,lat  ${topo_file_1_pg2} ${topo_file_3}"
echo "  $cmd" ; echo; eval "$cmd"

# np4 grid lat,lon, but first need to rename
cmd="${unified_bin}/ncrename -O  -v lon,lon_d -v lat,lat_d -d ncol,ncol_d  ${topo_file_1} ${topo_root}/tmp-latlon.nc"
echo "  $cmd" ; echo; eval "$cmd"
cmd="${unified_bin}/ncks -A -v lon_d,lat_d ${topo_root}/tmp-latlon.nc  ${topo_file_3}"
echo "  $cmd" ; echo; eval "$cmd"


# add smoothed PHIS and PHIS_d 
cmd="${unified_bin}/ncks -A -v PHIS,PHIS_d ${topo_file_2} ${topo_file_3}"
echo "  $cmd" ; echo; eval "$cmd"

