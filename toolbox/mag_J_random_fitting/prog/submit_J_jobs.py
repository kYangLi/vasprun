import random
import os
import sys
import json 
import numpy as np
import time 

def envs_check():
  '''Check the envriment'''
  # Check vasprun input files
  vr_in_files = ['vr.input.json', 'POSCAR', 'POTCAR', 
                 'INCAR.SSC', 'KPOINTS.SSC']
  for vr_in_file in vr_in_files:
    vr_in_file_path = os.path.join('calc','__origin',vr_in_files)
  if not os.path.isfile(vr_in_file_path):
    print("[error] File '%s' NOT found..." %vr_in_file_path)
    sys.exit(1)
  # Check fitting J input file
  if not os.path.isfile('ftj.input.json'):
    print("[error] File 'ftj.input.json' NOT found...")
    sys.exit(1)
  return 0

def read_input_json():
  with open("vr.input.json")