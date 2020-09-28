#!/bin/bash
#

for obj in lib/public/*; do
  if [ -d "${obj}" ]; then
    cd ${obj}
    bash ./_CLEAN.sh
    cd ../../..
  fi
done
for obj in lib/private/*; do
  if [ -d "${obj}" ]; then
    cd ${obj}
    bash ./_CLEAN.sh
    cd ../../..
  fi
done
rm vasprun_path.json
rm _BM-KILLJOBS.sh
rm _BM-SIMPLIFY.sh
rm _BM-CLEAN.sh

