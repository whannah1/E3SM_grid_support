#!/bin/bash
#-------------------------------------------------------------------------------
echo; echo -e ${GRN} Setting up environment ${NC}; echo
eval $(${e3sm_src_root}/cime/CIME/Tools/get_case_env)
#-------------------------------------------------------------------------------
cd ${homme_tool_root}
#-------------------------------------------------------------------------------
# Create namelist file for HOMME
nl_file=${homme_tool_root}/input.grd.${grid_name}.nl
rm -f ${nl_file}
cat > ${nl_file} <<EOF
&ctl_nl
mesh_file = "${grid_file_exodus}"
smooth_phis_p2filt = 0
smooth_phis_numcycle = 6 ! v2/v3 uses 12/6 for more/less smoothing
smooth_phis_nudt = 4e-16
hypervis_scaling = 2
se_ftype = 2 ! actually output NPHYS; overloaded use of ftype
/
&vert_nl
/
&analysis_nl
tool = 'topo_pgn_to_smoothed'
infilenames = '${topo_file_1}', '${topo_file_2}'
/
EOF
#-------------------------------------------------------------------------------
# run homme_tool for topography smoothing
cmd="srun -n 8 ${homme_tool_root}/src/tool/homme_tool < ${nl_file}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
chk_file=${topo_file_2}1.nc
if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  smoothed topo creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  smoothed topo creation SUCCESSFUL:${NC} ${chk_file}"; echo; fi
#-------------------------------------------------------------------------------
# rename output file to remove "1.nc" suffix
cmd="mv ${topo_file_2}1.nc ${topo_file_2}"
echo; echo -e "  ${GRN}${cmd}${NC}" ; echo; eval "$cmd"
#-----------------------------------------------------------------------------
# convert to 64-bit data format to avoid problems in next steps
echo;echo -e "${CYN}Converting to 64-bit data format ${NC}"

cmd="${unified_bin}/ncks -5 ${topo_file_2} ${topo_file_2}.tmp"
echo "  $cmd" ; echo; eval "$cmd"

cmd="mv ${topo_file_2}.tmp ${topo_file_2}"
echo "  $cmd" ; echo; eval "$cmd"
#-------------------------------------------------------------------------------
