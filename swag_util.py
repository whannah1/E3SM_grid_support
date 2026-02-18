import os
import subprocess as sp
#-------------------------------------------------------------------------------
class clr:
    END     = '\033[0m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    BOLD    = '\033[1m'
#-------------------------------------------------------------------------------
def print_line():
    print(' '*2+'-'*80)
#-------------------------------------------------------------------------------
def run_cmd(cmd: str) -> None:
    """Execute a shell command, printing it first and raising on failure."""
    print(f'\n  {clr.GREEN}{cmd}{clr.END}')
    sp.run(cmd, shell=True, check=True, executable='/bin/bash')
#-------------------------------------------------------------------------------
def get_env_var(project_config_path,var):
    if not os.path.exists(project_config_path):
        raise FileNotFoundError(f"Configuration script not found: {project_config_path}")
    cmd = f'source {project_config_path} >> /dev/null; echo ${var}'
    result = sp.run(cmd,shell=True,capture_output=True,text=True,check=True)
    value = result.stdout.strip()
    if not value:
        raise ValueError(f"Environment variable '{var}' is empty or not set in {project_config_path}")
    return value
#-------------------------------------------------------------------------------
