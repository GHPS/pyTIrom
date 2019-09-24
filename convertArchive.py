#!/usr/bin/env python3
# File: convertArchive.py
# Description: Create full TI-99 rom images from a directory containing C, D and G roms.
# Version 1.1
# Author: GHPS
# License: GPL-3.0
# Versions
#  1.0 Initial release
#  1.1 Removed Python 2 support due to end-of-life
#  1.2 More flexible naming scheme for input files

import argparse
import os
import sys
import glob
from datetime import datetime
from createImage import createRom


if __name__ == "__main__":
    vParser = argparse.ArgumentParser()
    vParser.add_argument('--romPath',help="The path to the roms - C, D, G (default .).",type=str, default='')
    vParser.add_argument('--fullromPath',help="The directory where the Rom files are created.",type=str,default='')
    vParser.add_argument('--systemromPath',help="The path to the system roms.",type=str, default='')
    vParser.add_argument("-c","--check", help='Checksum files - generate MD5 sums for input and output files (implies --verbose)',action="store_true")
    vParser.add_argument("-v","--verbose", help='Display respective actions and results.',action="store_true")
    lsArguments = vParser.parse_args()

    if lsArguments.fullromPath=='':
        lsArguments.fullromPath=lsArguments.romPath
        print(lsArguments.fullromPath)

    vStartTime=datetime.now()
    lsFiles=glob.glob(os.path.join(lsArguments.romPath,'*.[CDG]'))
    if lsArguments.romPath=='':
        iStartCartridgeName=0
    else:
        iStartCartridgeName=len(lsArguments.romPath)+1
    dcFiles={}
    for stFileName in lsFiles:
        if (stFileName.find('[a]')==-1) and (stFileName.find('[o]')==-1):
            iEndCartrigeName=stFileName.find(' (')
            if iEndCartrigeName!=-1:
                stCartrigeName=stFileName[iStartCartridgeName:iEndCartrigeName]
            else:
                print('** Warning: File mismatches naming scheme - continuing with complete file name **')
                stCartrigeName=stFileName[iStartCartridgeName:-2]
            if lsArguments.verbose: print('Adding',stFileName,'to',stCartrigeName)
            if stCartrigeName in dcFiles:
                dcFiles.update({stCartrigeName:dcFiles[stCartrigeName]+[stFileName]})
            else:
                dcFiles.update({stCartrigeName:[stFileName]})
    iCartridgesConverted=0
    iExitCode=0
    for stCartridgeName in sorted(dcFiles):
        stCromFileName=''
        stDromFileName=''
        stGromFileName=''
        for stFileName in dcFiles[stCartridgeName]:
            if stFileName[-1]=='C': stCromFileName=stFileName
            if stFileName[-1]=='D': stDromFileName=stFileName
            if stFileName[-1]=='G': stGromFileName=stFileName
        if lsArguments.verbose: print('Creating cartrige',stCartridgeName)
        iResult=createRom(stOutputFile=os.path.join(lsArguments.fullromPath,stCartridgeName)+'.bin', stCrom=stCromFileName,stDrom=stDromFileName,stGrom=stGromFileName,stSystemromPath=lsArguments.systemromPath,fCheck=lsArguments.check, fVerbose=lsArguments.verbose)
        if iResult==0:
            iCartridgesConverted+=1
        elif iExitCode==0:
            iExitCode=iResult
        print()
    if lsArguments.verbose:
        vTimeDelta=datetime.now()-vStartTime
        print(f'{iCartridgesConverted} cartridges created in {vTimeDelta.total_seconds():2.2f} seconds.')
    sys.exit(iExitCode)
