#!/bin/bash
#-------------------------------------------------------------------------------
# proj="2026-ne30-test" # project "name" or tag that will be used for data roo path
proj="2026-workflow-test" # project "name" or tag that will be used for data roo path
export timestamp="20260204" # yyyymmdd - timestamp for all files (just use the date you started)  
#-------------------------------------------------------------------------------
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/../set_machine_paths.sh
source ${SCRIPT_DIR}/../set_project_paths.sh
#-------------------------------------------------------------------------------