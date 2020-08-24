#!/bin/bash
#

## Check phonopy exec
declare -r PHONOPY='$(echo $(which phonopy 2>/dev/null | tail -1))'
if [ -z "${VASPRUN}" ]; then
  echo "[error] No program point to command 'phonopy'!"
  echo "[tips] Please add phonopy to the 'PATH' ..."
  exit 1
fi

### Calculate the set of force
${PHONOPY} -f ${vasprun_list}

### Post Process
${PHONOPY} -p phonopy.conf
${PHONOPY}-bandplot --gnuplot band.yaml > PHONON.dat