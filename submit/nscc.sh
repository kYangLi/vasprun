#!/bin/bash
#SBATCH -J __task_name__
#SBATCH -N __nodes_quantity__
#SBATCH -n __total_cores__

declare -r PYTHON_EXEC=__python_exec__
declare -r VASP_CALC_SCRIPT=__vasp_calc_script__

${PYTHON_EXEC} ${VASP_CALC_SCRIPT}
