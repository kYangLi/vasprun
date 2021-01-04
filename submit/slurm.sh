#!/bin/bash
####::SUBMIT_COMMAND::sbatch __submit_trg_script__
####::KILL_COMMAND::scancel __job_id__
#SBATCH --job-name=__task_name__
#SBATCH --partition=__job_queue__
#SBATCH --time=__job_walltime__:00:00 
#SBATCH --nodes=__nodes_quantity__
#SBATCH --ntasks-per-node=__tasks_per_node__
#SBATCH --cpus-per-task=__openmp_cores__
#SBATCH --exclusive

declare -r  PYTHON_EXEC='__python_exec__'
declare -r  VASP_CALC_SCRIPT='__vasp_calc_script__'
declare -r  VASP_EXEC='__vasp_exec__'
declare -ir OPENMP_CORES=__openmp_cores__

# Load module
__prog_module__
# OpenMP cores set
export OMP_NUM_THREADS=${OPENMP_CORES}
# Define the mpirun command
declare -r VR_MPIRUN_COMMAND="srun ${VASP_EXEC}"

${PYTHON_EXEC} ${VASP_CALC_SCRIPT} -c "${VR_MPIRUN_COMMAND}"
