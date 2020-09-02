#!/bin/bash
#

## Check the vasprun 
declare -r VASPRUN="$(echo $(which vasprun 2>/dev/null | tail -1))"
if [ -z "${VASPRUN}" ]; then
  echo "[error] No program point to command 'vasprun'!"
  echo "[tips] Please add vasprun to the 'PATH' ..."
  exit 1
fi

## Check phonopy exec
declare -r PHONOPY="$(echo $(which phonopy 2>/dev/null | tail -1))"
if [ -z "${PHONOPY}" ]; then
  echo "[error] No program point to command 'phonopy'!"
  echo "[tips] Please add phonopy to the 'PATH' ..."
  exit 1
fi

## Create clean job script
cat > _CLEAN.sh << 'EOF'
  rm -r POSCAR-*
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

## Generate the supercell
echo "[do] Generate the suppercell..."
${PHONOPY} -d phonopy.conf

## Calculate each structure
echo "[do] Submit the calculation task..."
vasprun_list=''
for poscar in POSCAR-*; do
  ((task_counter++)) 
  mkdir ${poscar}
  cd ${poscar}
  cp ../${poscar} POSCAR 
  cp ../INCAR INCAR.SSC 
  cp ../KPOINTS KPOINTS.SSC
  ln -s ../POTCAR POTCAR
  cp ../vr.input.json .
  # Submit the Job
  ${VASPRUN}
  cp vr.input.json ../
  cd ..
done 
