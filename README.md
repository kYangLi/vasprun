# vasprun

## Basic Info

`Author` liyang@cmt.tsinghua

`Start Date` 2020.8.3

`Last Update` 2019.12.31

`Version` 1.2.0

## Description

A python script to submit the VASP calculation task in different job managemet system.

## Installtion

* Download the source code from:
https://github.com/kYangLi/vasprun/archive/master.zip

* Unzip it, and add the whole folder to the `PATH`. 
```bash
echo "export PATH=<vasprun>/<path>/:${PATH}" >> ~/.bashrc
```

## Input File
  
To enable this script, you need perpare the following files:

| File Name       | Necessarity | Descripution |
| --------------- |:-----------:|:------------ |
| `vr.input.json` | Optional  |vasprun input file|
| `POSCAR`        | Necessary |VASP POSCAR|
| `POTCAR`        | Necessary |VASP POTCAR|
| `KPOINTS.RELAX` | Optional  |VASP KPOINTS for relax step|
| `INCAR.RELAX`   | Optional  |VASP INCAR for relax step|
| `WAVECAR.RELAX` | Optional  |VASP WAVECAR for relax step to continue calculation|
| `CHGCAR.RELAX`  | Optional  |VASP CHGCAR for relax step to continue calculation|
| `KPOINTS.SSC`   | Optional  |VASP KPOINTS for static step|
| `INCAR.SSC`     | Optional  |VASP INCAR for static step|
| `WAVECAR.SSC`   | Optional  |VASP WAVECAR for static step to continue calculation|
| `CHGCAR.SSC`    | Optional  |VASP CHGCAR for static step to continue calculation|
| `KPOINTS.BAND`  | Optional  |VASP KPOINTS for band step|
| `INCAR.BAND`    | Optional  |VASP INCAR for band step|
| `KPOINTS.DOS`   | Optional  |VASP KPOINTS for DOS step|
| `INCAR.DOS`     | Optional  |VASP INCAR for DOS step|

### `vr.input.json`
The `vr.input.json` contains the necessary parameters for a VASP task. 
Here is an example of the `vr.input.json`:
```json
{ 
  "task_name": "vasprun",
  "task_list": "TTTT",
  "prog_module": "ml intel/20u1",
  "vasp_exec": "/home/bin/vasp_ncl",
  "vaspkit": "/home/bin/vaspkit-1.12",
  "sys_type": "pbs",
  "cores_per_node": 24,
  "nodes_quantity": 1,
  "openmp_cores": 1,
  "job_walltime": 48,
  "job_queue": "unset-queue",
  "plot_energy_window": [
    -2,
    2
  ]
}
```
You can run the vasprun main script to check their meaning.

### `POSCAR`
VASP POSCAR file.

### `POTCAR`
VASP POTCAR file.

### `INCAR.[tag]`
VASP INCAR file, where the tag = `RELAX`, `SSC`, `BAND`, `DOS`

### `KPOINTS.[tag]`
VASP KPOINTS file, where the tag = `RELAX`, `SSC`, `BAND`, `DOS`

### `WAVECAR.*` `CHGCAR.*`
Files for VASP continue calculation.

## Supported Task
- VASP atomic structure relax
- VASP electronic static self-consistent 
- VASP DFT+U band
- VASP SCAN band
- VASP DOS

## Submit the Task
After prepare the necessary file, just run `vasprun` in the calculation folder to submit the task.

## Calc. Result
The calcualtion result can be found in the folder `RESULT`.

## Kill the Job
```bash
./_KILLJOBS.sh
```

## Clean the Foder to Initial
```bash
./_CLEAN.sh
```
