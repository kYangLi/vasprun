#!/bin/bash
####::SUBMIT_COMMAND::qsub __submit_trg_script__
#PBS -N __task_name__
#PBS -l nodes=__nodes_quantity__:ppn=__cores_per_node__
#PBS -l walltime=__job_walltime__:00:00
#PBS -q __job_queue__
#PBS -j oe

declare -r  PYTHON_EXEC='__python_exec__'
declare -r  VASP_CALC_SCRIPT='__vasp_calc_script__'
declare -r  MPI_MF='__mpi_machinefile__'
declare -r  VASP_EXEC='__vasp_exec__'
declare -ir TASKS_PER_NODE=__tasks_per_node__
declare -ir TOTAL_TASKS=__total_tasks__
declare -ir OPENMP_CORES=__openmp_cores__

# Enter the Calculate Folder
cd ${PBS_O_WORKDIR}
# Copy the Machinefile
uniq ${PBS_NODEFILE} > ${MPI_MF}
# Load module
__prog_module__
# OpenMP cores set
export OMP_NUM_THREADS=${OPENMP_CORES}
# Define the mpirun command
declare -r VR_MPIRUN_COMMAND="mpirun -machinefile ../${MPI_MF} -ppn ${TASKS_PER_NODE} -np ${TOTAL_TASKS} ${VASP_EXEC}"

${PYTHON_EXEC} ${VASP_CALC_SCRIPT} -c "${VR_MPIRUN_COMMAND}"
