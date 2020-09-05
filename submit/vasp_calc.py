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
    vasp6_omp_cups = calc_para_list["vasp6_omp_cups"]
    mpi_machinefile = filename_list["mpi_machinefile"]
    vasp_process_num = total_cores_number // vasp6_omp_cups
    process_per_node = vasp_process_num // nodes_quantity
    command = "export OMP_NUM_THREADS=%d; \
               mpirun -machinefile ../%s -ppn %d -np %d %s >> %s" \
               %(vasp6_omp_cups, mpi_machinefile, process_per_node,
                 vasp_process_num, vasp, vasp_log)
  elif sys_type == 'slurm':
    command = "srun %s >> %s" %(vasp, vasp_log)
  elif sys_type == 'nscc':
    command = "yhrun -N %d -n %d %s >> %s" %(nodes_quantity,
                                             total_cores_number,
                                             vasp,
                                             vasp_log)
  elif sys_type  == 'direct':
    vasp6_omp_cups = calc_para_list["vasp6_omp_cups"]
    vasp_process_num = total_cores_number // vasp6_omp_cups
    process_per_node = vasp_process_num // nodes_quantity
    command = "export OMP_NUM_THREADS=%d; \
               mpirun  -ppn %d -np %d %s >> %s" \
               %(vasp6_omp_cups, process_per_node,
                 vasp_process_num, vasp, vasp_log)
  
  start_time = time.time()
  _ = os.system("date >> %s" %vasp_log)
  _ = os.system(intel_module + '; ' + command)
  _ = os.system("date >> %s" %vasp_log)
  end_time = time.time()
  time_spend = end_time - start_time
  return time_spend


def res_collect(filename_list, time_spend, task_tag):
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
  lcs = lines[lc_index].split()
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
  atom_num = atom_num.split()
  atom_num = [int(val) for val in atom_num]
  atom_num = sum(atom_num)
  force_per_atoms = grep('total drift', 'OUTCAR')
  force_per_atom = force_per_atoms[-1].split(':')[1].split()
  force_per_atom[0] = float(force_per_atom[0])/atom_num
  force_per_atom[1] = float(force_per_atom[1])/atom_num
  force_per_atom[2] = float(force_per_atom[2])/atom_num
  # Total magnet
  total_mags = grep('mag=', 'OSZICAR')
  total_mag = total_mags[-1].split('=')[4].split()
  if len(total_mag) == 3:
    total_mag = (float(total_mag[0])**2 + \
                 float(total_mag[1])**2 + \
                 float(total_mag[2])**2)**0.5
  else:
    total_mag = float(total_mag[0])
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
    json.dump(res_record, jfwp, indent=2)
  with open('RUN_TIME', 'w') as fwp:
    fwp.write('%f\n' %time_spend)
  return 0


def relax(filename_list, calc_para_list, task_index):
  relax_folder = filename_list["relax_folder"]
  relax_vasp = calc_para_list["relax_vasp"]
  task_list = calc_para_list["task_list"]
  index_relax_folder = "%d-%s" %(task_index, relax_folder)
  if file_exist('-' + relax_folder):
    print("[info] Folder %s already exist, skip." %relax_folder)
    command = "mv *-%s %s" %(relax_folder, index_relax_folder)
    _ = os.system(command)
    # Recollect the result 
    os.chdir(index_relax_folder)
    with open("RUN_TIME") as frp:
      time_spend = float(frp.readlines()[0].replace('\n',''))
    res_collect(filename_list, time_spend, 'relax')
    os.chdir('..')
    task_index += 1
  elif task_list[0] != 'T':
    print("[info] Relax not include in the task list, abandon this step...")
  else:
    print("[do] Calculate vasp relax...")
    # File prepare
    os.mkdir(index_relax_folder)
    os.chdir(index_relax_folder)
    _ = os.system('cp ../INCAR.RELAX INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.RELAX KPOINTS')
    # Job Submit
    time_spend = mpirun(filename_list, calc_para_list, relax_vasp)
    # Res. Collect
    _ = os.system("cp CONTCAR ../POSCAR.RELAXED")
    _ = os.system("cp CONTCAR ../POSCAR")
    res_collect(filename_list, time_spend, 'relax')
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def ssc(filename_list, calc_para_list, task_index):
  ssc_folder = filename_list["ssc_folder"]
  ssc_vasp = calc_para_list["ssc_vasp"]
  task_list = calc_para_list["task_list"]
  index_ssc_folder = "%d-%s" %(task_index, ssc_folder)
  if file_exist('-' + ssc_folder):
    print("[info] Folder %s already exist, skip." %ssc_folder)
    command = "mv *-%s %s" %(ssc_folder, index_ssc_folder)
    _ = os.system(command)
    # Recollect the result
    os.chdir(index_ssc_folder)
    with open("RUN_TIME") as frp:
      time_spend = float(frp.readlines()[0].replace('\n',''))
    res_collect(filename_list, time_spend, 'ssc')
    os.chdir('..')
    task_index += 1
  elif task_list[1] != 'T':
    print("[info SSC not include in the task list, abandon this step...")
  else:
    print("[do] Calculate vasp ssc...")
    # File prepare
    os.mkdir(index_ssc_folder)
    os.chdir(index_ssc_folder)
    _ = os.system('cp ../INCAR.SSC INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.SSC KPOINTS')
    # Job Submit
    time_spend = mpirun(filename_list, calc_para_list, ssc_vasp)
    # Res. Collect
    res_collect(filename_list, time_spend, 'ssc')
    # Quit Dir.
    os.chdir('..')
    task_index += 1
  return task_index


def band_plot_collect(filename_list, calc_para_list, path_list, mode):
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
  if mode == 'scan':
    vaspkit_band_code = '252'
    vaspkit_pband_code = '254'
  else: #pbe mode
    vaspkit_band_code = '211'
    vaspkit_pband_code = '213'
  # Total Band 
  command = '(echo %s; echo 0) | %s >> %s' \
            %(vaspkit_band_code, vaspkit, vaspkit_log)
  _ = os.system(command)
  # Projected Band
  command = '(echo %s) | %s >> %s' %(vaspkit_pband_code, vaspkit, vaspkit_log)
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
  _ = os.system("rm band_plot.py 2>/dev/null")
  _ = os.system("ln -s %s band_plot.py" %band_plot_script)
  os.chdir(curr_path)
  return 0


def pbe_band(filename_list, calc_para_list, path_list, task_index):
  band_folder = filename_list["band_folder"]
  ssc_folder = filename_list["ssc_folder"]
  band_vasp = calc_para_list["ssc_vasp"]
  index_band_folder = "%d-%s" %(task_index, band_folder)
  # File prepare
  os.mkdir(index_band_folder)
  os.chdir(index_band_folder)
  _ = os.system('cp ../INCAR.BAND INCAR')
  _ = os.system('ln -s ../POTCAR POTCAR')
  _ = os.system('cp ../POSCAR .')
  _ = os.system('cp ../KPOINTS.BAND KPOINTS')
  chgcar = '../%d-%s/CHGCAR' %(task_index-1, ssc_folder)
  if os.stat(chgcar).st_size == 0:
    print("[error] CHGCAR is empty, cannot calculate scan band...")
    sys.exit(1)
  _ = os.system('ln -s %s CHGCAR' %chgcar)
  _ = os.system('ln -s ../*-%s/DOSCAR DOSCAR.SSC' %ssc_folder)
  # Job Submit
  time_spend = mpirun(filename_list, calc_para_list, band_vasp)
  # Res. Collect
  res_collect(filename_list, time_spend, 'band')
  _ = os.system('mv DOSCAR DOSCAR.BAND')
  _ = os.system('mv DOSCAR.SSC DOSCAR')
  band_plot_collect(filename_list, calc_para_list, path_list, 'pbe')
  # Quit Dir.
  os.chdir('..')
  task_index += 1
  return task_index


def get_kpath_ibzk():
  with open('KPATH.in') as frp:
    lines = frp.readlines()
  kpoints_per_path = int(lines[1].replace(' ','').replace('\n',''))
  kpath_ibzk_origin_lines = lines[4:]
  kiols = []
  for kiol in kpath_ibzk_origin_lines:
    if (kiol.replace(' ','').replace('\n','') == ''):
      continue
    kiols.append(kiol)
  kpath_num = len(kiols)
  if kpath_num%2 == 1:
    print("[error] KPOINTS.BAND error, the kpath lines number is odd...")
    sys.exit(1)
  kpath_num //= 2
  kpath_ibzk_lines = []
  for kpath_index in range(kpath_num):
    hsk_beg_index = 2 * kpath_index
    hsk_end_index = 2 * kpath_index + 1
    hsk_begin = kiols[hsk_beg_index].split()[:3]
    hsk_begin = [float(val) for val in hsk_begin]
    hsk_end = kiols[hsk_end_index].split()[:3]
    hsk_end = [float(val) for val in hsk_end]
    hsk_array = [
      hsk_end[0] - hsk_begin[0],
      hsk_end[1] - hsk_begin[1],
      hsk_end[2] - hsk_begin[2]
    ]
    for index in range(kpoints_per_path):
      kx = hsk_begin[0] + (index/(kpoints_per_path-1)) * hsk_array[0] 
      ky = hsk_begin[1] + (index/(kpoints_per_path-1)) * hsk_array[1]
      kz = hsk_begin[2] + (index/(kpoints_per_path-1)) * hsk_array[2]
      kpath_ibzk_line = '%.8f  %.8f  %.8f  0' %(kx, ky, kz)
      kpath_ibzk_lines.append(kpath_ibzk_line)
  return kpath_num, kpoints_per_path, kpath_ibzk_lines


def combine_ssc_band_kpoints():
  with open('KPOINTS.SSC') as frp:
    lines = frp.readlines()
  try:
    kgrid = lines[3].replace('\n','')
    kgrid = kgrid.split()
    kgrid = [int(val) for val in kgrid[0:3]]
  except BaseException:
    print("[error] Cannot read the kgrid from KPOINTS.SSC.")
    print("[error] Please make sure the KPOINTS.SSC is under the grid mode.")
  with open('IBZKPT.SSC') as frp:
    lines = frp.readlines()
  ssc_kp_num = int(lines[1].replace(' ','').replace('\n',''))
  ssc_ibzk_lines = lines[3:(ssc_kp_num+3)]
  ssc_ibzk_lines = [val.replace('\n','') for val in ssc_ibzk_lines]
  kpath_num, kpoints_per_path, kpath_ibzk_lines = get_kpath_ibzk()
  band_kp_num = kpath_num * kpoints_per_path
  total_kpoints_lines_num = ssc_kp_num + band_kp_num
  # Write the KPOINTS for SCAN band
  kpath_kpoints_str = ''
  for _ in range(kpath_num):
    kpath_kpoints_str += '%d '%kpoints_per_path
  paras_line = '-9999  %d %d %d  %d  -9999  %d  %d  %s'%(kgrid[0], kgrid[1], kgrid[2], ssc_kp_num, band_kp_num, kpath_num, kpath_kpoints_str)
  with open('KPOINTS', 'w') as fwp:
    fwp.write('%s\n'%(paras_line))
    fwp.write('      %d\n'%(total_kpoints_lines_num))
    fwp.write('Reciprocal lattice\n')
    for ssc_ibzk_line in ssc_ibzk_lines:
      fwp.write(ssc_ibzk_line + '\n')
    for kpath_ibzk_line in kpath_ibzk_lines:
      fwp.write(kpath_ibzk_line + '\n')
  return 0


def scan_band(filename_list, calc_para_list, path_list, task_index):
  band_folder = filename_list["band_folder"]
  ssc_folder = filename_list["ssc_folder"]
  band_vasp = calc_para_list["ssc_vasp"]
  index_band_folder = "%d-%s" %(task_index, band_folder)
  # File prepare
  os.mkdir(index_band_folder)
  os.chdir(index_band_folder)
  _ = os.system('cp ../INCAR.BAND INCAR')
  _ = os.system('ln -s ../POTCAR POTCAR')
  _ = os.system('cp ../POSCAR .')
  _ = os.system('cp ../KPOINTS.BAND KPATH.in')
  _ = os.system('cp ../KPOINTS.SSC KPOINTS.SSC')
  ibzkpt = '../%d-%s/IBZKPT'%(task_index-1, ssc_folder)
  if not os.path.isfile(ibzkpt):
      print("[error] No IBZKPT file was found in SSC folder...")
      print("[error] Please make sure the KPOINTS.SSC is under the grid mode.")
      sys.exit(1)
  _ = os.system('cp %s IBZKPT.SSC' %ibzkpt)
  combine_ssc_band_kpoints()
  wavecar = "../%d-%s/WAVECAR" %(task_index-1, ssc_folder)
  if os.stat(wavecar).st_size == 0:
    print("[error] WAVECAR is empty, cannot calculate scan band...")
    sys.exit(1)
  _ = os.system('ln -s %s WAVECAR' %wavecar)
  # Job Submit
  time_spend = mpirun(filename_list, calc_para_list, band_vasp)
  # Res. Collect
  res_collect(filename_list, time_spend, 'band')
  band_plot_collect(filename_list, calc_para_list, path_list, 'scan')
  # Quit Dir.
  os.chdir('..')
  task_index += 1
  return task_index


def band(filename_list, calc_para_list, path_list, task_index):
  band_folder = filename_list["band_folder"]
  task_list = calc_para_list["task_list"]
  index_band_folder = "%d-%s" %(task_index, band_folder)
  if os.path.isfile('INCAR.BAND'):
    band_mode = 'pbe'
    with open('INCAR.BAND') as frp:
      lines = frp.readlines()
    for line in lines:
      upl = line.upper()
      upl = upl.split('#')[0]
      if ('METAGGA' in upl) and ('SCAN' in upl):
        band_mode = 'scan'
        break
  if file_exist('-' + band_folder):
    print("[info] Folder %s already exist, skip." %band_folder)
    command = "mv *-%s %s" %(band_folder, index_band_folder)
    _ = os.system(command)
    # Recollect the result 
    os.chdir(index_band_folder)
    with open("RUN_TIME") as frp:
      time_spend = float(frp.readlines()[0].replace('\n',''))
    res_collect(filename_list, time_spend, 'band')
    band_plot_collect(filename_list, calc_para_list, path_list, band_mode)
    os.chdir('..')
    task_index += 1
  elif task_list[2] != 'T':
    print("[info] Band not include in the task list, abandon this step...")
  else:
    if band_mode == 'scan':
      print("[do] Calculate SCAN band ...")
      task_index = scan_band(filename_list, calc_para_list, 
                             path_list, task_index)
    else:
      print("[do] Calculate PBE band ...")
      task_index = pbe_band(filename_list, calc_para_list, 
                            path_list, task_index)
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
  _ = os.system("rm dos_plot.py 2>/dev/null")
  _ = os.system("ln -s %s dos_plot.py" %dos_plot_script)
  os.chdir(curr_path)
  return 0


def dos(filename_list, calc_para_list, path_list, task_index):
  dos_folder = filename_list["dos_folder"]
  ssc_folder = filename_list["ssc_folder"]
  dos_vasp = calc_para_list["ssc_vasp"]
  task_list = calc_para_list["task_list"]
  index_dos_folder = "%d-%s" %(task_index, dos_folder)
  if file_exist('-' + dos_folder):
    print("[info] Folder %s already exist, skip." %dos_folder)
    command = "mv *-%s %s" %(dos_folder, index_dos_folder)
    _ = os.system(command)
    os.chdir(index_dos_folder)
    with open("RUN_TIME") as frp:
      time_spend = float(frp.readlines()[0].replace('\n',''))
    res_collect(filename_list, time_spend, 'dos')
    dos_plot_collect(filename_list, calc_para_list, path_list)
    os.chdir('..')
    task_index += 1
  elif task_list[3] != 'T':
    print("[info] DOS not include in the task list, abandon this step...")
  else:
    print("[do] Calculate vasp dos...")
    # File prepare
    os.mkdir(index_dos_folder)
    os.chdir(index_dos_folder)
    _ = os.system('cp ../INCAR.DOS INCAR')
    _ = os.system('ln -s ../POTCAR POTCAR')
    _ = os.system('cp ../POSCAR .')
    _ = os.system('cp ../KPOINTS.DOS KPOINTS')
    _ = os.system('ln -s ../*-%s/CHGCAR CHGCAR' %ssc_folder)
    # Job Submit
    time_spend = mpirun(filename_list, calc_para_list, dos_vasp)
    # Res. Collect
    res_collect(filename_list, time_spend, 'dos')
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
  print('[done]')
  return 0


if __name__ == "__main__":
  main()
