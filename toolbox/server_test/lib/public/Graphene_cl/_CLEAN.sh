#!/bin/bash
#

read -p "Press <Enter> to confirm..."
rm -rf *-RELAX
rm -rf *-SSC
rm -rf *-BAND
rm -rf *-DOS
rm -rf RESULT
rm     POSCAR.*
rm     Graphene_cl.o*
rm     slurm-*.out
rm     cores-list
rm     vasp_submit.*.sh
rm     vr.allpara.json
rm     _KILLJOB.sh
rm     _CLEAN.sh 
