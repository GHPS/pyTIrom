#!/usr/bin/env python3
# File: createImage.py
# Repository: pyTIrom
# Description: Create a full TI-99 rom image from C, D, G and system roms.
# Author: GHPS
# License: GPL-3.0

import argparse
import hashlib
import os.path


def createRom(stOutputFile='',stCrom='',stDrom='',stGrom='',stRomPath='',stSystemromPath='',fCheck=False, fVerbose=False, fDiskIO=False):

    lsMemoryMap=[[None, None, None],
                 ['994AGROM.BIN',32768,None, None],
                 [8192,32768, '994AROM.BIN', None, None]]

    if (stSystemromPath=='') and (stRomPath!=''):
        stSystemromPath=stRomPath

    if stSystemromPath:
        lsMemoryMap[1][0]=os.path.join(stSystemromPath,lsMemoryMap[1][0])
        lsMemoryMap[2][2]=os.path.join(stSystemromPath,lsMemoryMap[2][2])
    if stCrom:
        lsMemoryMap[0][0]=os.path.join(stRomPath,stCrom)
    if stDrom:
        lsMemoryMap[0][1]=os.path.join(stRomPath,stDrom)
    if stGrom:
        lsMemoryMap[1][1]=os.path.join(stRomPath,stGrom)
    if fDiskIO:
        lsMemoryMap[2][0]=os.path.join(stSystemromPath,'Disk.Bin')


    if fCheck: fVerbose=True
    if fVerbose: print('-- Checking input files --')
    lsMissingFiles=[]
    for stInputFile in sorted(set([stFileName for lsOuterList in lsMemoryMap for stFileName in lsOuterList if type(stFileName) is str])):
        if fVerbose: print(f'Checking {stInputFile:<30s}' ,end=' ')
        if os.path.isfile(stInputFile):
            if fVerbose: print('found')
        else:
            if fVerbose: print('not found')
            lsMissingFiles.append(stInputFile)
    if fVerbose: print()

    if lsMissingFiles==[]:
        if fVerbose: print('-- Copying input files --\n\nMemory Map\n-------')
        with open(stOutputFile,'wb') as fOutputFile:
            for lsBlock in lsMemoryMap:
                iPaddingSize=65536
                for vCurrentSegment in lsBlock:
                    if type(vCurrentSegment) is str:
                        if fVerbose: print(f'Copying {vCurrentSegment:<30s}' ,end=' ')
                        with open(vCurrentSegment,'rb') as fCurrentFile:
                            vSingleFile=fCurrentFile.read()
                            if fCheck:
                                stChecksum=hashlib.md5(vSingleFile).hexdigest()
                            fOutputFile.write(vSingleFile)
                        if fVerbose: print('done',end='')
                        iClustersCurrentFile=os.path.getsize(vCurrentSegment)
                        if fCheck: print(f', MD5 Checksum: {stChecksum}', end=' ')
                        if fVerbose: print(f' ({iClustersCurrentFile}k occupied)', sep='')
                        iPaddingSize-=iClustersCurrentFile
                    elif type(vCurrentSegment) is int:
                        if fVerbose: print(f'Filling reserved {vCurrentSegment}k.')
                        vEmptySegment=bytearray([0]*vCurrentSegment)
                        fOutputFile.write(vEmptySegment)
                        iPaddingSize-=vCurrentSegment
                    else:
                        if iPaddingSize>0:
                            if fVerbose: print(f'Applying {iPaddingSize}k of padding.')
                            vPadding=bytearray([0]*iPaddingSize)
                            fOutputFile.write(vPadding)
                            iPaddingSize=0
                if fVerbose: print('-------')
        if fVerbose: print(f'Target ROM {stOutputFile} created',end='')
        if fCheck:
            with open(stOutputFile,'rb') as fOutputFile:
                vSingleFile=fOutputFile.read()
                stChecksum=hashlib.md5(vSingleFile).hexdigest()
            print(f', MD5 Checksum: {stChecksum}')
        else:
            print('')
        iReturnCode=0
    else:
        print(f'{len(lsMissingFiles)} files missing:',end=' ')
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
    vParser.add_argument("-d","--diskIO", help='Support disk I/O (experimental feature).',action="store_true")
    vParser.add_argument("-s","--speech", help='Support speech synthesizer (future feature).',action="store_true")
    vParser.add_argument("-v","--verbose", help='Display respective actions and results.',action="store_true")
    lsArguments = vParser.parse_args()

    createRom(stOutputFile=lsArguments.OutputFile, stCrom=lsArguments.Crom,stDrom=lsArguments.Drom,stGrom=lsArguments.Grom,stRomPath=lsArguments.romPath,stSystemromPath=lsArguments.systemromPath,fCheck=lsArguments.check, fVerbose=lsArguments.verbose, fDiskIO=lsArguments.diskIO)
