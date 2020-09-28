
#!/bin/bash
#
# This script alias on the default folder name, such as 'RESULT',"
#   '1-RELAX', etc. Pls do not change them in the server test."

if [ ! -d 'calc' ]; then
  echo '[info] Directory "calc" not found...'
  exit 1
fi

for obj_dir in calc/*; do 
  if [ ! -d ${obj_dir} ]; then
    continue
  fi 
  echo "[sub-do] Check ${obj_dir}..."
  for calc_dir in 1-RELAX 2-SSC 3-BAND 4-DOS; do
    abs_calc_dir="${obj_dir}/${calc_dir}"
    if [ -d ${abs_calc_dir} ]; then 
      check_finished=$(grep 'Total CPU time used' ${abs_calc_dir}/OUTCAR)
      if [ -z "${check_finished}" ]; then 
        printf " |--[info] %-11s <-- Not Finish...\n" ${calc_dir}
      else
        printf " |--[info] %-11s === Finished!\n" ${calc_dir}
      fi 
    else
      printf " |--[info] %-11s <xx Not Found...\n" ${calc_dir}
    fi 
  done
  # result.json
  if [ -s "${obj_dir}/RESULT/result.json" ]; then 
    printf " |--[info] %-11s === Valid!\n" 'result.json'
  else
    printf " |--[info] %-11s <xx Invalid...\n" 'result.json'
  fi 
  # band
  if [ -s "${obj_dir}/RESULT/band/BAND_GAP" ] && \
      [ -s "${obj_dir}/RESULT/band/band.json" ]; then 
    printf " |--[info] %-11s === Valid!\n" 'band'
  else
    printf " |--[info] %-11s <xx Invalid...\n" 'band'
  fi 
  # dos 
  if [ -s "${obj_dir}/RESULT/dos/dos.json" ]; then 
    printf " +--[info] %-11s === Valid!\n" 'dos'
  else
    printf " +--[info] %-11s <xx Invalid...\n" 'dos'
  fi
done 
