#!/bin/bash
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
#-------------------------------------------------------------------------------
cd ${homme_tool_root}

nl_file=${homme_tool_root}/input.grd.${grid_name}.nl

rm -f ${nl_file}
cat > ${nl_file} <<EOF
&ctl_nl
ne = 0
mesh_file = "${grid_file_exodus}"
/
&vert_nl    
/
&analysis_nl
tool = 'grid_template_tool'
output_dir = "./"
output_timeunits=1
output_frequency=1
output_varnames1='area','corners','cv_lat','cv_lon'
output_type='netcdf'    
io_stride = 1
/
EOF

cmd="srun -n 4 ${homme_tool_root}/src/tool/homme_tool < ${nl_file}"

echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
chk_file="${homme_tool_root}/ne0np4_tmp1.nc"
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  homme_tool grid file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  homme_tool grid file creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-------------------------------------------------------------------------------
# use python utility for format conversion
cmd="${unified_bin}/python ${e3sm_src_root}/components/homme/test/tool/python/HOMME2SCRIP.py"
cmd="${cmd} --src_file ${homme_tool_root}/ne0np4_tmp1.nc"
cmd="${cmd} --dst_file ${grid_file_np4_scrip}"

echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
# create 3km/ne3000 scrip grid file if it does not exist
if [ ! -f ${grid_file_3km_scrip} ]; then
  #-----------------------------------------------------------------------------
  # first create the exodus file
  cmd="${unified_bin}/GenerateCSMesh --alt --res 4 --file ${grid_file_3km_exodus}"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  # check to make sure grid file was created
  if [ ! -f ${grid_file_3km_exodus} ]; then echo;echo -e "${RED}  grid file creation FAILED:${NC} ${grid_file_3km_exodus}"; echo; exit 1; fi
  #-----------------------------------------------------------------------------
  # convert the format
  cmd="${unified_bin}/ncks -O -5 ${grid_file_3km_exodus} ${grid_file_3km_exodus}"
  echo "  $cmd" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  # now create the pg1 scrip format grid file
  cmd="${unified_bin}/ConvertMeshToSCRIP --in ${grid_file_3km_exodus} --out ${grid_file_3km_scrip}"
  echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
  #-----------------------------------------------------------------------------
  # check to make sure grid file was created
  if [ ! -f ${grid_file_3km_scrip} ]; then echo;echo -e "${RED}  grid file creation FAILED:${NC} ${grid_file_3km_scrip}"; echo; exit 1; fi
  #-----------------------------------------------------------------------------
  # convert the format
  cmd="${unified_bin}/ncks -O -5 ${grid_file_3km_scrip} ${grid_file_3km_scrip}"
  echo "  $cmd" ; echo; eval "$cmd"
else
  echo;echo -e "${CYN}Skipping 3km grid file creation${NC}"
fi
#-------------------------------------------------------------------------------
