#!/bin/bash
#-------------------------------------------------------------------------------
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL
#-------------------------------------------------------------------------------
# v2 is updated to handle very-fine grids with the new MVDA mapping tool and
# the ne12000 source topography dataset
#-------------------------------------------------------------------------------
if [ -z "${proj_root}" ]; then echo -e ${RED}ERROR: proj_root is not defined${NC}; exit ; fi
if [ -z "${grid_name}" ]; then echo -e ${RED}ERROR: grid_name is not defined${NC}; exit ; fi
#-------------------------------------------------------------------------------
create_grid=false; remap_topo=false; smooth_topo=false; calc_topo_sgh=false
force_new_3km_data=false
#-------------------------------------------------------------------------------
for arg in "$@"; do
  case $arg in
    --create_grid)        create_grid=true ;;
    --remap_topo)         remap_topo=true ;;
    --smooth_topo)        smooth_topo=true ;;
    --calc_topo_sgh)      calc_topo_sgh=true ;;
    --force_new_3km_data) force_new_3km_data=true;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done
set -- # Clear current arguments
#-------------------------------------------------------------------------------
# echo
# echo "create_grid: $create_grid"
# echo
# exit
#-------------------------------------------------------------------------------
source ${proj_root}/set_project.sh
#-------------------------------------------------------------------------------
slurm_log_create_grid=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.create_grid.out
slurm_log_remap_topo=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.remap_topo.out
slurm_log_smooth_topo=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.smooth_topo.out
slurm_log_calc_topo_sgh=$slurm_log_root/$SLURM_JOB_NAME-$SLURM_JOB_ID.slurm.calc_topo_sgh.out
#-------------------------------------------------------------------------------
export grid_file_exodus=${grid_root}/${grid_name}.g
export grid_file_np4_scrip="${grid_root}/${grid_name}-np4_scrip.nc"
export grid_file_pg2_scrip="${grid_root}/${grid_name_pg2}_scrip.nc"
export grid_file_3km_exodus="${grid_root}/ne3000.g"
export grid_file_3km_scrip="${grid_root}/ne3000pg1_scrip.nc"
#-------------------------------------------------------------------------------
# Specify topo file names - including temporary files that will be deleted
export topo_file_src=${DIN_LOC_ROOT}/atm/cam/gtopo30data/usgs-rawdata.nc
export topo_file_3km=${topo_root}/tmp_USGS-topo_ne3000.nc
export topo_file_3sq=${topo_root}/tmp_USGS-topo_ne3000-sqr_${grid_name}-np4.nc
export topo_file_1=${topo_root}/tmp_USGS-topo_${grid_name}-np4.nc
export topo_file_2=${topo_root}/tmp_USGS-topo_${grid_name}-np4_smoothedx6t.nc
export topo_file_3=${topo_root}/USGS-topo_${grid_name}-np4_smoothedx6t_${timestamp}.nc
#-------------------------------------------------------------------------------  
# print some useful things
echo --------------------------------------------------------------------------------
echo "   proj_root            = ${proj_root}"
echo "   grid_name            = ${grid_name}"; echo
echo "   create_grid          = ${create_grid}"
echo "   remap_topo           = ${remap_topo}"
echo "   smooth_topo          = ${smooth_topo}"
echo "   calc_topo_sgh        = ${calc_topo_sgh}"
echo "   force_new_3km_data   = ${force_new_3km_data}"; echo
echo "   homme_tool_root      = $homme_tool_root"
echo "   mbda_path            = $mbda_path"; echo
echo "   exodus grid file     = ${grid_file_exodus}"
echo "   np4 scrip grid file  = ${grid_file_np4_scrip}"
echo "   topo_file_src        = $topo_file_src"
echo "   topo_file_3km        = ${topo_file_3km}"
echo "   topo_file_3sq        = ${topo_file_3sq}"
echo "   topo_file_1          = $topo_file_1"
echo "   topo_file_2          = $topo_file_2"
echo "   topo_file_3 (final)  = $topo_file_3"
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
echo "SLURM JOB PARAMETERS"
echo "   Job Name             = $SLURM_JOB_NAME"
echo "   Job ID               = $SLURM_JOB_ID"
echo "   Submit Dir           = $SLURM_SUBMIT_DIR"
echo "   Nodes allocated      = $SLURM_JOB_NODELIST"
echo "   Number of nodes      = $SLURM_NNODES"
echo "   Tasks per node       = $SLURM_NTASKS_PER_NODE"
echo "   Total tasks          = $SLURM_NTASKS"
echo "   Memory per node      = $SLURM_MEM_PER_NODE"
echo "   CPUs per task        = $SLURM_CPUS_PER_TASK"
echo "   Partition            = $SLURM_JOB_PARTITION"
echo --------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if [ ! -f ${grid_file_exodus} ]; then echo -e ${RED}ERROR source grid file does not exist:${NC} ${grid_file_exodus} ; fi
if [ ! -f ${topo_file_src} ];      then echo -e ${RED}ERROR source topo data does not exist:${NC} ${topo_file_src} ; fi
#-------------------------------------------------------------------------------
start=`date +%s` # start timer for entire script
# set -e  # Stop script execution on error
#-------------------------------------------------------------------------------
echo --------------------------------------------------------------------------------
#===============================================================================
#===============================================================================
# Generate GLL SCRIP grid file for target topo grid
chk_file=${grid_file_np4_scrip}
if $create_grid; then
  echo;echo -e "${CYN}Creating np4 grid file with homme_tool${NC} >> ${YLW}${slurm_log_create_grid}${NC}"
  #-----------------------------------------------------------------------------
  bash ${grid_code_root}/batch_topo.v2.create_grid.sh >> $slurm_log_create_grid 2>&1
  #-----------------------------------------------------------------------------
  if [ ! $? -eq 0 ]; then echo;echo -e "${RED}  ERROR - see log file.${NC}"; echo; exit 1; fi
  #-----------------------------------------------------------------------------
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  np4 grid file creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  np4 grid file creation SUCCESSFUL:${NC} ${chk_file}"; fi
else
  echo;echo -e ${CYN}Skipping grid generation${NC}
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  np4 grid file does not exist:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  np4 grid file already exists:${NC} ${chk_file}"; fi
fi
#===============================================================================
#===============================================================================
# Remap to target grid with cube_to_target
chk_file=${topo_file_1}
if $remap_topo; then
  echo;echo -e "${CYN}Remapping topography with mbda${NC} >> ${YLW}${slurm_log_remap_topo}${NC}"
  #-----------------------------------------------------------------------------
  remap_opts=''
  if $force_new_3km_data; then remap_opts="${remap_opts} --force_new_3km_data"; fi
  bash ${grid_code_root}/batch_topo.v2.remap_topo.sh ${remap_opts} >> $slurm_log_remap_topo 2>&1
  #-----------------------------------------------------------------------------
  if [ ! $? -eq 0 ]; then echo;echo -e "${RED}  ERROR - see log file.${NC}"; echo; exit 1; fi
  #-----------------------------------------------------------------------------
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo creation SUCCESSFUL:${NC} ${chk_file}"; fi
else
  echo;echo -e "${CYN}Skipping topo remapping${NC}"
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  remapped topo does not exist:${NC} ${chk_file}"; echo; exit 0; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  remapped topo already exists:${NC} ${chk_file}"; fi
fi
#===============================================================================
#===============================================================================
# Apply Smoothing with homme_tool
chk_file=${topo_file_2}
if $smooth_topo; then
  echo;echo -e "${CYN}Smoothing topography with homme_tool${NC} >> ${YLW}$slurm_log_smooth_topo${NC}"
  #-----------------------------------------------------------------------------
  bash ${grid_code_root}/batch_topo.v2.smooth_topo.sh >> $slurm_log_smooth_topo 2>&1
  #-----------------------------------------------------------------------------
  if [ ! $? -eq 0 ]; then echo;echo -e "${RED}  ERROR - see log file.${NC}"; echo; exit 1; fi
  #-----------------------------------------------------------------------------
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  smoothed topo creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  smoothed topo creation SUCCESSFUL:${NC} ${chk_file}"; fi
else
  echo;echo -e "${CYN}Skipping topography smoothing${NC}"
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  smoothed topo does not exist:${NC} ${chk_file}"; echo; exit 0; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  smoothed topo already exists:${NC} ${chk_file}"; fi
fi
#===============================================================================
#===============================================================================
# Compute SGH
chk_file=${topo_file_3}
if $calc_topo_sgh; then
  echo;echo -e "${CYN}Calculating topography sub-grid std deviation (SGH)${NC} >> ${YLW}$slurm_log_calc_topo_sgh${NC}"
  #-----------------------------------------------------------------------------
  bash ${grid_code_root}/batch_topo.v2.calc_topo_sgh.sh >> $slurm_log_calc_topo_sgh 2>&1
  #-----------------------------------------------------------------------------
  if [ ! $? -eq 0 ]; then echo;echo -e "${RED}  ERROR - see log file.${NC}"; exit 1; fi
  #-----------------------------------------------------------------------------
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  final topo creation FAILED:${NC} ${chk_file}"; echo; exit 1; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  final topo creation SUCCESSFUL:${NC} ${chk_file}"; fi
else
  echo;echo -e "${CYN}Skipping SGH calculation${NC}"
  if [ ! -f ${chk_file} ]; then echo;echo -e "${RED}  final topo does not exist:${NC} ${chk_file}"; echo; exit 0; fi
  if [   -f ${chk_file} ]; then echo;echo -e "${GRN}  final topo already exists:${NC} ${chk_file}"; fi
fi
#-------------------------------------------------------------------------------
#*******************************************************************************
#-------------------------------------------------------------------------------
# list temporary files for manual deletion
echo;echo "The following temporary files will need to be deleted:"
ls -1 ${topo_root}/tmp_USGS-topo_ne${NE_DST}*
echo
#-------------------------------------------------------------------------------
# # Clean up Temporary Files
# rm ${topo_root}/tmp_USGS-topo_ne${NE_DST}*
#-------------------------------------------------------------------------------
# Indicate overall run time for this script
end=`date +%s`
runtime_sc=$(( end - start ))
runtime_mn=$(( runtime_sc/60 ))
runtime_hr=$(( runtime_mn/60 ))
echo -e    ${CYN} overall runtime: ${NC} ${runtime_sc} seconds / ${runtime_mn} minutes / ${runtime_hr} hours
echo
#-------------------------------------------------------------------------------
