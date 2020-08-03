# Author: Liyang@CMT
# Date: 2019.10.21
# Description: This python code is designed for calculate the fermi energy
#                and plot the dos structure use the vasp EIGENVAL file.
#              ::Input File::
#                - EIGENVAL
#                - KPOINTS
#                - OUTCAR
#              ::Output File::
#                - vasp.dos.png
#                - vasp.dos.json
# Usage: python3.7 dos_plot.py -u <max_energy> -d <min_energy>
#

import os
import sys
import getopt
import re
import matplotlib.pyplot as plt
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

def main(argv):
  # +----------------------+
  # | Command Line Options |
  # +----------------------+
  min_plot_energy = -6
  max_plot_energy = 6
  plot_format = 'png'
  plot_dpi = 400
  plot_filename = 'DOS'
  try:
      opts, args = getopt.getopt(argv, "hd:u:f:r:n:",
                                  ["min=", "max=", "format=", 
                                  "dpi=","name="])
  except getopt.GetoptError:
      print('dos_plot.py -n <filename> -d <E_min> -u <E_max> -f <PlotFormat>')
      sys.exit(2)
  del args
  for opt, arg in opts:
      if opt == '-h':
          print('dos_plot.py -n <filename> -d <E_min> -u <E_max> -f <PlotFormat>')
          sys.exit()
      elif opt in ("-d", "--min"):
          min_plot_energy = float(arg)
      elif opt in ("-u", "--max"):
          max_plot_energy = float(arg)
      elif opt in ("-f", "--format"):
          plot_format = arg
      elif opt in ("-r", "--dpi"):
          plot_dpi = int(arg.split(".")[0])
      elif opt in ("-n", "--name"):
          plot_filename = arg

  # +-------------------+
  # | DOS Data Read In |
  # +-------------------+
  ## Check the existance of the DOS Data
  if not os.path.isfile('TDOS.dat'):
      print("[error] TDOS.dat not found..")
      sys.exit(1)
  ## Spin Number
  spin_res = grep('TDOS-DOWN', 'TDOS.dat')
  if spin_res == []:
      spin_num = 1
  else:
      spin_num = 2
  # DOS data
  with open('TDOS.dat') as frp:
    lines = frp.readlines()
  energys = []
  if spin_num == 1: 
    doss = []
  elif spin_num == 2:
    up_doss = []
    dn_doss = []
  for line in lines:
    if '#' in line:
      continue
    line = line.replace('\n','')
    dos_data_line = list(filter(None, line.split(' ')))
    energys.append(float(dos_data_line[0]))
    if spin_num == 1:
      doss.append(float(dos_data_line[1]))
    elif spin_num == 2:
      up_doss.append(float(dos_data_line[1]))
      dn_doss.append(float(dos_data_line[2]))

  # +----------+
  # | DOS Plot |
  # +----------+
  ## Design the Figure
  # Set the Fonts
  plt.rcParams.update({'font.size': 14,
                      'font.family': 'STIXGeneral',
                      'mathtext.fontset': 'stix'})
  # Set the spacing between the axis and labels
  plt.rcParams['xtick.major.pad']='5'
  plt.rcParams['ytick.major.pad']='5'
  # Set the ticks 'inside' the axis
  plt.rcParams['xtick.direction'] = 'in'
  plt.rcParams['ytick.direction'] = 'in'
  # Create the figure and axis object
  fig = plt.figure()
  dos_plot = fig.add_subplot(1, 1, 1)
  # Set the range of plot
  x_min = min_plot_energy
  x_max = max_plot_energy
  plt.xlim(x_min, x_max)
  # Set the label of x and y axis
  plt.xlabel('Energy (eV)')
  plt.ylabel('Total DOS (a.u.)')
  # Plot the fermi energy surface with a dashed line
  plt.hlines(0.0, x_min, x_max, colors="black",
             linestyles="-", linewidth=0.7, zorder=3)
  # Grid 
  plt.grid(linestyle='--', linewidth=0.5)
  # Plot the dos Structure
  if spin_num == 1:
    x = energys
    y = doss
    dos_plot.plot(x, y, 'r-', linewidth=1.2)
  elif spin_num == 2:
    x = energys
    y = up_doss
    dos_plot.plot(x, y, 'r-', linewidth=1.2)
    x = energys
    y = dn_doss
    dos_plot.plot(x, y, '-', color='blue', linewidth=1.2)
  # Save the figure
  plot_dos_file_name = plot_filename + '.' + plot_format
  plt.savefig(plot_dos_file_name, format=plot_format, dpi=plot_dpi)
  
if __name__ == "__main__":
  main(sys.argv[1:])
