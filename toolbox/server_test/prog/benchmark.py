# Author: liyang@cmt.tsinghua
# Date: 2020.8.4
# Descripution: Server test benchmark code base on vasprun.

import os 
import sys
import json
import time 
import socket

def env_check():
  if not os.path.isfile('vasprun_path.json'):
    print("[error] 'vasprun_path.json' file not found...")
    sys.exit(1)
  if (not os.path.isdir('lib/public')) or \
     (not os.path.isdir('lib/private')):
    print("[error] Calculation lib not found...")
    sys.exit(1)
  if not os.path.isfile('vr.input.bm.json'):
    print("[error] No vr.input.bm.json was found under current dir. ...")
    sys.exit(1)
  return 0


def get_lib_objs():
  public_lib = 'lib/public'
  private_lib = 'lib/private'
  public_obj_list = os.listdir(public_lib)
  private_obj_list = os.listdir(private_lib)
  lib_obj_list = []
  for public_obj in public_obj_list:
    obj = os.path.join(public_lib, public_obj)
    if os.path.isdir(obj):
      lib_obj_list.append(obj)
  for private_obj in private_obj_list:
    obj = os.path.join(private_lib, private_obj)
    if os.path.isdir(obj):
      lib_obj_list.append(obj)
  return lib_obj_list


def paras_read_and_write(lib_obj_list):
  # Read in test parameters
  with open('vr.input.bm.json') as jfrp:
    env_para_list = json.load(jfrp)
  # Report the machine hostname
  env_para_list["hostname"] = socket.gethostname()
  with open('vr.input.bm.json', 'w') as jfwp:
    json.dump(env_para_list, jfwp, indent=2)
  # Define the env list
  env_para_name_list = ["prog_module", "vasp_exec", "vaspkit",
                        "sys_type", "cores_per_node", "job_queue"]
  for env_para_name in env_para_name_list:
    print("[para] Set %-14s   ::   %s"
          %(env_para_name, str(env_para_list[env_para_name])))
  print("[info] Exit this script to modify those parameters in vr.input.bm.json .")
  _ = input("Press <Enter> to continue...")
  # Loop for each lib obj
  for lib_obj in lib_obj_list:
    print("")
    print("-------------------------------------------------------------------")
    print("[do] Under benchmark object: %s" %lib_obj)
    print("-------------------------------------------------------------------")
    os.chdir(lib_obj)
    # Check if all ITEMS:
    for file in ['INCAR', 'KPOINTS']:
      for task in ['RELAX', 'SSC', 'BAND', 'DOS']:
        task_file = file + '.' + task
        if not os.path.isfile(task_file):
          print("[error] File %s not found..."%task_file)
          print("[error] The benchmark need to calculate all of the task,")
          print("        which including: RELAX, SSC, BAND, and DOS.")
          print("[error] Please make sure ALL of the s are in lib folder.")
          sys.exit(1)
    # Determine the task name
    task_name = 'bm.' + os.path.split(lib_obj)[-1]
    print("[para] Set Task Name to: %s" %task_name)
    print("")
    # Determine the expc_total_cores
    default_etcs = 20
    if os.path.isfile('vr.expc_total_cores.json'):
      with open('vr.expc_total_cores.json') as jfrp:
        expc_total_cores = json.load(jfrp)
      default_etcs = expc_total_cores.get("expc_total_cores", 20)
    print("[input] Please input the expected total cores number. [ %d ]"
          %default_etcs)
    expc_total_cores = input('> ')
    if expc_total_cores.replace(' ', '') == '':
      expc_total_cores = default_etcs
    else:
      expc_total_cores = int(expc_total_cores)
    expc_total_cores_json = {"expc_total_cores":expc_total_cores}
    with open('vr.expc_total_cores.json', 'w') as jfwp:
      json.dump(expc_total_cores_json, jfwp)
    # Determine the nodes quantity
    nodes_quantity = round(expc_total_cores / env_para_list["cores_per_node"])
    if nodes_quantity <= 0:
      nodes_quantity = 1
      print("[warning] Invalid expected total cores ...")
      print("[warning] Forcely set nodes_quantity to 1.")
    print("[para] Set nodes quantity to: %d" %(nodes_quantity))
    print("")
    # Read in the default vaule of walltime, pew, and ompcores
    if os.path.isfile('vr.input.json'):
      with open('vr.input.json') as jfrp:
        default_paras = json.load(jfrp)
      default_job_walltime = default_paras.get("job_walltime", 48)
      default_pew = default_paras.get("plot_energy_window", [-6.0, 6.0])
      default_openmp_cores = default_paras.get("openmp_cores", 1)
    else:
      default_job_walltime = 48
      default_pew = [-6.0, 6.0]
      default_openmp_cores = 1
    # Determine the walltime
    print("[input] Please input jobs walltime for this object. [ %d ]"
          %default_job_walltime)
    job_walltime = input('> ')
    if job_walltime.replace(' ', '') == '':
      job_walltime = default_job_walltime
    else:
      job_walltime = int(job_walltime)
    if (not isinstance(job_walltime, int)) or (job_walltime <= 0):
      print("[error] Bad input...")
      sys.exit(1)
    print("[para] Set PBS walltime to: %d" %job_walltime)
    print("")
    # OpenMP cores number
    cores_per_node = env_para_list["cores_per_node"]
    print("[do] Read in the OpenMP cups number...")
    if (not isinstance(default_openmp_cores, int)) or \
      (default_openmp_cores <= 0):
      default_openmp_cores = 1
    print("[input] Please input the number of OpenMP cups. [ %d ]"
          %(default_openmp_cores))
    openmp_cores = input('> ')
    if openmp_cores.replace(' ', '') == '':
      openmp_cores = default_openmp_cores
    else:
      openmp_cores = int(openmp_cores)
    if (cores_per_node <= 0) or \
      (cores_per_node//openmp_cores*openmp_cores != cores_per_node):
      print('[error] Invalid omp cups number...')
      print('[tips] The OMP cups must be a divisor of the cores per node.')
      sys.exit(1)
    print("[para] Set the number of OMP cores: %d" %(openmp_cores))
    print("")
    # Determine the plot energy window
    print("[input] Please input the plot energy window. [", default_pew, "]")
    pew = input('> ')
    if pew.replace(' ', '') == '':
      pew = default_pew
    else:
      pew = pew.split()[:2]
      pew = [float(val) for val in pew]
    if pew[0] >= pew[1]:
      print('[error] The lower limit must be samller than the upper...')
      sys.exit(1)
    print("[para] Set plot window to:", pew)
    print("")
    # Determine the task list
    print("[para] Set task list to: 'TTTT' ")
    print("")
    # Write paras into the lib vr.input.json
    calc_para_list = {}
    for env_para_name in env_para_name_list:
      calc_para_list[env_para_name] = env_para_list[env_para_name]
    calc_para_list["task_name"] = task_name
    calc_para_list["nodes_quantity"] = nodes_quantity
    calc_para_list["openmp_cores"] = openmp_cores
    calc_para_list["job_walltime"] = job_walltime
    calc_para_list["plot_energy_window"] = pew
    calc_para_list["task_list"] = 'TTTT'
    with open('vr.input.json', 'w') as jfwp:
      json.dump(calc_para_list, jfwp, indent=2)
    os.chdir('../../..')
  return 0


def submit_jobs(lib_obj_list):
  _ = input('Press <Enter> to submit the test jobs...')
  with open('vasprun_path.json') as jfrp:
    vasprun = json.load(jfrp)
  vasprun = vasprun["vasprun"]
  for lib_obj in lib_obj_list:
    os.chdir(lib_obj)
    with open("vr.input.json") as jfrp:
      calc_para_list = json.load(jfrp)
    nodes_quantity = calc_para_list["nodes_quantity"]
    cores_per_node = calc_para_list["cores_per_node"]
    openmp_cores = calc_para_list["openmp_cores"]
    total_cores = nodes_quantity * cores_per_node
    print("[submit] BM :: %-40s :: Nodes-%-3d Cores-%-4d OMPUs-%-4d"
          %(lib_obj, nodes_quantity, total_cores, openmp_cores))
    command = '(echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo; echo) \
               | %s > /dev/null' %(vasprun)
    _ = os.system(command)
    os.chdir('../../..')
  return 0


def post_process(lib_obj_list):
  # Copy job kill file
  print("[do] Create the JOB KILL script...")
  kill_jobs = ['#!/bin/bash','#','']
  for lib_obj in lib_obj_list:
    kill_job_script = os.path.join(lib_obj, '_KILLJOB.sh')
    with open(kill_job_script) as frp:
      lines = frp.readlines()
    for line in lines:
      line = line.replace('\n','')
      if ('#' in line) or (line.replace(' ','') == ''):
        continue
      kill_jobs.append(line)
  with open('_BM-KILLJOBS.sh', 'w') as fwp:
    for line in kill_jobs:
      fwp.write(line + '\n')
  _ = os.system('chmod 740 _BM-KILLJOBS.sh')
  # Create clean file
  print("[do] Create the FILE CLEAN script...")
  clean_file = [
      '#!/bin/bash',
      '#',
      '',
      'for obj in lib/public/*; do',
      '  if [ -d "${obj}" ]; then',
      '    cd ${obj}',
      '    bash ./_CLEAN.sh',
      '    cd ../../..',
      '  fi',
      'done',
      'for obj in lib/private/*; do',
      '  if [ -d "${obj}" ]; then',
      '    cd ${obj}',
      '    bash ./_CLEAN.sh',
      '    cd ../../..',
      '  fi',
      'done',
      'rm vasprun_path.json',
      'rm _BM-KILLJOBS.sh',
      'rm _BM-SIMPLIFY.sh',
      'rm _BM-CLEAN.sh']
  with open('_BM-CLEAN.sh', 'w') as fwp:
    for line in clean_file:
      fwp.write(line + '\n')
  _ = os.system('chmod 740 _BM-CLEAN.sh')
  # Create simplify file
  print("[do] Create the FILE SIMPLYFY script...")
  simplify_file = ['#!/bin/bash', '#', '']
  for lib_obj in lib_obj_list:
    os.chdir(lib_obj)
    with open('vr.allpara.json') as jfrp:
      all_paras = json.load(jfrp)
      filename = all_paras["filename"]
    result_folder = filename["result_folder"]
    simplify_file.append('# Simplify %s' %lib_obj)
    simplify_file.append('cd %s' %lib_obj)
    simplify_file.append('mkdir .tmp')
    simplify_file.append('mv %s .tmp/' %result_folder)
    simplify_file.append('mv vr.input.json .tmp/')
    simplify_file.append('mv vr.allpara.json .tmp/')
    simplify_file.append('mv vr.expc_total_cores.json .tmp/')
    simplify_file.append('cp _CLEAN.sh .tmp/')
    simplify_file.append('mv vasp_submit.nscc.sh .tmp/')
    simplify_file.append('( echo ) | ./_CLEAN.sh')
    simplify_file.append('mv .tmp/* .')
    simplify_file.append('rm -r .tmp')
    simplify_file.append('cd ../../..')
    simplify_file.append('')
    os.chdir('../../..')
  simplify_file.append('# Delete current script')
  simplify_file.append('rm _BM-SIMPLIFY.sh')
  with open('_BM-SIMPLIFY.sh','w') as fwp:
    for line in simplify_file:  
      fwp.write(line + '\n')
  _ = os.system('chmod 740 _BM-SIMPLIFY.sh')
  return 0


def main():
  env_check()
  lib_obj_list = get_lib_objs()
  paras_read_and_write(lib_obj_list)
  submit_jobs(lib_obj_list)
  print("[do] Please wait 3 second for job submitting...")
  time.sleep(3)
  post_process(lib_obj_list)
  print("[done]")
  return 0


if __name__ == "__main__":
  main()
