""" Utility functions and classes for SRP

Context : SRP
Module  : Frames.py
Version : 1.5.2
Author  : Stefano Covino
Date    : 22/01/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/09/2010) First version.
        : (28/09/2010) Minor name changes.
        : (29/09/2010) Minor correction.
        : (01/10/2010) Warning in saving FITS file suppressed.
        : (03/10/2010) Number of stars for astrometry. RA and DEC shift computed.
        : (04/10/2010) Sources close to frame border cleaned.
        : (13/10/2010) Larger search radius for catalogue object and no more maximum 
        :               number of objects.
        : (14/10/2010) Better estimate of frame size.
        : (24/10/2010) USNO-A2 catalogue also be used.
        : (25/10/2010) Flexible threshold for bad quality frames.
        : (27/10/2010) Simpler comment output.
        : (03/11/2010) Better comment formatting.
        : (17/11/2010) WCS header comments.
        : (20/11/2010) Better header formatting.
        : (31/12/2010) Minor bug correction.
        : (26/08/2011) Consistency check for unreliable CRVAL1,2 and CDELT1,2.
        : (04/11/2011) More flexibility in header coordinate format.
        : (22/01/2012) Check that at least one catalogue returns data.
"""


import copy, math, warnings

import pyfits
import astLib.astCoords as aLaC
import numpy
import scipy.optimize as so

import SRP
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPCatalogue.TWOMASSClass import TWOMASS
from SRP.SRPCatalogue.USNOClass import USNO
from SRP.SRPFits.FitsImageClass import FitsImage
from SRP.SRPFits import FitsConstants
from SRP.SRPMath.AngularDistance import AngularDistance
from SRP.SRPMath.AstroAngleInput import AstroAngleInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPMath.TriangleClass import Triangle
from SRP.SRPMath.TriangleMatch import TriangleMatch
from SRP.SRPStatistics.CoordDistanceMinimization import CoordDistanceMinimization
from SRP.SRPStatistics.SkyDistanceMinimization import SkyDistanceMinimization
from SRP.SRPStatistics.SkyDistanceMinimization import SkyDistSum
from SRP.SRPFrames.WCS2Pixel import WCS2Pixel
from SRP.SRPFrames.Pixel2WCS import Pixel2WCS


class Astrometry:
    def __init__ (self, fitsfile, center=None, pixcenter=None, point=None, pixsize=None, rotangle=None, framesize=None, maxres=3.0):
            # Fits file
            self.FitsFrame = FitsImage(fitsfile)
            # WCS
            # Pointing direction
            if point != None:
                pcoord = AstroCoordInput(point[0],point[1])
                self.RA = pcoord.RA
                self.DEC = pcoord.DEC
            else:
                try:
                    heacoord = AstroCoordInput(self.FitsFrame.Header[FitsConstants.RA],self.FitsFrame.Header[FitsConstants.DEC])
                except KeyError:
                    heacoord = AstroCoordInput(0.,0.)
                self.RA = heacoord.RA
                self.DEC = heacoord.DEC
            # Pixel reference
            if pixcenter != None:
                self.CRPIX1 = pixcenter[0]
                self.CRPIX2 = pixcenter[1]
            else:
                try:
                    self.CRPIX1 = self.FitsFrame.Header[FitsConstants.CRPIX1]
                    self.CRPIX2 = self.FitsFrame.Header[FitsConstants.CRPIX2]
                except KeyError:
                    self.CRPIX1 = 0.
                    self.CRPIX2 = 0.
            # Pixel size
            if pixsize != None:
                self.CDELT1 = pixsize[0]
                self.CDELT2 = pixsize[1]
            else:
                try:
                    self.CDELT1 = self.FitsFrame.Header[FitsConstants.CDELT1]
                    self.CDELT2 = self.FitsFrame.Header[FitsConstants.CDELT2]                    
                except KeyError:
                    self.CDELT1 = -1./3600.
                    self.CDELT2 = 1./3600.
            # check consistency of pixel size, it should not be larger than 0.1deg
            if math.fabs(self.CDELT1) > 0.1:
                self.CDELT1 = -1./3600.
            if math.fabs(self.CDELT2) > 0.1:
                self.CDELT2 = 1./3600.
            # Rotation angle
            if rotangle != None:
                angrad = math.radians(rotangle)
                self.RotationAngle = rotangle
                self.PC11 = math.cos(angrad)
                self.PC12 = -math.sin(angrad)
                self.PC21 = math.sin(angrad)
                self.PC22 = math.cos(angrad)
                self.pc = True
            else:
                try:
                    self.RotationAngle = self.FitsFrame.WCS.getRotationDeg()
                except AttributeError:
                    self.RotationAngle = 0.0
                try:
                    self.PC11 = self.FitsFrame.Header[FitsConstants.PC11]
                    self.PC12 = self.FitsFrame.Header[FitsConstants.PC12]
                    self.PC21 = self.FitsFrame.Header[FitsConstants.PC21]
                    self.PC22 = self.FitsFrame.Header[FitsConstants.PC22]
                    self.pc = True
                except KeyError:
                    self.PC11 = 1.
                    self.PC12 = 0.
                    self.PC21 = 0.
                    self.PC22 = 1.
                    self.pc = False
                try:
                    self.CD11 = self.FitsFrame.Header[FitsConstants.CD11]
                    self.CD12 = self.FitsFrame.Header[FitsConstants.CD12]
                    self.CD21 = self.FitsFrame.Header[FitsConstants.CD21]
                    self.CD22 = self.FitsFrame.Header[FitsConstants.CD22]
                    self.cd = True
                except KeyError:
                    self.cd = False
            if self.pc == False and self.cd == True:
                self.PC11 = self.CD11/self.CDELT1
                self.PC12 = self.CD12/self.CDELT2
                self.PC21 = self.CD21/self.CDELT1
                self.PC22 = self.CD22/self.CDELT2
            # Coordinate reference
            if center != None:
                coord = AstroCoordInput(center[0],center[1])
                self.CRVAL1 = coord.RA
                self.CRVAL2 = coord.DEC
            else:
                try:
                    heacoord = AstroCoordInput(self.FitsFrame.Header[FitsConstants.CRVAL1],self.FitsFrame.Header[FitsConstants.CRVAL2])
                    self.CRVAL1 = heacoord.RA
                    self.CRVAL2 = heacoord.DEC
                except KeyError:
                    self.CRVAL1 = self.RA
                    self.CRVAL2 = self.DEC
            # Check consistency between RA,DEC and CRVAL1,2
            if AngularDistance((self.RA,self.DEC),(self.CRVAL1,self.CRVAL2)) > 1.5:
                self.CRVAL1 = self.RA
                self.CRVAL2 = self.DEC
            # Image size
            sizelistpix = self.FitsFrame.GetFrameSizePix()
            if framesize != None:
                self.HalfSize = framesize/2.
            else:
                pxs = sum([math.fabs(i) for i in (self.CDELT1,self.CDELT2)])/2.0
                self.HalfSize = sum([i*pxs/2.0 for i in sizelistpix])/2.0
            #
            # Axes type
            try:
                self.CTYPE1 = self.FitsFrame.Header[FitsConstants.CTYPE1]
                self.CTYPE2 = self.FitsFrame.Header[FitsConstants.CTYPE2]
            except KeyError:
                self.CTYPE1 = FitsConstants.RAType
                self.CTYPE2 = FitsConstants.DECType
            # Strange CTYPES
            if self.CTYPE1 != FitsConstants.RAType or self.CTYPE1 != FitsConstants.DECType and self.CTYPE2 != FitsConstants.RAType or self.CTYPE2 != FitsConstants.DECType:
                self.CTYPE1 = FitsConstants.RAType
                self.CTYPE2 = FitsConstants.DECType   
            # Frame center
            self.FrameCenter = [(i/2.)+1.0 for i in sizelistpix]
            #
            self.List = []
            self.CatList = []
            self.Astrometrized = False
            self.Residuals = -1
            #
            self.MaxRes = maxres
            self.FitAstro = False
            self.TriAstro = False
            # Algorithms
            self.NativeSources = False
            self.EclipseSources = False
            #
            self.DefineWCSHeader()
                
                
    def GetSources(self, maxobjs=15, thre=23, mincnnt=3, cleanperc=1.):
            soglia = copy.copy(thre)
            while len(self.List) < maxobjs and soglia > 1: 
                self.FitsFrame.Sources(soglia,mincnnt)
                self.FitsFrame.CleanBorderSources(cleanperc)
                self.FitsFrame.SortSourceList()
                if len(self.FitsFrame.List) >= maxobjs:
                    self.List = self.FitsFrame.List[:maxobjs]
                else:
                    if soglia-5 > 3:
                        soglia = soglia - 5
                    elif soglia > 3:
                        soglia = 3
                    elif 2 < soglia <= 3:
                        soglia = soglia - 0.5
                    else:
                        soglia = soglia - 0.25
                    self.List = self.FitsFrame.List
            self.NativeSources = True
            self.EclipseSources = False


    def GetEclipseSources(self, maxobjs=15, thre=22, cleanperc=1.):
            soglia = copy.copy(thre)
            while len(self.List) < maxobjs and soglia > 0.1:
                self.FitsFrame.EclipseSources(soglia)
                self.FitsFrame.CleanBorderSources(cleanperc)
                self.FitsFrame.SortSourceList()
                if len(self.FitsFrame.List) >= maxobjs:
                    self.List = self.FitsFrame.List[:maxobjs]
                else:
                    if soglia-5 > 2:
                        soglia = soglia - 5
                    elif soglia > 2:
                        soglia = 2
                    elif 0.5 < soglia <= 2:
                        soglia = soglia - 0.5
                    else:
                        soglia = soglia - 0.1
                    self.List = self.FitsFrame.List
            self.EclipseSources = True
            self.NativeSources = False


                    
    def GetCatSources(self, maxentr=15, catq='N'): 
            radius = 1.5*self.HalfSize*60.0  # arcmin
            cntfld = (self.RA,self.DEC)
            if catq == 'N':
                cat = TWOMASS(cntfld[0], cntfld[1], math.floor(radius))
            elif catq == 'O':
                cat = USNO(cntfld[0], cntfld[1], math.floor(radius))
            else:
                cat = USNO(cntfld[0], cntfld[1], math.floor(radius))
            #
            if cat != None:
                cat.GetData()
                cat.sort()
                if len(cat.ListEntries) >= maxentr:
                    self.CatList = cat.ListEntries[:maxentr]
                else:
                    self.CatList = cat.ListEntries    


    def DefineWCSHeader(self):
        # remove alternate WCS
        del self.FitsFrame.Header[FitsConstants.CD11]
        del self.FitsFrame.Header[FitsConstants.CD12]
        del self.FitsFrame.Header[FitsConstants.CD21]
        del self.FitsFrame.Header[FitsConstants.CD22]
        # center ref
        self.FitsFrame.Header.update(FitsConstants.CRVAL1,self.CRVAL1,FitsConstants.CRVALCmt)
        self.FitsFrame.Header.update(FitsConstants.CRVAL2,self.CRVAL2,FitsConstants.CRVALCmt) 
        #             
        self.FitsFrame.Header.update(FitsConstants.CTYPE1,self.CTYPE1,FitsConstants.CTYPECmt)
        self.FitsFrame.Header.update(FitsConstants.CTYPE2,self.CTYPE2,FitsConstants.CTYPECmt)
        # rotation
        self.FitsFrame.Header.update(FitsConstants.PC11,self.PC11,FitsConstants.PCCmt)
        self.FitsFrame.Header.update(FitsConstants.PC12,self.PC12,FitsConstants.PCCmt)
        self.FitsFrame.Header.update(FitsConstants.PC21,self.PC21,FitsConstants.PCCmt)
        self.FitsFrame.Header.update(FitsConstants.PC22,self.PC22,FitsConstants.PCCmt)
        # pixel size
        self.FitsFrame.Header.update(FitsConstants.CDELT1,self.CDELT1,FitsConstants.CDELT1Cmt)
        self.FitsFrame.Header.update(FitsConstants.CDELT2,self.CDELT2,FitsConstants.CDELT2Cmt)  
        # pixel ref
        self.FitsFrame.Header.update(FitsConstants.CRPIX1,self.CRPIX1,FitsConstants.CRPIX1Cmt)
        self.FitsFrame.Header.update(FitsConstants.CRPIX2,self.CRPIX2,FitsConstants.CRPIX1Cmt)
        # pointing dir
        self.FitsFrame.Header.update(FitsConstants.RA,self.RA)
        self.FitsFrame.Header.update(FitsConstants.DEC,self.DEC)                        
        self.FitsFrame.Header.update(FitsConstants.RADECSys,FitsConstants.RADECSysVal)  
        self.FitsFrame.Header.update(FitsConstants.AngUnit1,FitsConstants.AngUnit1Val,FitsConstants.AngUnCmt)
        self.FitsFrame.Header.update(FitsConstants.AngUnit2,FitsConstants.AngUnit2Val,FitsConstants.AngUnCmt) 
        #
        self.FitsFrame.WCS.updateFromHeader()  
#        print self.CRVAL1, self.CRVAL2


    def UpgradeWCSHeader(self,(crpix1,crpix2,rot,sf)):
#        self.FitsFrame.Header.update(FitsConstants.CRVAL1,crval1)
#        self.FitsFrame.Header.update(FitsConstants.CRVAL2,crval2)              
#        self.FitsFrame.Header.update(FitsConstants.PC11,pc11)
#        self.FitsFrame.Header.update(FitsConstants.PC12,pc12)
#        self.FitsFrame.Header.update(FitsConstants.PC21,pc21)
#        self.FitsFrame.Header.update(FitsConstants.PC22,pc22)
        rotrnd = math.radians(rot)
        self.FitsFrame.Header.update(FitsConstants.PC11,math.cos(rotrnd))
        self.FitsFrame.Header.update(FitsConstants.PC12,-math.sin(rotrnd))
        self.FitsFrame.Header.update(FitsConstants.PC21,math.sin(rotrnd))
        self.FitsFrame.Header.update(FitsConstants.PC22,math.cos(rotrnd))
        if self.CDELT1 >= 0:
            cdelt1 = sf
        else:
            cdelt1 = -sf
        if self.CDELT2 >= 0:
            cdelt2 = sf
        else:
            cdelt2 = -sf
        self.FitsFrame.Header.update(FitsConstants.CDELT1,cdelt1)
        self.FitsFrame.Header.update(FitsConstants.CDELT2,cdelt2)  
        self.FitsFrame.Header.update(FitsConstants.CRPIX1,crpix1)
        self.FitsFrame.Header.update(FitsConstants.CRPIX2,crpix2)
        self.FitsFrame.WCS.updateFromHeader()            
  
              

#    def SkyDistSum (self, pars, oldvars, newvars):
#        tot = 0.0
#        self.UpgradeWCSHeader(pars)
#        newc = Pixel2WCS(self.FitsFrame.Header,oldvars)
#        for i,l in zip(newc,newvars):
#            tot = tot + aLaC.calcAngSepDeg(i[0],i[1],l[0],l[1])*3600.0
#        return tot


#    def SkyDistanceMinimization (self, guessparset, oldcoord, refcoord):
#        rc = numpy.array(refcoord)
#        oc = numpy.array(oldcoord)
#        xopt = so.fmin(self.SkyDistSum, guessparset, args=(oc,rc), disp=0, maxiter=10000, maxfun=10000)
#        return xopt, self.SkyDistSum(xopt,oc,rc)/len(oc)

    
    def ImproveWCS (self,(sx,sy,rot,sf)):
        self.CDELT1 = self.CDELT1 * sf
        self.CDELT2 = self.CDELT2 * sf
        self.CRPIX1 = self.CRPIX1 + sx
        self.CRPIX2 = self.CRPIX2 + sy
        self.RotationAngle = self.RotationAngle + rot
                    
                                    
    def FindSolution(self):
        reflist = []
        objlist = []
        # centering
        if self.NativeSources:
            for i in self.List:
                objlist.append(((i[0]-self.CRPIX1),(i[1]-self.CRPIX2)))
                #print objlist[-1]
        elif self.EclipseSources:
            for i in self.List:
                objlist.append(((i.X-self.CRPIX1),(i.Y-self.CRPIX2)))
                #print objlist[-1]
                #print i.flux
        #print 
        radec = []
        for i in self.CatList:
            radec.append((i.RA,i.DEC))
            #print i.H
        RefPos = WCS2Pixel(self.FitsFrame.Header,[(self.CRVAL1,self.CRVAL2)])
        #print RefPos
        CatListPix = WCS2Pixel(self.FitsFrame.Header,radec)
        for i in CatListPix:
            reflist.append(((i[0]-RefPos[0][0]), (i[1]-RefPos[0][1])))
            #print reflist[-1]
        #
        mtchres = TriangleMatch(reflist,objlist)
        if mtchres != None:
#            print mtchres
            mtchinplist = []
            mtchoutlist = []
            for i in mtchres[0]:
                if self.NativeSources:
                    mtchinplist.append((self.List[i][0],self.List[i][1]))
                elif self.EclipseSources:
                    mtchinplist.append((self.List[i].X,self.List[i].Y))                
            for i in mtchres[1]:
                mtchoutlist.append((self.CatList[i].RA,self.CatList[i].DEC))
            self.NStarRes = len(mtchres[0])
            self.ImproveWCS(mtchres[2][0])
            ris = SkyDistSum((self.CRPIX1,self.CRPIX2,self.RotationAngle,math.fabs(self.CDELT1)),mtchinplist,mtchoutlist,self)/len(mtchoutlist)
            dataris = (self.CRPIX1,self.CRPIX2,self.RotationAngle,math.fabs(self.CDELT1))
#            print self.CRVAL1,self.CRVAL2,self.CRPIX1,self.CRPIX2,self.PC11,self.PC12,self.PC21,self.PC22,self.CDELT1,self.CDELT2
            res = SkyDistanceMinimization((self.CRPIX1,self.CRPIX2,self.RotationAngle,math.fabs(self.CDELT1)),mtchinplist,mtchoutlist,self)           
            self.Residuals = res[1]
            self.UpgradeWCSHeader(res[0])
#            print self.CRVAL1,self.CRVAL2,self.CRPIX1,self.CRPIX2,self.PC11,self.PC12,self.PC21,self.PC22,self.CDELT1,self.CDELT2
#            print ris,res[1]
            if self.Residuals <= self.MaxRes:
                self.Astrometrized = True
                self.FitAstro = True
            else:
                # try with no fit
                if ris < self.MaxRes:
                    self.Residuals = ris
                    self.UpgradeWCSHeader(dataris)
                    self.Astrometrized = True
                    self.TriAstro = True 
                else:
                    self.Astrometrized = False
            #
            self.GetPointingShift()
            #
        else:
            self.Astrometrized = False
            self.Residuals = -1
            self.NStarRes = 0
            


    def GetPointingShift(self):
        # derive true center coordinate
        ccord = Pixel2WCS(self.FitsFrame.Header,[(self.FrameCenter[0],self.FrameCenter[1])])
        self.RAshift = ((self.RA - ccord[0][0])*math.cos(math.radians(self.DEC)))*3600.0
        self.DECshift = (self.DEC - ccord[0][1])*3600.0

            
    def SaveFile(self,nfile):
        frm = pyfits.open(self.FitsFrame.Name)
        if self.Astrometrized:
            self.FitsFrame.Header.add_comment('SRPComment: Astrometric solution acceptable.') 
            self.FitsFrame.Header.add_comment('SRPComment: Average residual: %.2g arcsec for %d stars.' % (self.Residuals, self.NStarRes))  
            self.FitsFrame.Header.add_comment('SRPComment: Shift wrt pointing RA and DEC coords: %.1f %.1f arcsec.' % (self.RAshift, self.DECshift)) 
        else:
            self.FitsFrame.Header.add_comment('SRPComment: Astrometric solution not acceptable.') 
            self.FitsFrame.Header.add_comment('Average residual: %.2g arcsec for %d stars.' % (self.Residuals, self.NStarRes))              
        frm[0].header = self.FitsFrame.Header
        warnings.resetwarnings()
        warnings.filterwarnings('ignore', category=UserWarning, append=True)
        frm.writeto(nfile,clobber=True)
        warnings.resetwarnings() 
        warnings.filterwarnings('always', category=UserWarning, append=True)

