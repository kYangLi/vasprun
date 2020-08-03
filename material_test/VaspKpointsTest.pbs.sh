#!/bin/bash
#
#PBS -N Kpoints-Test
#PBS -l nodes=1:ppn=24
#PBS -j oe
#
# Author: Liyang@CMT.Tinghua
#
# Date: 2019.2.25
#
# Descripution:
#

######################
### Parametere Set ###
######################
declare -r kVaspPath='/home/apps/vasp544-18u2/vasp_ncl'
declare -r kKpointsList=' 0.006 0.008 0.010 0.012 0.014 0.016 0.018 0.020 0.022 0.024 0.026 0.028 0.030'

declare -r  kCalculationDetailLog='VASP.log'
declare -r  kNodesVaspInfoFile='MachineFile'
declare -r  kKpointsTestResult='KpointsTestResult.data'
declare -r  kKpointsAutoGen='KpAutoGen'

##################################
### Perpare Before Calculation ###
##################################
## Enter the calculate folder
cd ${PBS_O_WORKDIR}

## Get the Nodes's Information
# Copy the machinefile
cp ${PBS_NODEFILE} ${kNodesVaspInfoFile}
# Get the totoal core number you requested.
total_core_number=$(cat ${kNodesVaspInfoFile} | wc -l)

####################
### Kpoints Test ###
####################
### Main Test Process
echo "KpointsSep k_a k_b k_c  Energy(eV/Ion)" > ${kKpointsTestResult}
for kpoints_seperation in ${kKpointsList}; do 
  mkdir Kpoints-${kpoints_seperation} 
  cp POSCAR  Kpoints-${kpoints_seperation}/
  cp INCAR   Kpoints-${kpoints_seperation}/
  cp POTCAR  Kpoints-${kpoints_seperation}/
  cp ${kKpointsAutoGen}.o Kpoints-${kpoints_seperation}/
  cd Kpoints-${kpoints_seperation}
  # Generate the KPOINTS
  ./${kKpointsAutoGen}.o -s ${kpoints_seperation} -f
  # Run vasp
  mpirun -machinefile ../${kNodesVaspInfoFile} \
         -np ${total_core_number} \
         ${kVaspPath} >> ${kCalculationDetailLog}
  # Get the result
  final_toten_energy=$(echo $(grep 'TOTEN' OUTCAR | tail -1) | cut -d ' ' -f 5)
  if [ "${final_toten_energy}" == "" ]; then 
    final_toten_energy=255.
  fi
  ions_number=$(echo $(grep NIONS OUTCAR) | cut -d ' ' -f 12)
  energy_per_ion=$(awk 'BEGIN{printf "%.8f\n",('${final_toten_energy}'/'${ions_number}')}')

  kpoints_number_char=$(sed -n '4p' KPOINTS)
  echo "${kpoints_seperation} ${kpoints_number_char} ${energy_per_ion}" \
        >> ../${kKpointsTestResult} 
  cd ..
done
column -t ${kKpointsTestResult} > .data.tmp
mv .data.tmp ${kKpointsTestResult}
