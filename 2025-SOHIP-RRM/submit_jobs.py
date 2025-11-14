#!/usr/bin/env python3
import os,subprocess as sp
#-------------------------------------------------------------------------------
home = os.getenv('HOME')
script_root = os.path.realpath(__file__).replace('/submit_jobs.py','')
logs_root = f'{script_root}/logs_slurm'
cmd = f'source {script_root}/set_project.sh>>/dev/null;echo $proj'
proj = sp.run(cmd,shell=True,capture_output=True,text=True,check=True).stdout.replace('\n','')
#-------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
#-------------------------------------------------------------------------------
grid_name_list = []
grid_name_list.append('2025-sohip-256x3-ptgnia-v1')
grid_name_list.append('2025-sohip-256x3-sw-ind-v1')
grid_name_list.append('2025-sohip-256x3-eq-ind-v1')
grid_name_list.append('2025-sohip-256x3-se-pac-v1')
grid_name_list.append('2025-sohip-256x3-sc-pac-v1')
grid_name_list.append('2025-sohip-256x3-sc-ind-v1')
#-------------------------------------------------------------------------------
topo_args = ''
topo_args += ' --create_grid'
topo_args += ' --cttrmp_topo'
topo_args += ' --smooth_topo'
topo_args += ' --cttsgh_topo'
#-------------------------------------------------------------------------------
for grid_name in grid_name_list:
  sbatch_common = f'sbatch'
  sbatch_common += f' --export=ALL,SCRIPT_DIR={script_root},grid_name={grid_name}'
  sbatch_common += f' --output={logs_root}/%x_%j.slurm.main.out'

  # run_cmd(f'{sbatch_common} --job-name=gen_maps_{grid_name} {script_root}/{proj}_batch_maps.sh')
  # run_cmd(f'{sbatch_common} --job-name=gen_domain_{grid_name} {script_root}/{proj}_batch_domain.sh')
  # run_cmd(f'{sbatch_common} --job-name=gen_topo_{grid_name} {script_root}/{proj}_batch_topo.sh {topo_args}')

  # run_cmd(f'{sbatch_common} --job-name=gen_maps_{grid_name}   {script_root}/../batch_maps.sh')
  # run_cmd(f'{sbatch_common} --job-name=gen_domain_{grid_name} {script_root}/../batch_domain.sh')
  run_cmd(f'{sbatch_common} --job-name=gen_topo_{grid_name}   {script_root}/../batch_topo.sh {topo_args}')

#-------------------------------------------------------------------------------
print_line()
sp.run(['/bin/bash','-i','-c','qjob'],shell=False)
#-------------------------------------------------------------------------------
