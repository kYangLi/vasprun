# Author: liyang@cmt.tsinghua
# Date: 2020.8.2
# Descripution: This python script is designed for run vasp
#               calculation with one command.

import os
import sys
import json


def grep(tstr, file):
  with open(file) as frp:
    lines = frp.readlines()
  targets = []
  for line in lines:
    if tstr in line:
      line = line.replace('\n','')
      targets.append(line)
  return targets


def check_input_json(vasprun_path):
  input_json = 'vr.input.json'
  if not os.path.isfile(input_json):
    input_json = os.path.join(vasprun_path, input_json)
    print("[info] DO NOT found the input json file in current folder...")
    print("[do] Searching in program folder...")
    if not os.path.isfile(input_json):
      print("[info] DO NOT found the input json file in vasprun folder...")
      print("[info] No defualt value is setting...")
      return {}
  print("[para] You are using the input file: %s" %(input_json))
  with open(input_json) as jfrp:
    calc_para_list = json.load(jfrp)
  return calc_para_list


def read_parameters():
  print("")
  print("+----------------------------+")
  print("|     Parameters Read in     |")
  print("+----------------------------+")
  ## Init Parameters lists
  filename_list = {"mpi_machinefile" : 'cores-list',
                   "relax_folder"    : 'RELAX',
                   "ssc_folder"      : 'SSC',
                   "band_folder"     : 'BAND',
                   "dos_folder"      : 'DOS',
                   "result_folder"   : 'RESULT',
                   "band_res_folder" : 'band',
                   "dos_res_folder"  : 'dos',
                   "result_json"     : 'result.json',
                   "vasp_log"        : 'VASP.log',
                   "vaspkit_log"     : 'VASPKIT.log',
                   "band_fig"        : 'band',
                   "dos_fig"         : 'dos'}
  vasprun_path = os.path.realpath(sys.argv[0])
  curr_script_name = os.path.split(vasprun_path)[-1]
  vasprun_path = vasprun_path.replace('/'+curr_script_name, '')
  python_exec = os.popen('which python').read().replace('\n','')
  path_list = {"vasprun_path" : vasprun_path,
               "python_exec"  : python_exec}
  calc_para_list = check_input_json(vasprun_path)
  sys_type_list = ["pbs", "slurm", "nscc", "direct"]
  # Remove the older RESULT
  result_folder = filename_list["result_folder"]
  if os.path.isdir(result_folder):
    _ = os.system('rm -r %s' %result_folder)
  ## Read from command line
  # Path list
  print("[para] You are using python: %s" %python_exec)
  print("[para] You are using the vasprun in: %s" %vasprun_path)
  print("")
  # Task Name
  print("[do] Read in the task name...")
  curr_dirname = os.path.split(os.getcwd())[-1]
  # default_task_name = calc_para_list["task_name"]
  # if not default_task_name:
  #   default_task_name = curr_dirname
  default_task_name = curr_dirname
  print("[input] Please input the task name. [ %s ]" %default_task_name)
  task_name = input('> ')
  if task_name.replace(' ','') == '':
    task_name = default_task_name
  calc_para_list["task_name"] = task_name
  print("[para] Task name: %s" %task_name)
  print("")
  # Selected Task List
  print("[do] Read in the task list...")
  default_task_list = calc_para_list.get("task_list")
  if not default_task_list:
    default_task_list = 'TTTT'
  print("[input] Please input the selected task list. [ %s ]"%default_task_list)
  task_list = input("> ")
  if task_list.replace(' ', '') == '':
    task_list = default_task_list
  task_list = task_list.upper()
  if ('T' not in task_list) or (len(task_list) != 4):
    print("[error] Invalid task list, exit...")
    sys.exit(1)
  if task_list[2] == 'T' or task_list[3] == 'T':
    print("[info] Calculating the Bnad or DOS, add the SSC task to the list...")
    # if calculate the band or dos, then must calculate ssc.
    task_list = task_list[0] + 'T' + task_list[2] + task_list[3]
  calc_para_list["task_list"] = task_list
  print("[para] Task list: %s" %task_list)
  print("")
  # Intel Module
  print("[do] Read in the intel module...")
  intel_module = calc_para_list.get("intel_module")
  if not intel_module:
    print("[info] Not set the INTEL MODULE yet...")
    print("[input] Please input the intel module.")
    intel_module = input("> ")
    calc_para_list["intel_module"] = intel_module
  command = "%s > /dev/null 2>&1; echo ${MKLROOT}"\
            %(calc_para_list["intel_module"])
  mklroot = os.popen(command).read().replace('\n','')
  print("[para] Using the Intel module: %s" %intel_module)
  print("[para] Using the Intel MKL lib: %s" %(mklroot))
  print("")
  # VASP for Relax
  if task_list[0] == 'T':
    print("[do] Read in the VASP for relax...")
    relax_vasp = calc_para_list.get("relax_vasp")
    if not relax_vasp:
      print("[info] Not set the VASP for relax yet...")
      print("[input] Please input the vasp.relax path.")
      relax_vasp = input("> ")
      calc_para_list["relax_vasp"] = relax_vasp
    if not os.path.isfile(relax_vasp):
      print("[error] Invalid path of relax VASP... exit..")
      sys.exit(1)
    print("[para] Using the relax VASP: %s" %(relax_vasp))
  else:
    print("[skip] The relax step is not in the task list...")
    print("[skip] Skip the read in for relax VASP...")
  print("")
  # VASP for SSC
  if task_list[1] == 'T' or task_list[3] == 'T':
    print("[do] Read in the VASP for SSC...")
    ssc_vasp = calc_para_list.get("ssc_vasp")
    if not ssc_vasp:
      print("[info] Not set the VASP for SSC yet...")
      print("[input] Please input the vasp.ssc path.")
      ssc_vasp = input("> ")
      calc_para_list["ssc_vasp"] = ssc_vasp
    if not os.path.isfile(ssc_vasp):
      print("[error] Invalid path of ssc VASP... exit..")
      sys.exit(1)
    print("[para] Using the SSC VASP: %s" %(ssc_vasp))
  else:
    print("[skip] The ssc step is not in the task list...")
    print("[skip] Skip the read in for SSC VASP...")
  print("")
  # VASPKIT
  if task_list[2] == 'T' or task_list[3] == 'T':
    print("[do] Read in the VASPKIT...")
    vaspkit = calc_para_list.get("vaspkit")
    if not vaspkit:
      print("[info] Not set the VASPKIT yet...")
      print("[input] Please input the vaspkit path.")
      vaspkit = input("> ")
      calc_para_list["vaspkit"] = vaspkit
    if not os.path.isfile(vaspkit):
      print("[error] Invalid path of vaspkit... exit..")
      sys.exit(1)
    # Check vaspkit version:
    vk_res = os.popen('echo 0 | %s' %vaspkit).read()
    vk_version = vk_res.split('VASPKIT Version:')[1].split()[0]
    print("[para] Using the vaspkit: %s" %(vaspkit))
    print("[para] Current vaspkit version is: %s" %vk_version)
    if vk_version != '1.12':
      print("[error] Please using the vaspkit-1.12 ...")
      print("[tips] Go to website: ")
      print("  https://sourceforge.net/projects/vaspkit/files/Binaries/vaspkit.1.12.linux.x64.tar.gz/download")
      print("  to download the vaspkit-1.12...")
      sys.exit()
  else:
    print("[skip] The band&dos step is not in the task list...")
    print("[skip] Skip the read in for VASPKIT...")
  print("")
  # System Type
  print("[do] Read in the system type...")
  sys_type = calc_para_list.get("sys_type")
  if sys_type not in sys_type_list:
    print("[input] Please input the system type of your mechine.")
    print("[input] You can choice one from the list: ", sys_type_list)
    sys_type = input("> ")
    if sys_type not in sys_type_list:
      print("[error] Invalid system type...")
      sys.exit(1)
    calc_para_list["sys_type"] = sys_type
  print("[para] Under the job system: %s" %sys_type)
  print("")
  # Cores Per Nodes
  print("[do] Read in the number of cores per node...")
  default_cores_per_node = calc_para_list.get("cores_per_node", 1)
  if (not isinstance(default_cores_per_node, int)) or \
     (default_cores_per_node <= 0):
     default_cores_per_node = 1
  print("[input] Please input the number of cores per node. [ %d ]"
        %default_cores_per_node)
  cores_per_node = input('> ')
  if cores_per_node.replace(' ','') == '':
    cores_per_node = default_cores_per_node
  else:
    cores_per_node = int(cores_per_node)
    if (cores_per_node <= 0):
      print('[error] Invalid nodes quantity...')
      sys.exit(1)
  calc_para_list["cores_per_node"] = cores_per_node
  print("[para] Set the number of cores per node: %d" %(cores_per_node))
  print("")
  # OPENMP cpus number
  if (sys_type == 'pbs') or (sys_type == 'direct'):
    print("[do] Read in the VASP6 PBS OMP cups number...")
    default_openmp_cpus = calc_para_list.get("openmp_cpus", 1)
    if (not isinstance(default_openmp_cpus, int)) or \
       (default_openmp_cpus <= 0):
      default_openmp_cpus = 1
    print("[input] Please input the number of vasp6 OMP cups. [ %d ]"
          %(default_openmp_cpus))
    openmp_cpus = input('> ')
    if openmp_cpus.replace(' ', '') == '':
      openmp_cpus = default_openmp_cpus
    else:
      openmp_cpus = int(openmp_cpus)
    if (cores_per_node <= 0) or \
      (cores_per_node//openmp_cpus*openmp_cpus != cores_per_node):
      print('[error] Invalid omp cups number...')
      print('[tips] The omp cups num must be a divisor of the cores per node.')
      sys.exit(1)
    calc_para_list["openmp_cpus"] = openmp_cpus
    print("[para] Set the number of OMP cpus: %d" %(openmp_cpus))
    print("")
  # Nodes Quantity
  print("[do] Read in the nodes quantity...")
  default_nodes_quantity = calc_para_list.get("nodes_quantity")
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
      print('[error] Invalid nodes quantity...')
      sys.exit(1)
  calc_para_list["nodes_quantity"] = nodes_quantity
  print("[para] Using %d nodes." %nodes_quantity)
  print("")
  # PBS Walltime
  if sys_type == 'pbs':
    print("[do] Read in the PBS walltime...")
    default_pbs_walltime = calc_para_list.get("pbs_walltime")
    if (not isinstance(default_pbs_walltime, int)) or \
      (default_pbs_walltime <= 0):
      default_pbs_walltime = 1
    print("[input] Please input the PBS walltime in hours. [ %d ]" 
          %default_pbs_walltime)
    pbs_walltime = input('> ')
    if pbs_walltime.replace(' ','') == '':
      pbs_walltime = default_pbs_walltime
    else:
      pbs_walltime = int(pbs_walltime)
      if (not isinstance(pbs_walltime, int)) or (pbs_walltime <= 0):
        print('[error] Invalid PBS walltime...')
        sys.exit(1)
    calc_para_list["pbs_walltime"] = pbs_walltime
    print("[para] Using PBS wall time : %s hour(s)." %pbs_walltime)
    print("")
  # PBS Queue
  if (sys_type == 'pbs') or (sys_type == 'slurm'):
    print("[do] Read in the PBS queue...")
    default_pbs_queue = calc_para_list.get("pbs_queue")
    print("[input] Please input the PBS queue. [ %s ]" %default_pbs_queue)
    pbs_queue = input("> ")
    if pbs_queue.replace(' ','') == '':
      pbs_queue = default_pbs_queue
    if pbs_queue.replace(' ','') == '':
      print("[error] Invalid PBS queue...")
      sys.exit(1)
    calc_para_list["pbs_queue"] = pbs_queue
    print("[para] You are in the queue: %s" %pbs_queue)
    print("")
  # Plot Energy Window
  if task_list[2] == 'T' or task_list[3] == 'T':
    print("[do] Read in the band&dos plot energy window...")
    default_pew = calc_para_list.get("plot_energy_window")
    if not default_pew:
      default_pew = [-6, 6]
    print("[input] Please input the plot energy window. [ %f, %f ]" 
          %(default_pew[0], default_pew[1]))
    pew = input('> ')
    if pew.replace(' ','') == '':
      pew = default_pew
    else:
      pew = pew.split()
      pew[0] = float(pew[0])
      pew[1] = float(pew[1])
      if pew[1] <= pew[0]:
        print('[error] The lower limit must be samller than the upper...')
        sys.exit(1)
    calc_para_list["plot_energy_window"] = pew
    print("[para] Plot energy window: ", pew)
    print("")
  ## Return Values
  return filename_list, calc_para_list, path_list


def record_parameters(filename_list, calc_para_list, path_list):
  all_para_list = {"filename"  : filename_list,
                   "calc_para" : calc_para_list,
                   "path_list" : path_list}
  with open('vr.input.json', 'w') as jfwp:
    json.dump(calc_para_list, jfwp, indent=2)
  with open('vr.allpara.json', 'w') as jfwp:
    json.dump(all_para_list, jfwp, indent=2)
  return 0


def file_check(calc_para_list):
  print("+----------------------------+")
  print("|         File Check         |")
  print("+----------------------------+")
  task_list = calc_para_list["task_list"]
  ## POSCAR
  print("[do] Checing POSCAR...")
  element_table = ['H',  'He', 'Li', 'Be', 'B' , 'C' , 'N' , 'O' , 'F' , 'Ne',
                   'Na', 'Mg', 'Al', 'Si', 'P' , 'S' , 'Cl', 'Ar', 'K' , 'Ca',
                   'Sc', 'Ti', 'V' , 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
                   'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y' , 'Zr',
                   'Nb', 'Mo', 'Tc', 'Tu', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
                   'Sb', 'Te', 'I' , 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
                   'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
                   'Lu', 'Hf', 'Ta', 'W' , 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
                   'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
                   'Pa', 'U' , 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
                   'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
                   'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
  if not os.path.isfile('POSCAR'):
    print("[error] POSCAR not found...")
    sys.exit(1)
  with open('POSCAR') as frp:
    lines = frp.readlines()
  poscar_elements = lines[5].replace('\n','').split()
  for element in poscar_elements:
    if element not in element_table:
      print("[error] POSCAR element list error...")
      print("[error] Please make sure the 6th line is the element list...")
      sys.exit(1)
  print("[done] POSCAR PASS.")
  print("")
  ## POTCAR
  print("[do] Checking POTCAR...")
  potcar_elements = grep('VRH', 'POTCAR')
  potcar_elements = \
    [val.split('=')[1].split(':')[0].replace(' ','') for val in potcar_elements]
  if potcar_elements != poscar_elements:
    print("[error] POTCAR, POSCAR elements do not match...")
    sys.exit(1)
  print("[done] POTCAR PASS.")
  print("")
  ## VASP && VASPKIT
  #-->has been checked in parameters read in step, skip...
  ## INCAR && KPOINTS
  print("[do] Checking INCAR & KPOINTS...")
  if task_list[0] == 'T':
    if not os.path.isfile('INCAR.RELAX'):
      print("[error] INCAR.RELAX not found...")
      sys.exit(1)
    if not os.path.isfile('KPOINTS.RELAX'):
      print("[error] KPOINTS.RELAX not found...")
      sys.exit(1)
  if task_list[1] == 'T':
    if not os.path.isfile('INCAR.SSC'):
      print("[error] INCAR.SSC not found...")
      sys.exit(1)
    if not os.path.isfile('KPOINTS.SSC'):
      print("[error] KPOINTS.SSC not found...")
      sys.exit(1)
  if task_list[2] == 'T':
    if not os.path.isfile('INCAR.BAND'):
      print("[error] INCAR.BAND not found...")
      sys.exit(1)
    if not os.path.isfile('KPOINTS.BAND'):
      print("[error] KPOINTS.BAND not found...")
      sys.exit(1)
  if task_list[3] == 'T':
    if not os.path.isfile('INCAR.DOS'):
      print("[error] INCAR.DOS not found...")
      sys.exit(1)
    if not os.path.isfile('KPOINTS.DOS'):
      print("[error] KPOINTS.DOS not found...")
      sys.exit(1)
  print("[done] INCAR & KPOINTS PASS.")
  print("")
  return 0


def vasp_submit(filename_list, calc_para_list, path_list):
  print("+----------------------------+")
  print("|         Submit VASP        |")
  print("+----------------------------+")
  print("[do] Creating job submit script...")
  # Parameters read in
  vasprun_path = path_list["vasprun_path"]
  sys_type = calc_para_list["sys_type"]
  nodes_quantity = calc_para_list["nodes_quantity"]
  cores_per_node = calc_para_list["cores_per_node"]
  total_cores = nodes_quantity * cores_per_node
  task_name = calc_para_list["task_name"]
  vasp_calc_script = os.path.join(vasprun_path, 'submit', 'vasp_calc.py')
  python_exec = os.popen('which python').read().replace('\n','')
  # PBS system
  if sys_type == 'pbs':
    pbs_walltime = calc_para_list["pbs_walltime"]
    pbs_queue = calc_para_list["pbs_queue"]
    mpi_machinefile = filename_list["mpi_machinefile"]
    submit_file = "%s/submit/pbs.sh" %vasprun_path
    with open(submit_file) as frp:
      script = frp.read()
    script = script.replace('__task_name__', task_name)
    script = script.replace('__nodes_quantity__', str(nodes_quantity))
    script = script.replace('__cores_per_node__', str(cores_per_node))
    script = script.replace('__pbs_walltime__', str(pbs_walltime))
    if pbs_queue == 'unset-pbs-queue':
      script = script.replace('#PBS -q', '##PBS -q')
    else:
      script = script.replace('__pbs_queue__', pbs_queue)
    script = script.replace('__python_exec__', python_exec)
    script = script.replace('__vasp_calc_script__', vasp_calc_script)
    script = script.replace('__mpi_mechinefile__', mpi_machinefile)
    with open('vasp_submit.pbs.sh', 'w') as fwp:
      fwp.write(script)
    command = 'qsub vasp_submit.pbs.sh'
  # SLURM system
  elif sys_type == 'slurm':
    pbs_queue = calc_para_list["pbs_queue"]
    submit_file = "%s/submit/slurm.sh" %vasprun_path
    with open(submit_file) as frp:
      script = frp.read()
    script = script.replace('__task_name__', task_name)
    script = script.replace('__nodes_quantity__', str(nodes_quantity))
    script = script.replace('__total_cores__', str(total_cores))
    if pbs_queue == 'unset-pbs-queue':
      script = script.replace('#SBATCH -p', '##SBATCH -p')
    else:
      script = script.replace('__pbs_queue__', pbs_queue)
    script = script.replace('__python_exec__', python_exec)
    script = script.replace('__vasp_calc_script__', vasp_calc_script)
    with open('vasp_submit.slurm.sh', 'w') as fwp:
      fwp.write(script)
    command = 'sbatch vasp_submit.slurm.sh'
  # NSCC system
  elif sys_type == 'nscc':
    submit_file = "%s/submit/nscc.sh" %vasprun_path
    with open(submit_file) as frp:
      script = frp.read()
    script = script.replace('__task_name__', task_name)
    script = script.replace('__nodes_quantity__', str(nodes_quantity))
    script = script.replace('__total_cores__', str(total_cores))
    script = script.replace('__python_exec__', python_exec)
    script = script.replace('__vasp_calc_script__', vasp_calc_script)
    with open('vasp_submit.nscc.sh', 'w') as fwp:
      fwp.write(script)
    command = 'yhbatch vasp_submit.nscc.sh'
  elif sys_type == 'direct':
    submit_file = "%s/submit/direct.sh" %vasprun_path
    with open(submit_file) as frp:
      script = frp.read()
    script = script.replace('__task_name__', task_name)
    script = script.replace('__python_exec__', python_exec)
    script = script.replace('__vasp_calc_script__', vasp_calc_script)
    with open('vasp_submit.direct.sh', 'w') as fwp:
      fwp.write(script)
    command = 'nohup bash vasp_submit.direct.sh > %s.out 2>&1 &' %task_name
  # Submit the script
  print("[done] vasp_submit.%s.sh" %sys_type)
  _ = input("Press <Enter> to confirm the submition...")
  print("[do] Submitting the job...")
  print("[do] %s" %command)
  job_id = os.popen(command).read().replace('\n','')
  if (sys_type == 'slurm') or (sys_type == 'nscc'):
    job_id = job_id.split()[-1]
  print("[done] Job ID: " + job_id)
  return job_id


def post_process(job_id, calc_para_list, filename_list):
  print("")
  print("+----------------------------+")
  print("|        Post Process        |")
  print("+----------------------------+")
  print("[do] Creating post script...")
  sys_type = calc_para_list["sys_type"]
  relax_folder = filename_list["relax_folder"]
  ssc_folder = filename_list["ssc_folder"]
  band_folder = filename_list["band_folder"]
  dos_folder = filename_list["dos_folder"]
  result_folder = filename_list["result_folder"]
  mpi_machinefile = filename_list["mpi_machinefile"]
  task_name = calc_para_list["task_name"]
  # Kill job script
  kill_job = ['#!/bin/bash','#','']
  if sys_type == 'pbs':
    kill_job.append('qdel %s'%(job_id))
  elif sys_type == 'slurm':
    kill_job.append('scancel %s'%(job_id))
  elif sys_type == 'nscc':
    kill_job.append('yhcancel %s'%(job_id))
  with open("_KILLJOB.sh", 'w') as fwp:
    for line in kill_job:
      fwp.write(line + '\n')
  # Clean script
  clean_folder = [
    '#!/bin/bash',
    '#',
    '',
    'read -p "Press <Enter> to confirm..."',
    'rm -rf *-%s'%(relax_folder),
    'rm -rf *-%s'%(ssc_folder),
    'rm -rf *-%s'%(band_folder),
    'rm -rf *-%s'%(dos_folder),
    'rm -rf %s'%(result_folder),
    'rm     POSCAR.*',
    'rm     %s.o*'%(task_name),
    'rm     slurm-*.out',
    'rm     %s'%(mpi_machinefile),
    'rm     vasp_submit.*.sh',
    'rm     vr.allpara.json',
    'rm     _KILLJOB.sh',
    'rm     _CLEAN.sh '
  ]
  with open("_CLEAN.sh", 'w') as fwp:
    for line in clean_folder:
      fwp.write(line + '\n')
  os.system("chmod 740 _KILLJOB.sh _CLEAN.sh")
  print("[done] _KILLJOB.sh _CLEAN.sh")
  return 0


def welcome_interface():
  # Check the folder
  if (not os.path.isfile("POSCAR")) or (not os.path.isfile("POTCAR")):
    print("[error] You are not under a VASP calculation folder.")
    sys.exit(1)
  # Welcome
  print("                              ")
  print("    +--------------------+    ")
  print("====| Welcome to vasprun |====")
  print("    +--------------------+    ")
  print("                              ")
  print("+----------------------------+")
  print("|     Tips Before Start      |")
  print("+----------------------------+")
  print("[tips] Please double check the vasprun(.py) are in the vasprun path.")
  print("[tips] Please make sure you are using vaspkit-1.12 ...")
  _ = input('Press <Enter> to start the vasprun process... ')
  return 0


def end_interface():
  print("                              ")
  print("+----------------------------+")
  print("|        SUBMIT DONE         |")
  print("+----------------------------+")
  return 0 


def main():
  welcome_interface()
  filename_list, calc_para_list, path_list = read_parameters()
  record_parameters(filename_list, calc_para_list, path_list)
  file_check(calc_para_list)
  job_id = vasp_submit(filename_list, calc_para_list, path_list)
  post_process(job_id, calc_para_list, filename_list)
  end_interface()


if __name__ == '__main__':
  main()
