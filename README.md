# vasprun

## Basic Info

`Author` liyang@cmt.tsinghua

`Start Date` 2020.8.3

`Last Update` 2019.10.10

`Version` 1.1.0

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
- `vr.input.json` ==> (Optional)
- `POSCAR` =========> (Necessary)
- `POTCAR` =========> (Necessary)
- `KPOINTS.RELAX` ==> (Optional)
- `INCAR.RELAX` ====> (Optional)
- `WAVECAR.RELAX` ==> (Optional)
- `CHGCAR.RELAX` ===> (Optional)
- `KPOINTS.SSC` ====> (Optional)
- `INCAR.SSC` ======> (Optional)
- `WAVECAR.SSC` ====> (Optional)
- `CHGCAR.SSC` =====> (Optional)
- `KPOINTS.BAND` ===> (Optional)
- `INCAR.BAND` =====> (Optional)
- `KPOINTS.DOS` ====> (Optional)
- `INCAR.DOS` ======> (Optional)

### `vr.input.json`
The `vr.input.json` contains the necessary parameters for a VASP task.
Here is an example of the `vr.input.json`:
```json
{
  "task_name": "u3_cl-fm",
  "task_list": "TTTF",
  "intel_module": "ml intel/20u1",
  "relax_vasp": "/home/liyang1/Software/CalcProg/VASP/Main/vasp-544-patched_20u1/bin/vasp_ncl",
  "ssc_vasp": "/home/liyang1/Software/CalcProg/VASP/Main/vasp-544-patched_20u1/bin/vasp_ncl",
  "vaspkit": "/home/liyang1/Software/CalcProg/VASP/Tools/VaspKit/vaspkit-1.12/bin/vaspkit",
  "sys_type": "pbs",
  "cores_per_node": 24,
  "openmp_cpus": 1,
  "pbs_queue": "unset-pbs-queue",
  "nodes_quantity": 2,
  "pbs_walltime": 48,
  "plot_energy_window": [-2.0, 2.0]
}
```

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

## Result Output
The Calcualtion result can be found in the folder `RESULT`.

## Kill the Job
```bash
./_KILLJOBS.sh
```

## Clean the Foder to Initial
```bash
./_CLEAN.sh
```
