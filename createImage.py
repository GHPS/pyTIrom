#!/usr/bin/env python3
# File: createImage.py
# Description: Create a full TI-99 rom image from C, D, G and system roms.
# Version 1.7
# Author: GHPS
# License: GPL-3.0
# Versions
#  1.0 Initial release
#  1.1 Python 2 support
#  1.5 Support for romPath, systemromPath and MD5 checksums
#  1.6 Code refactoring: Allow use as a library
#  1.7 Removed Python 2 support due to end-of-life

import argparse
import hashlib
import os.path


def createRom(stOutputFile='',stCrom='',stDrom='',stGrom='',stRomPath='',stSystemromPath='',fCheck=False, fVerbose=False):
    lsMemoryMap=[['', '', ''],['994AGROM-EP.Bin', 'hole32k','', ''],['hole8k', 'hole32k', '994aROM.Bin', '', '']]
    if (stSystemromPath=='') and (stRomPath!=''):
        stSystemromPath=stRomPath

    if (stSystemromPath):
        lsMemoryMap[1][0]=os.path.join(stSystemromPath,lsMemoryMap[1][0])
        lsMemoryMap[2][2]=os.path.join(stSystemromPath,lsMemoryMap[2][2])
    if (stCrom is not None):
        lsMemoryMap[0][0]=os.path.join(stRomPath,stCrom)
    if (stDrom is not None):
        lsMemoryMap[0][1]=os.path.join(stRomPath,stDrom)
    if (stGrom is not None):
        lsMemoryMap[1][1]=os.path.join(stRomPath,stGrom)

    if fCheck: fVerbose=True
    if fVerbose: print('== Checking input files ==')
    lsMissingFiles=[]
    for stInputFile in sorted(set([stFileName for lsOuterList in lsMemoryMap for stFileName in lsOuterList if stFileName!=''])):
        if fVerbose: print('Checking %-27s' % stInputFile,end=' ')
        if os.path.isfile(stInputFile):
            if fVerbose: print('found')
        else:
            if fVerbose: print('not found')
            lsMissingFiles.append(stInputFile)
    if fVerbose: print()

    if lsMissingFiles==[]:
        if fVerbose: print('== Copying input files ==')
        with open(stOutputFile,'wb') as fOutputFile:
            for lsBlock in lsMemoryMap:
                iPaddingRequired=8
                for stCurrentFile in lsBlock:
                    if stCurrentFile!='':
                        if fVerbose: print('Copying %-28s' % stCurrentFile,end=' ')
                        with open(stCurrentFile,'rb') as fCurrentFile:
                            vSingleFile=fCurrentFile.read()
                            if fCheck:
                                stChecksum=hashlib.md5(vSingleFile).hexdigest()
                            fOutputFile.write(vSingleFile)
                        if fVerbose: print('done',end='')
                        iClustersCurrentFile=os.path.getsize(stCurrentFile)//8192
                        if fCheck: print(', MD5 Checksum:',stChecksum, end=' ')
                        if fVerbose: print(' (',iClustersCurrentFile,' cluster of 8k occupied)', sep='')
                        iPaddingRequired-=iClustersCurrentFile
                    else:
                        if iPaddingRequired>0:
                            if fVerbose: print('Padding',iPaddingRequired,'clusters of 8k')
                            for iFill in range(iPaddingRequired):
                                with open('hole8k','rb') as fCurrentFile:
                                    fOutputFile.write(fCurrentFile.read())
                            iPaddingRequired=0
                if fVerbose: print('-------')
        if fVerbose: print('Target ROM',stOutputFile,'created',end='')
        if fCheck:
            with open(stOutputFile,'rb') as fOutputFile:
                vSingleFile=fOutputFile.read()
                stChecksum=hashlib.md5(vSingleFile).hexdigest()
            print(', MD5 Checksum:',stChecksum)
        else:
            print('')
        iReturnCode=0
    else:
        print(len(lsMissingFiles),"files missing:",end=' ')
        print(*lsMissingFiles,sep=', ')
        print('No ROM file created')
        iReturnCode=66   # EX_NOINPUT
    return iReturnCode


if __name__ == "__main__":
    vParser = argparse.ArgumentParser()
    vParser.add_argument('OutputFile',help="The Full Rom file to be created.",type=str)
    vParser.add_argument('--Crom',help="The C Rom file to use.",type=str)
    vParser.add_argument('--Drom',help="The D Rom file to use.",type=str)
    vParser.add_argument('--Grom',help="The G Rom file to use.",type=str)
    vParser.add_argument('--romPath',help="The path to the all roms - C, D, G and system roms (default .).",type=str, default='')
    vParser.add_argument('--systemromPath',help="The path to the system roms. Takes precedence over --romPath (default .).",type=str, default='')
    vParser.add_argument("-c","--check", help='Checksum files - generate MD5 sums for input and output files (implies --verbose)',action="store_true")
    vParser.add_argument("-d","--diskIO", help='Support disk I/O (future feature).',action="store_true")
    vParser.add_argument("-s","--speech", help='Support speech synthesizer (future feature).',action="store_true")
    vParser.add_argument("-v","--verbose", help='Display respective actions and results.',action="store_true")
    lsArguments = vParser.parse_args()

    createRom(stOutputFile=lsArguments.OutputFile, stCrom=lsArguments.Crom,stDrom=lsArguments.Drom,stGrom=lsArguments.Grom,stRomPath=lsArguments.romPath,stSystemromPath=lsArguments.systemromPath,fCheck=lsArguments.check, fVerbose=lsArguments.verbose)
