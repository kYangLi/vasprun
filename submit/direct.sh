#!/bin/bash
####::SUBMIT_COMMAND::nohup bash __submit_trg_script__ < /dev/null > %s.out 2>&1 & echo $!
####::KILL_COMMAND::kill -TERM -- -__job_id__
#
declare -r  PYTHON_EXEC='__python_exec__'
declare -r  VASP_CALC_SCRIPT='__vasp_calc_script__'
declare -r  TASK_NAME='__task_name__'
declare -r  MPI_MF='__mpi_machinefile__'
declare -r  VASP_EXEC='__vasp_exec__'
declare -ir TASKS_PER_NODE=__tasks_per_node__
declare -ir TOTAL_TASKS=__total_tasks__
declare -ir OPENMP_CORES=__openmp_cores__

# Load module
__prog_module__
# OpenMP cores set
export OMP_NUM_THREADS=${OPENMP_CORES}
# Define the mpirun command
if [ -s "${MPI_MF}" ]; then
  uniq ${MPI_MF} > ${MPI_MF}.tmp
  mv ${MPI_MF}.tmp ${MPI_MF}
  declare -r VR_MPIRUN_COMMAND="mpirun -machinefile ../${MPI_MF} -ppn ${TASKS_PER_NODE} -np ${TOTAL_TASKS} ${VASP_EXEC}"
else
  declare -r VR_MPIRUN_COMMAND="mpirun -ppn ${TASKS_PER_NODE} -np ${TOTAL_TASKS} ${VASP_EXEC}"
fi 

echo "[calc] Start!!!"
${PYTHON_EXEC} ${VASP_CALC_SCRIPT} -c "${VR_MPIRUN_COMMAND}" > ${TASK_NAME}.out
