#!/bin/bash
#

declare -r PYTHON="$(which python 2>/dev/null)"

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

# echo "[do] Checking completion of benchmark..."
# bash ./prog/check_bm_progress.sh

# echo "[do] Checking completion of server test..."
# bash ./prog/check_st_progress.sh

# read -p 'Press <Enter> to continue the report...'
${PYTHON} ./prog/report_result.py
