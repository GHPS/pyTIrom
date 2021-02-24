#!/usr/bin/env python3
# File: createImage.py
# Repository: pyTIrom
# Description: Create a TI-99 memory image from C, D, G and system roms.
# Author: GHPS
# License: GPL-3.0

import argparse
import hashlib
import os.path


def createRom(stOutputFile='',
              stCrom='', stDrom='', stGrom='', stRomPath='', stSystemromPath='',
              blCheck=False, blVerbose=False, blDiskIO=False, blSpeech=False):

    lsMemoryMap=[[None, None, None],
                 ['994AGROM.BIN',2**15,None, None],
                 [2**13,2**15, '994AROM.BIN', None, None]]

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
    if blDiskIO:
        lsMemoryMap[2][0]=os.path.join(stSystemromPath,'Disk.Bin')
    if blSpeech:
        lsMemoryMap.extend([[None],[os.path.join(stSystemromPath,'Spchrom.bin')]])

    if blCheck: blVerbose=True
    if blVerbose: print('-- Checking input files --')
    lsMissingFiles=[]
    for stInputFile in sorted(set([stFileName for lsOuterList in lsMemoryMap for stFileName in lsOuterList if type(stFileName) is str])):
        if blVerbose: print(f'Checking {stInputFile:<30s}' ,end=' ')
        if os.path.isfile(stInputFile):
            if blVerbose: print('found')
        else:
            if blVerbose: print('not found')
            lsMissingFiles.append(stInputFile)
    if blVerbose: print()

    if lsMissingFiles==[]:
        if blVerbose: print('-- Copying input files --\n\n|--------------\n|Image Map\n|--------------')
        with open(stOutputFile,'wb') as fOutputFile:
            for lsBlock in lsMemoryMap:
                iPaddingSize=2**16
                for vCurrentSegment in lsBlock:
                    if type(vCurrentSegment) is str:
                        if blVerbose: print(f'|  Copying {vCurrentSegment:<30s}' ,end=' ')
                        with open(vCurrentSegment,'rb') as fCurrentFile:
                            vSingleFile=fCurrentFile.read()
                            if blCheck:
                                stChecksum=hashlib.md5(vSingleFile).hexdigest()
                            fOutputFile.write(vSingleFile)
                        if blVerbose: print('done',end='')
                        iClustersCurrentFile=os.path.getsize(vCurrentSegment)
                        if blCheck: print(f', MD5 Checksum: {stChecksum}', end=' ')
                        if blVerbose: print(f' ({iClustersCurrentFile}k occupied)', sep='')
                        iPaddingSize-=iClustersCurrentFile
                    elif type(vCurrentSegment) is int:
                        if blVerbose: print(f'|  Filling reserved {vCurrentSegment}k.')
                        vEmptySegment=bytes([0]*vCurrentSegment)
                        fOutputFile.write(vEmptySegment)
                        iPaddingSize-=vCurrentSegment
                    else:
                        if iPaddingSize>0:
                            if blVerbose: print(f'|  Applying {iPaddingSize}k of padding.')
                            vPadding=bytes([0]*iPaddingSize)
                            fOutputFile.write(vPadding)
                            iPaddingSize=0
                if blVerbose: print('|--------------')
        if blVerbose: print(f'\nTarget ROM {stOutputFile} created',end='')
        if blCheck:
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
    vParser.add_argument('OutputFile', help="The memory image to be created.", type=str)
    vParser.add_argument('--Crom', help="The C Rom file to use.", type=str)
    vParser.add_argument('--Drom', help="The D Rom file to use.", type=str)
    vParser.add_argument('--Grom', help="The G Rom file to use.", type=str)
    vParser.add_argument('--romPath', help="The path to the all roms - C, D, G and system roms (default .).", type=str, default='')
    vParser.add_argument('--systemromPath',help="The path to the system roms. Takes precedence over --romPath (default .).", type=str, default='')
    vParser.add_argument("-c","--check", help='Checksum files - generate MD5 sums for input and output files (implies --verbose).',action="store_true")
    vParser.add_argument("-d","--diskIO", help='Support for disk I/O.', action="store_true")
    vParser.add_argument("-s","--speech", help='Support for speech synthesizer.', action="store_true")
    vParser.add_argument("-v","--verbose", help='Display respective actions and results.', action="store_true")
    lsArguments=vParser.parse_args()

    createRom(stOutputFile=lsArguments.OutputFile,
              stCrom=lsArguments.Crom, stDrom=lsArguments.Drom, stGrom=lsArguments.Grom, stRomPath=lsArguments.romPath, stSystemromPath=lsArguments.systemromPath,
              blCheck=lsArguments.check, blVerbose=lsArguments.verbose, blDiskIO=lsArguments.diskIO, blSpeech=lsArguments.speech)
