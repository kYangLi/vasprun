#!/bin/bash
#
#PBS -N phonopy
#PBS -l nodes=4:ppn=24
#PBS -l walltime=48:00:00
#PBS -j oe

cd ${PBS_O_WORKDIR}

declare -r PHONOPY_EXEC='/home/liyang1/Software/Anaconda3/envs/phonopy/bin/phonopy'
declare -r VASP_EXEC='/home/apps/vasp544-18u2/vasp_ncl'
declare -r INTEL_MODULE='module load intel/18.2.199'
declare -r MPI_MACHINE_FILE='MachineFile'
declare -r VASP_LOG='VASP.log'

cat > _CLEAN.sh << 'EOF'
  rm -r SSC.POSCAR-*
  rm    SPOSCAR
  rm    POSCAR-*
  rm    *.yaml
  rm    *.o*
  rm    PHONON.dat
  rm    MachineFile
  rm    FORCE_SETS
  rm    _CLEAN.sh
EOF
chmod 740 _CLEAN.sh

### Prepare for calculation
# Load the Intel Lib
${INTEL_MODULE}
# Copy the Machinefile
cp ${PBS_NODEFILE} ${MPI_MACHINE_FILE}
# Calc. the Total Cores Number
cores_number=$(cat ${MPI_MACHINE_FILE} | wc -l)

### Generate the supercell
${PHONOPY_EXEC} -d phonopy.conf

### Calculate the elestr
vasprun_list=''
for poscar in POSCAR-*; do
  ((task_counter++)) 
  mkdir SSC.${poscar}
  cd SSC.${poscar}
  cp ../${poscar} POSCAR 
  cp ../INCAR . 
  cp ../KPOINTS .
  cp ../POTCAR . 
  # Submit the Job
  mpirun -machinefile ../${MPI_MACHINE_FILE} \
         -np ${cores_number} ${VASP_EXEC} >> ${VASP_LOG}
  rm POTCAR 
  ln -s ../POTCAR .
  vasprun_list="${vasprun_list}  SSC.${poscar}/vasprun.xml"
  cd ..
done 

### Calculate the set of force
${PHONOPY_EXEC} -f ${vasprun_list}

### Post Process
${PHONOPY_EXEC} -p phonopy.conf
${PHONOPY_EXEC}-bandplot --gnuplot band.yaml > PHONON.dat


