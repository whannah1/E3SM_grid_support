#!/usr/bin/env python3
import os,subprocess as sp
#-------------------------------------------------------------------------------
home = os.getenv('HOME')
script_root = os.path.realpath(__file__).replace('/submit_jobs.py','')
logs_root = f'{script_root}/logs_slurm'
proj = sp.run(f'source {script_root}/set_project.sh>>/dev/null;echo $proj',shell=True,capture_output=True,text=True,check=True).stdout
#-------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): print('\n  '+clr.GREEN+cmd+clr.END); os.system(cmd); return
#-------------------------------------------------------------------------------
grid_name_list = []
grid_name_list.append('???')
#-------------------------------------------------------------------------------
for grid_name in grid_name_list:
  sbatch_common = f'sbatch'
  sbatch_common += f' --export=ALL,SCRIPT_DIR={script_root},grid_name={grid_name}'
  sbatch_common += f' --output={logs_root}/%x_%j.slurm.main.out'

  run_cmd(f'{sbatch_common} --job-name={proj}_gen_maps_{grid_name}   {script_root}/{proj}_batch_maps.sh')
  run_cmd(f'{sbatch_common} --job-name={proj}_gen_domain_{grid_name} {script_root}/{proj}_batch_domain.sh')
  run_cmd(f'{sbatch_common} --job-name={proj}_gen_topo_{grid_name}   {script_root}/{proj}_batch_topo.sh')

#-------------------------------------------------------------------------------
print_line()
sp.run(['/bin/bash','-i','-c','qjob'],shell=False)
#-------------------------------------------------------------------------------
