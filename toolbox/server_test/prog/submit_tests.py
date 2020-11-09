# Author: liyang@cmt.tsinghua
# Date: 2020.8.4
# Descripution: Server test code base on vasprun.

import os 
import sys
import json
import time
import socket


def env_check():
  if not os.path.isfile('vasprun_path.json'):
    print("[error] vasprun path file not found...")
    sys.exit(1)
  if (not os.path.isdir('lib/public')) or \
     (not os.path.isdir('lib/private')):
    print("[error] Calculation lib not found...")
    sys.exit(1)
  if not os.path.isfile('vr.input.st.json'):
    print("[error] No vr.input.st.json was found in test dir. ...")
    sys.exit(1)
  if os.path.isdir('calc'):
    _ = os.system("rm -rf calc")
  os.mkdir('calc')
  return 0


def copy_file_to_calc():
  public_lib = 'lib/public'
  private_lib = 'lib/private'
  calc_dir = 'calc'
  public_obj_list = os.listdir(public_lib)
  private_obj_list = os.listdir(private_lib)
  lib_obj_list = []
  calc_obj_list = []
  for obj in public_obj_list:
    lib_obj = os.path.join(public_lib, obj)
    if os.path.isdir(lib_obj):
      lib_obj_list.append(lib_obj)
  for obj in private_obj_list:
    if os.path.join(public_lib, obj) in lib_obj_list:
      print("[error] Folder name '%s' appear in both pri. and pub. lib..."%obj)
      sys.exit(1)
    lib_obj = os.path.join(private_lib, obj)
    if os.path.isdir(lib_obj):
      lib_obj_list.append(lib_obj)
  # Copy files
  for lib_obj in lib_obj_list:
    obj = os.path.split(lib_obj)[-1]
    calc_obj = os.path.join(calc_dir, obj)
    os.mkdir(calc_obj)
    _ = os.system("cp %s/INCAR* %s/" %(lib_obj, calc_obj))
    _ = os.system("cp %s/KPOINTS* %s/" %(lib_obj, calc_obj))
    _ = os.system("cp %s/POTCAR %s/" %(lib_obj, calc_obj))
    _ = os.system("cp %s/POSCAR %s/" %(lib_obj, calc_obj))
    _ = os.system("cp %s/vr.input.json %s/" %(lib_obj, calc_obj))
    _ = os.system("cp %s/vr.expc_total_cores.json %s/" %(lib_obj, calc_obj))
    calc_obj_list.append(calc_obj)
  return calc_obj_list


def paras_read_and_write(calc_obj_list):
  # Read in test parameters
  with open('vr.input.st.json') as jfrp:
    env_para_list = json.load(jfrp)
  # Report the mechine hostname
  env_para_list["hostname"] = socket.gethostname()
  with open('vr.input.st.json', 'w') as jfwp:
    json.dump(env_para_list, jfwp, indent=2)
  # Define the env name
  env_para_name_list = ["intel_module", "relax_vasp", "ssc_vasp",
                        "vaspkit", "sys_type", "cores_per_node",
                        "pbs_queue"]
  for env_para_name in env_para_name_list:
    print("[para] Set %-14s   ::   %s"
          %(env_para_name, str(env_para_list.get(env_para_name, None))))
  print("[info] Exit this script to modify those parameters in vr.input.st.json .")
  # Determine the nodes quantity
  for calc_obj in calc_obj_list:
    print("")
    print("-------------------------------------------------------------------")
    print("[do] Under test object: %s" %calc_obj)
    print("-------------------------------------------------------------------")
    os.chdir(calc_obj)
    # Check if all ITEMS:
    for file in ['INCAR', 'KPOINTS']:
      for task in ['RELAX', 'SSC', 'BAND', 'DOS']:
        task_file = file + '.' + task
        if not os.path.isfile(task_file):
          print("[error] File %s not found..."%task_file)
          print("[error] The benchmark need to calculate all of the task...")
          print("[error] Which including: RELAX, SSC, BAND, and DOS.")
          print("[error] Please make sure ALL of the s are in lib folder.")
          sys.exit(1)
    # Check if the calc has run the benchmark...
    if (not os.path.isfile('vr.input.json')) or \
       (not os.path.isfile('vr.expc_total_cores.json')):
      print("[error] %s not ready for calculate..." %calc_obj)
      print("[error] vr.*.json not found in %s... Remove..." %calc_obj)
      os.chdir('../..')
      if not os.path.isdir('_trash'):
        os.mkdir('_trash')
      _ = os.system('mv %s _trash/' %calc_obj)
      continue
    # Read in the default paras
    with open('vr.input.json') as jfrp:
      calc_para_list = json.load(jfrp)
    # Determine the task name
    task_name = 'st.' + os.path.split(calc_obj)[-1]
    # Determin the nodes quantity
    with open('vr.expc_total_cores.json') as jfrp:
      expc_total_cores = json.load(jfrp)
      expc_total_cores = expc_total_cores["expc_total_cores"]
    default_nodes_quantity = \
      round(expc_total_cores / env_para_list["cores_per_node"])
    if (not isinstance(default_nodes_quantity, int)) or \
       (default_nodes_quantity <= 0):
     default_nodes_quantity = 1
    print("[input] Please input the nodes quantity. [ %d ]"
          %default_nodes_quantity)
    nodes_quantity = input('> ')
    if nodes_quantity.replace(' ','') == '':
      nodes_quantity = default_nodes_quantity
    else:
      nodes_quantity = int(nodes_quantity)
      if (not isinstance(nodes_quantity, int)) or (nodes_quantity <= 0):
        nodes_quantity = 1
        print("[warning] Invalid nodes qunatity ...")
        print("[warning] Forcely set nodes_quantity to 1.")
    print("[para] Using %d nodes." %nodes_quantity)
    print("")
    # Read the VASP6 OMP cpus number
    cores_per_node = env_para_list["cores_per_node"]
    if env_para_list["sys_type"] == 'pbs':
      print("[do] Read in the VASP6 PBS OMP cups number...")
      default_openmp_cpus = calc_para_list.get("openmp_cpus", 1)
      if (not isinstance(default_openmp_cpus, int)) or \
        (default_openmp_cpus <= 0):
        default_openmp_cpus = 1
      print("[input] Please input the number of vasp6 OMP cups. [ %d ]"
            %(default_openmp_cpus))
      openmp_cpus = input('> ')
      if openmp_cpus.replace(' ','') == '':
        openmp_cpus = default_openmp_cpus
      else:
        openmp_cpus = int(openmp_cpus)
      if (cores_per_node <= 0) or \
        (cores_per_node//openmp_cpus*openmp_cpus != cores_per_node):
        print('[error] Invalid omp cups number...')
        print('[tips] The OMP cups must be a divisor of the cores per node.')
        sys.exit(1)
      print("[para] Set the number of OMP cpus: %d" %(openmp_cpus))
      print("")
    # Write paras into the calc vr.input.json
    for env_para_name in env_para_name_list:
      calc_para_list[env_para_name] = env_para_list[env_para_name]
    calc_para_list["nodes_quantity"] = nodes_quantity
    if env_para_list["sys_type"] == 'pbs':
      calc_para_list["openmp_cpus"] = openmp_cpus
    calc_para_list["task_name"] = task_name
    with open('vr.input.json', 'w') as jfwp:
      json.dump(calc_para_list, jfwp, indent=2)
    os.chdir('../..')
  return 0 


def submit_jobs(calc_obj_list):
  _ = input('Press <Enter> to submit the test jobs...')
  with open('vasprun_path.json') as jfrp:
    vasprun = json.load(jfrp)
  vasprun = vasprun["vasprun"]
  for calc_obj in calc_obj_list:
    os.chdir(calc_obj)
    with open("vr.input.json") as jfrp:
      calc_para_list = json.load(jfrp)
    nodes_quantity = calc_para_list["nodes_quantity"]
    cores_per_node = calc_para_list["cores_per_node"]
    total_cores = nodes_quantity * cores_per_node
    print("[submit] ST :: %-60s :: Nodes %3d   Cores %4d"
          %(calc_obj, nodes_quantity, total_cores))
    command = '(echo; echo; echo; echo; echo; echo; echo; echo; echo; echo) \
               | %s > /dev/null' %(vasprun)
    _ = os.system(command)
    os.chdir('../..')
  return 0 


def post_process(calc_obj_list):
  # Copy job kill file
  print("[do] Create the JOB KILL script...")
  kill_jobs = ['#!/bin/bash','#','']
  for calc_obj in calc_obj_list:
    kill_job_script = os.path.join(calc_obj, '_KILLJOB.sh')
    with open(kill_job_script) as frp:
      lines = frp.readlines()
    for line in lines:
      line = line.replace('\n','')
      if ('#' in line) or (line.replace(' ','') == ''):
        continue
      kill_jobs.append(line)
  with open('_ST-KILLJOBS.sh', 'w') as fwp:
    for line in kill_jobs:
      fwp.write(line + '\n')
  _ = os.system('chmod 740 _ST-KILLJOBS.sh')
  # Create clean file
  print("[do] Create the FILE CLEAN script...")
  clean_file = [
  '#!/bin/bash',
  '#',
  '',
  'rm -rf calc',
  'rm -rf _trash',
  'rm     vasprun_path.json',
  'rm     _ST-KILLJOBS.sh',
  'rm     _ST-CLEAN.sh',
  ] 
  with open('_ST-CLEAN.sh','w') as fwp:
    for line in clean_file:  
      fwp.write(line + '\n')
  _ = os.system('chmod 740 _ST-CLEAN.sh')
  return 0 

def main():
  env_check()
  calc_obj_list = copy_file_to_calc()
  paras_read_and_write(calc_obj_list)
  submit_jobs(calc_obj_list)
  print("[do] Please wait 3 second for job submitting...")
  time.sleep(3)
  post_process(calc_obj_list)
  print("[done]")
  return 0 


if __name__ == "__main__":
  main()