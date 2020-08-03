#!/bin/bash
#
#PBS -N Sigma-Test
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
declare -r kSigmaList='0.10 0.11 0.12 0.13 0.14 0.15 0.16 0.17 0.18 0.19 0.20'

declare -r  kCalculationDetailLog='VASP.log'
declare -r  kNodesVaspInfoFile='MachineFile'
declare -r  kSigmaTestResult='SigmaTestResult.data'

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
echo "Sigma   Energy(eV/Ion)" > ${kSigmaTestResult}
for sigma_value in ${kSigmaList}; do 
  mkdir Sigma-${sigma_value} 
  cp POSCAR  Sigma-${sigma_value}
  cp INCAR   Sigma-${sigma_value}
  cp POTCAR  Sigma-${sigma_value}
  cp KPOINTS Sigma-${sigma_value}
  cd Sigma-${sigma_value}
  # Modify the INCAR
  sed " /SIGMA/c\  SIGMA  =  ${sigma_value}\ " INCAR > .incar.tmp
  mv .incar.tmp INCAR
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

  echo "${sigma_value}  ${energy_per_ion}" >> ../${kSigmaTestResult} 
  cd ..
done
column -t ${kSigmaTestResult} > .data.tmp
mv .data.tmp ${kSigmaTestResult}
