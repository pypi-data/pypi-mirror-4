""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.6.0
Author  : Stefano Covino
Date    : 25/10/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/05/2010) First version.
        : (15/07/2010) WCS added.
        : (24/08/2010) Minor correction and source list sorting.
        : (25/08/2010) Frame size.
        : (30/08/2010) Fits Headers.
        : (04/09/2010) New importing rules.
        : (27/09/2010) Eclipse sources added.
        : (28/09/2010) Named changed from ObjList to FitsImage and adapted to native source class. 
        : (29/09/2010) Naming rationalized.
        : (04/10/2010) Possibility to remove stars close to frame border.
        : (25/10/2010) Basic statistics for frames.
"""

import os

import numpy

from GetData import GetData
from GetHeader import GetHeader
from GetWCS import GetWCS
import FitsConstants as FitsConstants

from SRP.SRPFrames.SourceObjectsClass import SourceObjects
from SRP.SRPFrames.EclipseObjectClass import EclipseObjects
from SRP.SRPFrames.Pixel2WCS import Pixel2WCS


class FitsImage:
    def __init__ (self, fitsfile):
        self.Name = fitsfile
        self.Header = GetHeader(fitsfile)[0]
        self.Data = GetData(fitsfile)[0]
        self.WCS = GetWCS(fitsfile)[0]
        self.List = []
        self.NativeSourcesFlag = False
        self.EclipseSorcesFlag = False


    def Sources(self, threshold=5.0, filtsing=3):
        slist = SourceObjects(self.Name)
        slist.FindObjects(self.Data, threshold, filtsing)
        srclist = []
        for i in slist.ListEntries:
            srclist.append((i.X,i.Y))
        coolist = Pixel2WCS(self.Header,srclist)
        for i,l in zip(slist.ListEntries,coolist):
            i.RA = l[0]
            i.DEC = l[1]
        self.List = slist.ListEntries
        self.NativeSourcesFlag = True
        self.EclipseSourcesFlag = False
        return len(self.List)
        
        
    def SortSourceList(self):
        if self.NativeSourcesFlag:
            self.List.sort()
            self.List.reverse()
        elif self.EclipseSourcesFlag:
            self.List.sort()
            self.List.reverse()
        
        
    def GetFrameSizePix(self):
        base = FitsConstants.NAxis
        sizelist = []
        try:
            naxis = self.Header[base]
        except KeyError:
            return None
        for i in range(naxis):
            baseax = '%s%s' % (base,i+1)
            try:
                value = self.Header[baseax]
            except KeyError:
                value = None
            sizelist.append(value)
        return sizelist

        
    def EclipseSources(self,level=2.0):
        elist = EclipseObjects(self.Name,level)
        elist.FindEclipseObjects()
        srclist = []
        for i in elist.ListEntries:
            srclist.append((i.X,i.Y))
        try:
            coolist = Pixel2WCS(self.Header,srclist)
        except AttributeError:
            coolist = []
            for ii in range(len(srclist)):
                coolist.append((0.,0.))
        for i,l in zip(elist.ListEntries,coolist):
            i.RA = l[0]
            i.DEC = l[1]
        self.List = elist.ListEntries
        self.EclipseSourcesFlag = True
        self.NativeSourcesFlag = False
        return len(self.List)


    def CleanBorderSources(self,cleaningpercentage=1):
        framesize = self.GetFrameSizePix()
        avoidzone = (framesize[0]*cleaningpercentage/100.,framesize[1]*cleaningpercentage/100.)
        CleanList = []
        oldnobj = len(self.List)
        for entry in self.List:
            if (1+avoidzone[0] <= entry.X <= framesize[0]-avoidzone[0]) and (1+avoidzone[1] <= entry.Y <= framesize[1]-avoidzone[1]):
                CleanList.append(entry)
        self.List = CleanList
        return len(self.List),oldnobj
        
        
    def __str__(self):
        msg = ''
        # Native
        if self.NativeSourcesFlag:
            for i in range(len(self.List)):
                msg = msg + str(self.List[i])
        # Eclipse
        elif self.EclipseSourcesFlag:
            for i in range(len(self.List)):
                self.List[i].Id = i+1
                msg = msg + str(self.List[i])
        return msg
        

    def Skycat(self, outname='SRP.cat'):
        msg = ''
        msg = msg + "long_name: SRP catalog for file %s\n" % (self.Name)
        msg = msg + "short_name: %s\n" % (outname)
        msg = msg + "url: ./%s\n" % (outname)
        msg = msg + "symbol: {} {circle blue} 4\n"
        msg = msg + "id_col: 0\n"
        msg = msg + "x_col: 1\n"
        msg = msg + "y_col: 2\n"
        # Native
        if self.NativeSourcesFlag:
            msg = msg + "Id\tX\tY\tRA\tDEC\tNPix\tMag\n"
        # Eclipse
        elif self.EclipseSourcesFlag:
            msg = msg + "Id\tX\tY\tNpix\tMin\tMax\tFW_X\tFW_Y\tFWHM\tFlux\tRA\tDEC\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def GetStats(self):
        mean = numpy.mean(self.Data)
        std = numpy.std(self.Data)
        median = numpy.median(self.Data)
        max = numpy.max(self.Data)
        return mean,std,median,max