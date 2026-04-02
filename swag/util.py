#!/usr/bin/env python3
"""
swag.util — Shared utilities for SWAG workflow scripts.
"""
import os
import subprocess as sp

# -------------------------------------------------------------------
# terminal color codes
class clr:
    END     = '\033[0m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    BOLD    = '\033[1m'

# -------------------------------------------------------------------
# output helpers
def print_line(width=80):
    print('  ' + '-' * width)

# -------------------------------------------------------------------
# command execution
def run_cmd(cmd: str) -> None:
    """Execute a shell command, printing it first and raising on failure."""
    print(f'\n  {clr.GREEN}{cmd}{clr.END}')
    sp.run(cmd, shell=True, check=True, executable='/bin/bash')

# -------------------------------------------------------------------
# legacy: read env var from a bash config script
def get_env_var(project_config_path, var):
    """Source a bash config script and return the value of an env var.

    Deprecated: use swag_config instead. Kept for backward compatibility
    with projects that haven't yet migrated to project.yaml.
    """
    if not os.path.exists(project_config_path):
        raise FileNotFoundError(f'Configuration script not found: {project_config_path}')
    cmd = f'source {project_config_path} >> /dev/null; echo ${var}'
    result = sp.run(cmd, shell=True, capture_output=True, text=True, check=True)
    value = result.stdout.strip()
    if not value:
        raise ValueError(f"Environment variable '{var}' is empty or not set in {project_config_path}")
    return value
