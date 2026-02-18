#!/usr/bin/env python3
import os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from swag_util import run_cmd,get_env_var,print_line
#-------------------------------------------------------------------------------
proj_root = os.path.dirname(os.path.realpath(__file__))
logs_root = f'{proj_root}/logs_batch'
#-------------------------------------------------------------------------------
host      = get_env_var(f'{proj_root}/set_project.sh','swag_host')
mail_user = get_env_var(f'{proj_root}/set_project.sh','swag_slurm_mail_user')
mail_type = get_env_var(f'{proj_root}/set_project.sh','swag_slurm_mail_type')
#-------------------------------------------------------------------------------
grid_name_list = []
# grid_name_list.append('ne30')
grid_name_list.append('ne256')
#-------------------------------------------------------------------------------
map_args = ''
map_args += f' --create_maps_ocn'
map_args += f' --create_maps_lnd'
#-------------------------------------------------------------------------------
# topo generation arguments for MBDA workflow
topo_args = ''
topo_args += ' --create_grid'
topo_args += ' --remap_topo'
topo_args += ' --smooth_topo'
# topo_args += ' --calc_topo_sgh'
# topo_args += ' --force_new_3km_data'
# topo_args += ' --python-sgh'
topo_slurm_opts = '--nodes=1 --ntasks-per-node=4 --time=8:00:00'
#-------------------------------------------------------------------------------
for grid_name in grid_name_list:
  sbatch_common = f'sbatch'
  sbatch_common += f' --export=ALL,proj_root={proj_root}'
  sbatch_common += f',grid_name={grid_name}'
  sbatch_common += f',grid_name_pg2={grid_name}pg2'

  sbatch_common += f' --output={logs_root}/%x-%j.slurm.main.out'
  sbatch_common += f' --account=e3sm'
  sbatch_common += f' --mail-user={mail_user}'
  sbatch_common += f' --mail-type={mail_type}'

  if host=='NERSC':
    sbatch_common += f' --constraint=cpu'
    sbatch_common += f' --qos=regular'
    # sbatch_common += f' --qos=debug'

  # run_cmd(f'{sbatch_common} --job-name=gen_maps_{grid_name}   --time=48:00:00   {proj_root}/../batch_maps.sh {map_args}')
  # run_cmd(f'{sbatch_common} --job-name=gen_domain_{grid_name} --time=6:00:00    {proj_root}/../batch_domain.sh')
  run_cmd(f'{sbatch_common} --job-name=gen_topo_{grid_name}   {topo_slurm_opts} {proj_root}/../batch_topo.v2.sh {topo_args}')

  # env_cmd  = ''
  # # env_cmd += f'source {proj_root}/set_project.sh;'
  # env_cmd += f' export proj_root={proj_root};'
  # env_cmd += f' export grid_name={grid_name};'
  # env_cmd += f' export grid_name_pg2={grid_name}pg2;'
  # run_cmd(f'{env_cmd} bash {proj_root}/../batch_topo.v2.sh {topo_args}')

  # ### SGH testing
  # run_cmd(f'{env_cmd} bash {proj_root}/../batch_topo.v2.sh --calc_topo_sgh')
  # run_cmd(f'{env_cmd} bash {proj_root}/../batch_topo.v2.sh --calc_topo_sgh --python-sgh')

'''
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
'''
#-------------------------------------------------------------------------------
print_line()
# sp.run(['/bin/bash','-i','-c','qjob'],shell=False)
#-------------------------------------------------------------------------------
