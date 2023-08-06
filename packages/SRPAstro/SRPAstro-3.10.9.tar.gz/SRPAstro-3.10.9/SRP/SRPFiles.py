""" Collections of constans, functions and classes for file managements.

Context : SRP
Module  : SRPFiles.py
Version : 1.7.4
Status  : approved
Author  : Stefano Covino, Nico Cucchiara
Date    : 21/05/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/~covino
Purpose : Collection of constants and functions for file managements.

Usage   : to be imported

Remarks :

History : (20/05/2003) First version.
        : (21/05/2003) Read session name function.
        : (08/09/2003) Flux-magnitude file
        : (09/09/2003) Wavelength to frequency conversion.
        : (20/09/2003) Check if a file is readable.
        : (01/10/2003) Reading absorpion data file.
        : (14/10/2003) Tool for pipe management.
        : (24/10/2003) Reading total file.
        : (12/10/2008) Minor correction.
        : (07/09/2009) python 2.6 upgrade.
        : (06/10/2009) Minor correction.
        : (17/06/2010) Better data file path management.
        : (21/03/2011) Better coding for extinction routines.
        : (16/08/2011) Absolute pathes correctly managed.
        : (05/02/2012) Better path management.
        : (21/05/2012) pipe function commented.
"""



import os, os.path, string, pickle
import sys
if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
    import subprocess
else:
    import popen2
import SRPConstants
import SRP
from SRP.SRPSystem.SRPPath import SRPPath



# Constants

ReadMode   = "r"
WriteMode  = "w"
AppendMode = "a"




# Classes

# Generic SRP file

class SRPFile:
    """SRP file.

    Parameters are dirname, filename and mode."""
    def __init__ (self, dirname, filename, mode):
        self.dirname = dirname          # Directory
        self.filename = filename        # File name
        self.mode = mode                # Mode
        self.f = None                   # File pointer

    def SRPOpenFile (self):
        """Open a SRP file.

        Create the directory if it does not exist, return None
        if file does not exist."""
        if len(self.filename) > 0 and self.filename[0] == os.sep:
            fullpath = self.filename
        else:
            fullpath = self.dirname+os.sep+self.filename
        if self.mode == ReadMode and os.path.isfile(fullpath):
            self.f = open(fullpath,self.mode)
        elif self.mode == WriteMode or self.mode == AppendMode:
            if os.path.isfile(self.dirname):
                os.remove(self.dirname)
            if not os.path.isdir(self.dirname):
                os.mkdir(self.dirname)
            self.f = open(fullpath,self.mode)
        else:
            self.f = None


    def SRPCloseFile (self):
        """Close a SRP file."""
        self.f.close()

    def SRPReadTotFile(self):
        """ Read all data from a SRP file."""
        return self.f.readlines()

    def SRPReadFile(self):
        """Read data from a SRP file."""
        return self.f.readline()

    def SRPReadFilePickle(self):
        """Read pickled data from a SRP file."""
        return pickle.load(self.f)

    def SRPWriteFile(self, data=os.linesep):
        self.f.write(str(data))

    def SRPWriteFilePickle(self, data=os.linesep):
        pickle.dump(data,self.f)



def getSRPSessionName():
    f = SRPFile(SRPConstants.SRPLocalDir,SRPConstants.SRPSessionName,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return SRPConstants.SRPStandardSessionName
    else:
        return f.SRPReadFile()



def getSRPFITSList(filename):
    list = []
    f = SRPFile(SRPConstants.SRPLocalDir,filename,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return list
    else:
        while True:
            ffile = f.SRPReadFile()
            if ffile != '':
                list.append(string.strip(ffile))
            else:
                break
        f.SRPCloseFile()
        return list



def getSRPKeyList(filename):
    list = []
    f = SRPFile(SRPConstants.SRPLocalDir,filename,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return list
    else:
        while True:
            fkey = f.SRPReadFile()
            if fkey != '':
                list.append(string.strip(fkey))
            else:
                break
        f.SRPCloseFile()
        return list



#def getSRPPath ():
#       felot = None
#       f = SRPFile(SRPConstants.SRPHomeDir,SRPConstants.SRPSetupFile,ReadMode)
#       f.SRPOpenFile()
#       if f.f == None:
#               return None
#       else:
#               while True:
#                       fe = f.SRPReadFile()
#                       if fe != '':
#                               if string.find(fe,'bin') >= 0:
#                                       fel = string.split(fe)[-1]
#                                       felo = os.path.split(fel)[0]
#                                       felot = os.path.join(felo,SRPConstants.SRPPyScrDir)
#                       else:
#                               break
#               f.SRPCloseFile()
#               return felot



def getSRPDataPath():
    return SRPPath()



def SRPLeggiMagCalFile (nomefile):
    # Leggi il file
    try:
        f = file(nomefile, "r")
    except:
        return [], [], [], []
    data = f.readlines()
    f.close()
    # Elimina le righe che cominciano con #
    dataclean = []
    for i in range(len(data)):
        if data[i][0] != '#':
            dataclean.append(data[i])
    # Leggi i valori
    banda = []
    l0 = []
    f0 = []
    n0 = []
    for i in range(len(dataclean)):
        valori = string.split(dataclean[i])
        banda.append(valori[0])
        try:
            l0.append(float(valori[1]))
            f0.append(float(valori[2]))
            n0.append(SRPConstants.Cspeed/l0[i])
        except:
            l0.append(SRPConstans.SRPMagErr)
            f0.append(SRPConstants.SRPMagErr)
            n0.append(SRPConstants.SRPMagErr)
    return banda, l0, f0, n0



def IsReadable (filename):
    return os.access(filename,os.R_OK)



#def LeggiAbsFile (nomefile,l):
    # Leggi il file
#    try:
#        f = file(nomefile, "r")
#    except:
#        return [], [], [], []
#    data = f.readlines()
#    f.close()
    # Elimina le righe che cominciano con #
#    dataclean = []
#    for i in range(len(data)):
#        if (data[i][0] != ' ' or data[i][0] != '#') and len(data[i]) > 1:
#            dataclean.append(data[i])
    #legge i valori
#    ai = []
#    li = []
#    bi = []
#    ni = []
#    for i in range(len(dataclean)):
#        if string.split(dataclean[i])[0] == l:
#            valori = string.split(dataclean[i])
#            try:
#                ai.append(float(valori[2]))
#                li.append(float(valori[3]))
#                bi.append(float(valori[4]))
#                ni.append(float(valori[5]))
#            except:
#                ai.append(SRPConstants.SRPMagErr)
#                li.append(SRPConstants.SRPMagErr)
#                bi.append(SRPConstants.SRPMagErr)
#                ni.append(SRPConstants.SRPMagErr)
#    return ai, li, bi, ni




# SRP pipe
#if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
#    def SRPPipe (file):
#        f = subprocess.Popen(file,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
#        ky = f.stdout.read()
#        estatus = f.wait()
#        del f
#        if os.WEXITSTATUS (estatus):
#            return None
#        else:
#            return ky
#else:
#    def SRPPipe (file):
#        f = popen2.Popen4(file)
#        ky = f.fromchild.read()
#        estatus = f.wait()
#        del f
#        if os.WEXITSTATUS (estatus):
#            return None
#        else:
#            return ky
