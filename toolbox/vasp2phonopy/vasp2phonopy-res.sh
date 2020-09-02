#!/bin/bash
#

## Check phonopy exec
declare -r PHONOPY="$(echo $(which phonopy 2>/dev/null | tail -1))"
if [ -z "${PHONOPY}" ]; then
  echo "[error] No program point to command 'phonopy'!"
  echo "[tips] Please add phonopy to the 'PATH' ..."
  exit 1
fi

### Calculate the set of force
echo "[do] Calculate the Force set..."
vasprun_list=$(find . -name vasprun.xml | xargs)
${PHONOPY} -f ${vasprun_list}

### Post Process
echo "[do] Plot the phonon band..."
${PHONOPY} -p phonopy.conf
${PHONOPY}-bandplot --xlabel '' \
                    --ylabel 'Frequency (THz)' \
                    --legacy --line -o band.pdf band.yaml
${PHONOPY}-bandplot --gnuplot band.yaml > band.dat