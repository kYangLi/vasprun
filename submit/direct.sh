#!/bin/bash
#

declare -r PYTHON_EXEC=__python_exec__
declare -r VASP_CALC_SCRIPT=__vasp_calc_script__
declare -r TASK_NAME=__task_name__

echo "[calc] Start!!!"
${PYTHON_EXEC} ${VASP_CALC_SCRIPT} > ${TASK_NAME}.out
