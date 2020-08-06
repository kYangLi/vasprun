import os 
import sys 
import json 
import time 


def paras_load():
  with open("vr.allpara.json") as jfrp:
    all_para_list = json.load(jfrp)
    filename_list = all_para_list["filename"]
    calc_para_list = all_para_list["calc_para"]
    path_list = all_para_list["path_list"]
  return filename_list, calc_para_list, path_list


def file_exist(part_of_filename):
  for filename in os.listdir('.'):
    if part_of_filename in filename:
      return True
  return False


def grep(tstr, file):
  with open(file) as frp:
    lines = frp.readlines()
  targets = []
  for line in lines:
    if tstr in line:
      line = line.replace('\n','')
      targets.append(line)
  return targets

def grep_index(tstr, file):
  with open(file) as frp:
    lines = frp.readlines()
  targets_line_index = []
  index = 0
  for line in lines:
    if tstr in line:
      targets_line_index.append(index)
    index += 1
  return targets_line_index

def mpirun(filename_list, calc_para_list, vasp):
  vasp_log = filename_list["vasp_log"]
  sys_type = calc_para_list["sys_type"]
  nodes_quantity = calc_para_list["nodes_quantity"]
  cores_per_node = calc_para_list["cores_per_node"]
  total_cores_number = nodes_quantity * cores_per_node
  intel_module = calc_para_list["intel_module"]
  if sys_type == 'pbs':
    mpi_machinefile = filename_list["mpi_machinefile"]
    command = "mpirun -machinefile ../%s -np %d %s >> %s" %(mpi_machinefile,
                                                            total_cores_number,
                                                            vasp,
                                                            vasp_log)
  elif sys_type == 'slurm':
    command = "srun %s >> %s" %(vasp, vasp_log)
  elif sys_type == 'nscc':
    command = "yhrun -N %d -n %d %s >> %s" %(nodes_quantity,
                                             total_cores_number,
                                             vasp,
                                             vasp_log)
  _ = os.system(intel_module + '; ' + command)
  return 0


def res_collect(filename_list, calc_para_list, time_spend, task_tag):
  # Prepare 
  result_folder = filename_list["result_folder"]
  result_folder = '../%s' %result_folder
  if not os.path.isdir(result_folder):
    os.mkdir(result_folder)
  result_json = filename_list['result_json']
  result_json = os.path.join(result_folder, result_json)
  if os.path.isfile(result_json):
    with open(result_json) as jfrp:
      res_record = json.load(jfrp)
  else:
    res_record = {"time"           : {},
                  "lattice_para"   : {},
                  "fermi"          : {}, 
                  "energy"         : {}, 
                  "force_per_atom" : {}, 
                  "total_mag"      : {}
    }
  # Lattice constant
  with open('OUTCAR') as frp:
    lines = frp.readlines()
  index = 0
  for line in lines:
    if 'length of vectors' in line:
      lc_index = index
    index += 1
  lc_index += 1
  lcs = lines[lc_index].split(' ')
  lcs = list(filter(None, lines[lc_index].split(' ')))
  lcs = [float(val) for val in lcs[:3]]
  # Fermi level
  fermi_levels = grep('fermi', 'OUTCAR')
  fermi_level = fermi_levels[-1].split(':')[1].split('X')[0].replace(' ','')
  fermi_level = float(fermi_level)
  # Total energy
  total_energys = grep ('sigma', 'OUTCAR')
  total_energy = total_energys[-1].split('=')[2].replace(' ','')
  total_energy = float(total_energy)
  # Total force
  with open('POSCAR') as frp:
    lines = frp.readlines()
  atom_num = lines[6]
  atom_num = atom_num.replace('\n','')
  atom_num = list(filter(None, atom_num.split(' ')))
  atom_num_int = [int(val) for val in atom_num]
  atom_num = sum(atom_num_int)
  force_per_atoms = grep('total drift', 'OUTCAR')
  force_per_atom = force_per_atoms[-1].split(':')[1].split(' ')
  force_per_atom = list(filter(None, force_per_atom))
  force_per_atom[0] = float(force_per_atom[0])/atom_num
  force_per_atom[1] = float(force_per_atom[1])/atom_num
  force_per_atom[2] = float(force_per_atom[2])/atom_num
  # Total magnet
  total_mags = grep('mag=', 'OSZICAR')
  total_mag = total_mags[-1].split('=')[4].replace(' ','')
  total_mag = float(total_mag)
  # Total time
  total_time = res_record["time"].get("total", 0)
  total_time += time_spend
  # Result record
  res_record["time"]["total"] = total_time
  res_record["time"][task_tag] = time_spend
  res_record["lattice_para"][task_tag] = lcs
  res_record["fermi"][task_tag] = fermi_level
  res_record["energy"][task_tag] = total_energy
  res_record["force_per_atom"][task_tag] = force_per_atom
  res_record["total_mag"][task_tag] = total_mag
  with open(result_json, 'w') as jfwp:
    json.dump(res_record, jfwp, indent=1)
  return 0


def relax(filename_list, calc_para_list, task_index):
  relax_folder = filename_list["relax_folder"]
  relax_vasp = calc_para_list["relax_vasp"]
  vasp_log = filename_list["vasp_log"]
  task_list = calc_para_list["task_list"]
  if file_exist('-' + relax_folder):
    print("[info] Folder %s already exist, skip." %relax_folder)
    command = "mv *-%s %d-%s" %(relax_folder, task_index, relax_folder)
    _ = os.system(command)
    task_index += 1
  elif task_list[0] != 'T':
    print("[info] Relax not include in the task list, abandon this step...")
  else:
    # File prepare
    index_relax_folder = "%d-%s" %(task_index, relax_folder)
    os.mkdir(index_relax_folder)
    os.chdir(index_relax_folder)
    _ = os.system('cp ../INCAR.RELAX INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.RELAX KPOINTS')
    # Job Submit
    start_time = time.time()
    _ = os.system("date >> %s" %vasp_log)
    mpirun(filename_list, calc_para_list, relax_vasp)
    _ = os.system("date >> %s" %vasp_log)
    end_time = time.time()
    time_spend = end_time - start_time
    # Res. Collect
    _ = os.system("cp CONTCAR ../POSCAR.RELAXED")
    _ = os.system("cp CONTCAR ../POSCAR")
    res_collect(filename_list, calc_para_list, time_spend, 'relax')
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def ssc(filename_list, calc_para_list, task_index):
  ssc_folder = filename_list["ssc_folder"]
  ssc_vasp = calc_para_list["ssc_vasp"]
  vasp_log = filename_list["vasp_log"]
  task_list = calc_para_list["task_list"]
  if file_exist('-' + ssc_folder):
    print("[info] Folder %s already exist, skip." %ssc_folder)
    command = "mv *-%s %d-%s" %(ssc_folder, task_index, ssc_folder)
    _ = os.system(command)
    task_index += 1
  elif task_list[1] != 'T':
    print("[info SSC not include in the task list, abandon this step...")
  else:
    # File prepare
    index_ssc_folder = "%d-%s" %(task_index, ssc_folder)
    os.mkdir(index_ssc_folder)
    os.chdir(index_ssc_folder)
    _ = os.system('cp ../INCAR.SSC INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.SSC KPOINTS')
    # Job Submit
    start_time = time.time()
    _ = os.system("date >> %s" %vasp_log)
    mpirun(filename_list, calc_para_list, ssc_vasp)
    _ = os.system("date >> %s" %vasp_log)
    end_time = time.time()
    time_spend = end_time - start_time
    # Res. Collect
    res_collect(filename_list, calc_para_list, time_spend, 'ssc')
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def band_plot_collect(filename_list, calc_para_list, path_list):
  ## Prepare 
  curr_path = os.getcwd()
  result_folder = filename_list["result_folder"]
  result_folder = '../%s' %result_folder
  if not os.path.isdir(result_folder):
    print("[error] No result folder avaliable...")
    sys.exit(1)
  band_res_folder = filename_list["band_res_folder"]
  band_res_folder = os.path.join(result_folder, band_res_folder)
  if not os.path.isdir(band_res_folder):
    os.mkdir(band_res_folder)
  ## Use vaspkit to generate the file
  vaspkit = calc_para_list["vaspkit"]
  vaspkit_log = filename_list["vaspkit_log"]
  # Total Band 
  command = '(echo 211) | %s >> %s' %(vaspkit, vaspkit_log)
  _ = os.system(command)
  # Projected Band
  command = '(echo 213) | %s >> %s' %(vaspkit, vaspkit_log)
  _ = os.system(command)
  # Copy Band file 
  _ = os.system('cp KLABELS %s' %band_res_folder)
  _ = os.system('cp BAND.dat %s' %band_res_folder)
  _ = os.system('cp PBAND_*.dat %s' %band_res_folder)
  _ = os.system('cp BAND_GAP %s' %band_res_folder)
  # Plot Band 
  vasprun_path = path_list["vasprun_path"]
  band_plot_script = "%s/plot/vaspkit_band.py" %vasprun_path
  python_exec = path_list["python_exec"]
  band_fig = filename_list["band_fig"]
  pew = calc_para_list["plot_energy_window"]
  os.chdir(band_res_folder)
  command = "%s %s -n %s -u %f -d %f" %(python_exec, band_plot_script,
                                        band_fig, pew[1], pew[0])
  _ = os.system(command)
  _ = os.system("ln -s %s band_plot.py" %band_plot_script)
  os.chdir(curr_path)
  return 0


def band(filename_list, calc_para_list, path_list, task_index):
  band_folder = filename_list["band_folder"]
  ssc_folder = filename_list["ssc_folder"]
  band_vasp = calc_para_list["ssc_vasp"]
  vasp_log = filename_list["vasp_log"]
  task_list = calc_para_list["task_list"]
  index_band_folder = "%d-%s" %(task_index, band_folder)
  if file_exist('-' + band_folder):
    print("[info] Folder %s already exist, skip." %band_folder)
    command = "mv *-%s %s" %(band_folder, index_band_folder)
    _ = os.system(command)
    os.chdir(index_band_folder)
    band_plot_collect(filename_list, calc_para_list, path_list)
    os.chdir('..')
    task_index += 1
  elif task_list[2] != 'T':
    print("[info] Band not include in the task list, abandon this step...")
  else:
    # File prepare
    os.mkdir(index_band_folder)
    os.chdir(index_band_folder)
    _ = os.system('cp ../INCAR.BAND INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.BAND KPOINTS')
    _ = os.system('ln -s ../*-%s/CHGCAR CHGCAR' %ssc_folder)
    _ = os.system('ln -s ../*-%s/DOSCAR DOSCAR.SSC' %ssc_folder)
    # Job Submit
    start_time = time.time()
    _ = os.system("date >> %s" %vasp_log)
    mpirun(filename_list, calc_para_list, band_vasp)
    _ = os.system("date >> %s" %vasp_log)
    end_time = time.time()
    time_spend = end_time - start_time
    # Res. Collect
    res_collect(filename_list, calc_para_list, time_spend, 'band')
    _ = os.system('mv DOSCAR DOSCAR.BAND')
    _ = os.system('mv DOSCAR.SSC DOSCAR')
    band_plot_collect(filename_list, calc_para_list, path_list)
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def dos_plot_collect(filename_list, calc_para_list, path_list):
  ## Prepare 
  curr_path = os.getcwd()
  result_folder = filename_list["result_folder"]
  result_folder = '../%s' %result_folder
  if not os.path.isdir(result_folder):
    print("[error] No result folder avaliable...")
    sys.exit(1)
  dos_res_folder = filename_list["dos_res_folder"]
  dos_res_folder = os.path.join(result_folder, dos_res_folder)
  if not os.path.isdir(dos_res_folder):
    os.mkdir(dos_res_folder)
  ## Use vaspkit to generate the file
  vaspkit = calc_para_list["vaspkit"]
  vaspkit_log = filename_list["vaspkit_log"]
  # Total DOS
  command = '(echo 111) | %s >> %s' %(vaspkit, vaspkit_log)
  _ = os.system(command)
  # Projected DOS
  command = '(echo 113) | %s >> %s' %(vaspkit, vaspkit_log)
  _ = os.system(command)
  # Copy DOS file 
  _ = os.system('cp TDOS.dat %s' %dos_res_folder)
  _ = os.system('cp PDOS_*.dat %s' %dos_res_folder)
  # Plot DOS 
  vasprun_path = path_list["vasprun_path"]
  python_exec = path_list["python_exec"]
  dos_plot_script = "%s/plot/vaspkit_dos.py" %vasprun_path
  dos_fig = filename_list["dos_fig"]
  pew = calc_para_list["plot_energy_window"]
  os.chdir(dos_res_folder)
  command = "%s %s -n %s -u %f -d %f" %(python_exec, dos_plot_script, 
                                        dos_fig,  pew[1], pew[0])
  _ = os.system(command)
  _ = os.system("ln -s %s dos_plot.py" %dos_plot_script)
  os.chdir(curr_path)
  return 0


def dos(filename_list, calc_para_list, path_list, task_index):
  dos_folder = filename_list["dos_folder"]
  ssc_folder = filename_list["ssc_folder"]
  dos_vasp = calc_para_list["ssc_vasp"]
  vasp_log = filename_list["vasp_log"]
  task_list = calc_para_list["task_list"]
  index_dos_folder = "%d-%s" %(task_index, dos_folder)
  if file_exist('-' + dos_folder):
    print("[info] Folder %s already exist, skip." %dos_folder)
    command = "mv *-%s %s" %(dos_folder, index_dos_folder)
    _ = os.system(command)
    os.chdir(index_dos_folder)
    dos_plot_collect(filename_list, calc_para_list, path_list)
    os.chdir('..')
    task_index += 1
  elif task_list[2] != 'T':
    print("[info] DOS not include in the task list, abandon this step...")
  else:
    # File prepare
    os.mkdir(index_dos_folder)
    os.chdir(index_dos_folder)
    _ = os.system('cp ../INCAR.DOS INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.DOS KPOINTS')
    _ = os.system('ln -s ../*-%s/CHGCAR CHGCAR' %ssc_folder)
    # Job Submit
    start_time = time.time()
    _ = os.system("date >> %s" %vasp_log)
    mpirun(filename_list, calc_para_list, dos_vasp)
    _ = os.system("date >> %s" %vasp_log)
    end_time = time.time()
    time_spend = end_time - start_time
    # Res. Collect
    res_collect(filename_list, calc_para_list, time_spend, 'dos')
    dos_plot_collect(filename_list, calc_para_list, path_list)
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def main():
  ## Prepare 
  filename_list, calc_para_list, path_list = paras_load()
  task_index = 1
  _ = os.system("cp POSCAR POSCAR.INIT")
  ## Calculate
  task_index = relax(filename_list, calc_para_list, task_index)
  task_index = ssc(filename_list, calc_para_list, task_index)
  task_index = band(filename_list, calc_para_list, path_list, task_index)
  task_index = dos(filename_list, calc_para_list, path_list, task_index)
  _ = task_index
  ## Post Process
  _ = os.system("mv POSCAR.INIT POSCAR")
  return 0


if __name__ == "__main__":
  main()
