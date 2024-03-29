#!/bin/bash
#

declare -r PYTHON="$(which python 2>/dev/null)"
declare -r VASPRUN="$(echo $(which vasprun 2>/dev/null | tail -1))"

if [ -z "${PYTHON}" ]; then
  echo "[error] No program point to command 'python'!"
  echo "[tips] Please add python3 to the 'PATH' ..."
  exit 1
fi

python_version=$(python --version 2>&1 | grep 'Python 3')
if [ -z "${python_version}" ]; then
  echo "[error] Please make sure the command 'python' point to python3."
  exit 1
fi

if [ -z "${VASPRUN}" ]; then
  echo "[error] No program point to command 'vasprun'!"
  echo "[tips] Please add vasprun to the 'PATH' ..."
  exit 1
fi

echo "{\"vasprun\":\"${VASPRUN}\"}" > vasprun_path.json
${PYTHON} ./prog/submit_tests.py
