#!/bin/bash
#-------------------------------------------------------------------------------
proj="2026-INCITE-CONUS-RRM"
#-------------------------------------------------------------------------------
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/../set_machine_paths.sh
export grid_data_root=/global/cfs/cdirs/e3sm
source ${SCRIPT_DIR}/../set_project_paths.sh
#-------------------------------------------------------------------------------