#!/usr/bin/env python3
import os,subprocess as sp
#-------------------------------------------------------------------------------
home = os.getenv('HOME')
script_root = os.path.realpath(__file__).replace('/submit_jobs.py','')
logs_root = f'{script_root}/logs_slurm'
#-------------------------------------------------------------------------------
def get_env_var(var):
  cmd = f'source {script_root}/set_project.sh>>/dev/null;echo ${var}'
  return sp.run(cmd,shell=True,capture_output=True,text=True,check=True).stdout.replace('\n','')
#-------------------------------------------------------------------------------
proj_root = get_env_var('proj_root')
host = get_env_var('host')
#-------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
#-------------------------------------------------------------------------------
grid_name_list = []
# grid_name_list.append('2026-incite-conus-128x2') # 4 nodes seem to work
grid_name_list.append('2026-incite-conus-1024x2') # num_elem=7908298
# grid_name_list.append('2026-incite-conus-1024x3') # num_elem=13017523 => 1.646 more than x2
# grid_name_list.append('2026-incite-conus-1024x4') # num_elem=33333240 => 4.215 more than x2

#-------------------------------------------------------------------------------
map_args = ''
map_args += f' --create_maps_ocn'
map_args += f' --create_maps_lnd'
#-------------------------------------------------------------------------------
# topo_args = ''
# topo_args += ' --create_grid'
# # topo_args += ' --cttrmp_topo'
# # topo_args += ' --smooth_topo'
# # topo_args += ' --cttsgh_topo'
#-------------------------------------------------------------------------------
topo_args = ''
topo_args += ' --create_grid'
# topo_args += ' --remap_topo'
# topo_args += ' --smooth_topo'
# topo_args += ' --calc_topo_sgh'
# topo_args += ' --force_new_3km_data'
#-------------------------------------------------------------------------------
for grid_name in grid_name_list:
  sbatch_common = f'sbatch'
  sbatch_common += f' --export=ALL,proj_root={proj_root}'
  sbatch_common += f',grid_name={grid_name}'
  sbatch_common += f',grid_name_pg2={grid_name}-pg2'
  # sbatch_common += f',OMP_PROC_BIND=spread,OMP_PLACES=threads'
  sbatch_common += f' --output={logs_root}/%x-%j.slurm.main.out'
  sbatch_common += f' --account=e3sm'
  
  if host=='NERSC':
    sbatch_common += f' --constraint=cpu'
    sbatch_common += f' --qos=regular'
    # sbatch_common += f' --qos=debug'

    # topo_slurm_opts = '--nodes=64 --ntasks-per-node=4 --time=2:00:00' # failed => DUE TO TIME LIMI
    # topo_slurm_opts = '--nodes=64 --ntasks-per-node=1 --time=8:00:00' # failed => forrtl: severe (174): SIGSEGV, segmentation fault occurred
    # topo_slurm_opts = '--nodes=96 --ntasks-per-node=1 --time=2:00:00' # cancelled to test MArk's config below
    topo_slurm_opts = '--nodes=16 --cpus-per-task=8 --time=0:30:00'
    # topo_slurm_opts = '--nodes=16 --cpus-per-task=16 --time=0:30:00'
    # topo_slurm_opts = '--nodes=16 --cpus-per-task=32 --time=0:30:00'
    # topo_slurm_opts = '--nodes=32 --cpus-per-task=32 --time=0:30:00' # Mark thinks this will work for x4
    if grid_name=='2026-incite-conus-1024x2': topo_slurm_opts = '--nodes=16 --cpus-per-task=8 --time=0:30:00'
    if grid_name=='2026-incite-conus-1024x3': topo_slurm_opts = '--nodes=32 --cpus-per-task=8 --time=0:30:00'
    if grid_name=='2026-incite-conus-1024x4': topo_slurm_opts = '--nodes=64 --cpus-per-task=8 --time=0:30:00'
    if 'topo_slurm_opts' not in locals(): topo_slurm_opts = '--nodes=4 --cpus-per-task=8 --time=0:30:00'

  # run_cmd(f'{sbatch_common} --job-name=gen_maps_{grid_name} --time=48:00:00 {home}/E3SM_grid_support/batch_maps.sh {map_args}')
  # run_cmd(f'{sbatch_common} --job-name=gen_domn_{grid_name} --time=6:00:00  {home}/E3SM_grid_support/batch_domain.sh')
  run_cmd(f'{sbatch_common} --job-name=gen_topo_{grid_name} {topo_slurm_opts} {home}/E3SM_grid_support/batch_topo.v2.sh {topo_args}')

#-------------------------------------------------------------------------------
print_line()
# sp.run(['/bin/bash','-i','-c','qjob'],shell=False)
#-------------------------------------------------------------------------------
