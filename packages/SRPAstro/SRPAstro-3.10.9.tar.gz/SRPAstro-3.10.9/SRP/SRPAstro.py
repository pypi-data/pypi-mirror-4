""" Utility functions and classes for SRP

Context : SRP
Module  : SRPAstro.py
Version : 1.5.4
Status  : approved
Author  : Stefano Covino
Date    : 20/12/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/~covino
Purpose : Collection of utility functions and classes for SRP.

Usage   : to be imported

Remarks :

History : (19/10/2008) First version.
        : (05/11/2008) Sky in MiPhotdata class.
        : (19/11/2008) Many more minor issues and average sigma-clipping for arrays.
        : (20/11/2008) Better sky estimate and sorting of output file.
        : (27/11/2008) Better center moment estimate.
        : (03/01/2009) Better error estimate.
        : (17/04/2009) Better centering algorithm. MinMax function added.
        : (10/10/2009) Management of negative net fluxes.
        : (12/11/2009) Better (simpler) zero point determination.
        : (25/02/2010) RON in electrons.
        : (21/05/2010) Better sigma clipping algorithm.
        : (17/06/2010) Better managment of objects close to the frame boundaries.
        : (20/06/2010) Better centroid determination.
        : (22/06/2010) Minor improvement.
        : (20/12/2010) Import style corrected.

"""

import math, random, os, copy, sys
import pyfits
from scipy.optimize import fmin
#import scipy.stats
import SRPUtil
import SRP.stats as stats
from SRP.SRPStatistics.AverIterSigmaClipp import AverIterSigmaClipp


class MiPhotData:
        def __init__ (self, Id, x0, y0, max, mag, emag, saturation=55000, exptime=1.0, zp=(25.0,0.0), mjd=-99.0, etm=-99.0, sky=0.0, airm=(1.0,0.0), tmg=0.0, etmg=0.0, calsts=(1.0,0.0), cmt='N'):
                self.Id = Id
                self.XC = float(x0)
                self.YC = float(y0)
                self.MAX = float(max)
                if float(mag) < 90:
                    self.Mag = float(mag)+2.5*math.log10(exptime)
                else:
                    self.Mag = float(mag)
                self.eMag = float(emag)
                self.MagCal = self.Mag+float(zp[0])
                self.eMagCal = math.sqrt(self.eMag**2+float(zp[1])**2)
                self.Comment = cmt
#                if self.MAX < saturation and self.Mag < 90:
#                        self.Comment = 'Ok'
#                elif self.MAX >= saturation:
#                        self.Comment = 'S'
                self.MJD = float(mjd)
                self.Exptime = float(etm)
                self.Sky = float(sky)
                self.ZP = float(zp[0])
                self.eZP = float(zp[1])
		self.ChiZP = float(calsts[0])
		self.NZP = int(calsts[1])
                self.Airm = float(airm[0])
                self.Coef = float(airm[1])
                self.TMag = float(tmg)
                self.eTMag = float(etmg)
                self.DM = 0.0
                self.eDM = 0.0
                
                
        def __str__ (self):
                msg = ''
                msg = msg + "%10s\t%7.2f\t%7.2f\t%10.2f\t" % (self.Id, self.XC, self.YC, self.MAX)
                msg = msg + "%7.3f\t%7.3f\t%7.3f\t%7.3f\t" % (self.Mag, self.eMag, self.MagCal, self.eMagCal)
                msg = msg + "%4s\t%15.6f\t%10.1f\t%10.2f\t" % (self.Comment, self.MJD, self.Exptime, self.Sky)
                msg = msg + "%7.3f\t%7.3f\t%7.3f\t%6d\t%7.2f\t%7.3f\t" % (self.ZP, self.eZP, self.ChiZP, self.NZP, self.Airm, self.Coef)
                msg = msg + "%7.3f\t%7.3f" % (self.DM, self.eDM)
                return msg+os.linesep

        
        def __cmp__ (self, other):
                if self.MJD > other.MJD:
                        return 1
                elif self.MJD == othr.MJD:
                        return 0
                else:
                        return -1
                


def BiGauss (x,y,x0,y0,A,sx,sy,B):
        return A*math.exp( (-(x-x0)**2)/(2*sx**2) + (-(y-y0)**2)/(2*sy**2) ) + B


def resid (pars,field):
        x0 = pars[0]
        y0 = pars[1]
        A = pars[2]
        sx = pars[3]
        sy = pars[4]
        B = pars[5]
        if sx < 0.0:
                sx = 0.0
        if sy < 0.0:
                sy = 0.0
        if x0 < 0.0:
                x0 = 0.0
        elif x0 > field.shape[1]:
                x0 = field.shape[1]
        if y0 < 0.0:
                y0 = 0.0
        elif y0 > field.shape[0]:
                y0 = field.shape[0]
        restot = 0.0
        for i in range(field.shape[1]):
                for l in range(field.shape[0]):
                        y = BiGauss(float(i+1),float(l+1),x0,y0,A,sx,sy,B)
                        restot = restot + (y-field[l,i])**2
        return restot


def centerGauss (table, x, y, r):
        if math.floor(x-r) < 1:
                xmin = 1
        else:
                xmin = int(math.floor(x-r))
        if math.ceil(x+r) > table.shape[1]:
                xmax = table.shape[1]
        else:
                xmax = int(math.ceil(x+r))
        if math.floor(y-r) < 1:
                ymin = 1
        else:
                ymin = int(math.floor(y-r)) 
        if math.ceil(y+r) > table.shape[0]:
                ymax = table.shape[0]
        else:
                ymax = int(math.ceil(y+r)) 
        field = table[(ymin-1):ymax,(xmin-1):xmax]
        init = [x-xmin,y-ymin,field[int(y-ymin),int(x-xmin)],r,r,field[0,0]]
        pars = fmin (resid, init, args=(field,), maxfun=10000, maxiter=10000, disp=0)
        return pars[0]+xmin-1, pars[1]+ymin-1, pars[2], 2.35*pars[3], 2.35*pars[4], pars[5]
      
        
 
 
def getBackground (table, x, y, rmin, rmax):
        if math.floor(x-rmax) < 1:
                xmin = 1
        else:
                xmin = int(math.floor(x-rmax))
        if math.ceil(x+rmax) > table.shape[1]:
                xmax = table.shape[1]
        else:
                xmax = int(math.ceil(x+rmax))
        if math.floor(y-rmax) < 1:
                ymin = 1
        else:
                ymin = int(math.floor(y-rmax)) 
        if math.ceil(y+rmax) > table.shape[0]:
                ymax = table.shape[0]
        else:
                ymax = int(math.ceil(y+rmax)) 
        field = table[ymin-1:ymax,xmin-1:xmax]
        pval = []
        for i in range(field.shape[1]):
                for l in range(field.shape[0]):
                        dist = math.sqrt((x-(l+xmin-0.5))**2+(y-(i+ymin-0.5))**2)
                        if rmin < dist < rmax:
                                pval.append((float(field[l,i]),1.0))
        sgl = AverIterSigmaClipp(pval)
        return sgl
 
 
 
 
def centerMoment (table, x, y, r):
        bck = getBackground(table,x,y,0,r)
        minmax = MinMax(table,x,y,r)
        if math.floor(x-r) < 1:
                xmin = 1
        else:
                xmin = int(math.floor(x-r))
        if math.ceil(x+r) > table.shape[1]:
                xmax = table.shape[1]
        else:
                xmax = int(math.ceil(x+r))
        if math.floor(y-r) < 1:
                ymin = 1
        else:
                ymin = int(math.floor(y-r)) 
        if math.ceil(y+r) > table.shape[0]:
                ymax = table.shape[0]
        else:
                ymax = int(math.ceil(y+r))
#        for i in range(math.floor(y-r),math.ceil(y+r)):
#                for l in range(math.floor(x-r),math.ceil(x+r)):
#                        print l+1,i+1,table[l+1,i+1]
        field = table[(ymin-1):ymax,(xmin-1):xmax]
#        print field
        xc = 0.0
        yc = 0.0
        tot = 0.0
#        bckmin = bck[0]+(2.0/3.0)*(minmax[1]-bck[0])
        bckmin1 = bck[0]+2*bck[1]
        bckmin2 = minmax[1]
        if bckmin1 > minmax[1]:
            bckmin1 = minmax[1]
        for i in range(field.shape[1]):         # x
                for l in range(field.shape[0]): # y
                        if bckmin1 <= field[l,i] <= bckmin2:
                                xc = xc + i*(float(field[l,i])-bck[0])**2
                                yc = yc + l*(float(field[l,i])-bck[0])**2
                                tot = tot + (float(field[l,i])-bck[0])**2
        if tot != 0.0:
                return xc/tot+xmin, yc/tot+ymin
        else:
                return x, y
 
   

def findPercArea (x,y,r,xp,yp,ntrial=10000):
        good = 0
        for i in range(ntrial):
                xpp = random.uniform(xp-1,xp)
                ypp = random.uniform(yp-1,yp)
                dist = math.sqrt((x-xpp)**2+(y-ypp)**2)
                if dist <= r:
                        good = good + 1
        return float(good)/ntrial
   


def integFuct (a,b,x0,y0,r,y,plus=True):
#        print a,b,x0,y0,r,y
        fct1 = y0*(b-a)
        fct2 = 0.5*r**2 * (math.asin((b-x0)/r) - math.asin((a-x0)/r))
        fct3 = 0.5*( (b-x0)*math.sqrt(r**2-(b-x0)**2) - (a-x0)*math.sqrt(r**2-(a-x0)**2))
        subt = (b-a)*(y-1)
#        print fct1,fct2,fct3
        if plus:
                return fct1+fct2+fct3-subt
        else:
                return fct1-fct2-fct3-subt


def Funct (x,x0,y0,r,plus=True):
        if plus:
                return y0+math.sqrt(r**2-(x-x0)**2)
        else:
                return y0-math.sqrt(r**2-(x-x0)**2)
        
        

def findPercAreaBis (x,y,r,xp,yp):
        intersezioni = []
        xA = xp - 1
        sqr = r**2-(xA-x)**2
        if sqr >= 0:
                yA1 = y + math.sqrt(sqr)
                yA2 = y - math.sqrt(sqr)
                if yp-1 <= yA1 <= yp:
                        intersezioni.append((xA,yA1,True,1))
                if yp-1 <= yA2 <= yp:
                        intersezioni.append((xA,yA2,False,1))
        xB = xp
        sqr = r**2-(xB-x)**2
        if sqr >= 0: 
                yB1 = y + math.sqrt(sqr)
                yB2 = y - math.sqrt(sqr)
                if yp-1 <= yB1 <= yp:
                        intersezioni.append((xB,yB1,True,2))
                if yp-1 <= yB2 <= yp:
                        intersezioni.append((xB,yB2,False,2))
        yC = yp - 1
        sqr = r**2-(yC-y)**2
        if sqr >= 0.0:
                xC1 = x + math.sqrt(sqr)
                xC2 = x - math.sqrt(sqr)
                if xp-1 <= xC1 <= xp:
                        intersezioni.append((xC1,yC,True,3))
                if xp-1 <= xC2 <= xp:
                        intersezioni.append((xC2,yC,False,3))
        yD = yp
        sqr = r**2-(yD-y)**2
        if sqr >= 0.0: 
                xD1 = x + math.sqrt(sqr)
                xD2 = x - math.sqrt(sqr)        
                if xp-1 <= xD1 <= xp:
                        intersezioni.append((xD1,yD,True,4))
                if xp-1 <= xD2 <= xp:
                        intersezioni.append((xD2,yD,False,4))
        if len(intersezioni) == 2:
#                area = (intersezioni[0][1]-(yp-1)+intersezioni[1][1]-(yp-1))/2.0
                if yp-1 >= y or yp <= y:
                        if intersezioni[0][0] <= intersezioni[1][0]:
                                area1 = (intersezioni[0][0]-(xp-1))*(intersezioni[0][1]-(yp-1))
                                area3 = (xp-intersezioni[1][0])*(intersezioni[1][1]-(yp-1))
                                if yp-1 >= y:
                                        area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp)
                                elif yp <= y:
                                        area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp,False)                        
                        else:
                                area1 = (intersezioni[1][0]-(xp-1))*(intersezioni[1][1]-(yp-1))
                                area3 = (xp-intersezioni[0][0])*(intersezioni[0][1]-(yp-1))
                                if yp-1 >= y:
                                        area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp)
                                elif yp <= y:
                                        area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp,False)
                        area = area1 + area2 + area3
                else:
                        if xp-1 >= x:
                                if intersezioni[0][1] <= intersezioni[1][1]:
                                        area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp)
                                else:
                                        area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp)
                        else:
                                if intersezioni[0][1] <= intersezioni[1][1]:
                                        area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp,False)
                                else:
                                        area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp,False)   
#                print area
#                print intersezioni
#                print
#                if intersezioni[0][3] in [1,2]:
#                        print Funct(intersezioni[0][0],x,y,r,intersezioni[0][2])
#                else:
#                        print Funct(intersezioni[0][1],y,x,r,intersezioni[0][2])
#                if intersezioni[1][3] in [1,2]:
#                        print Funct(intersezioni[1][0],x,y,r,intersezioni[1][2])
#                else:
#                        print Funct(intersezioni[1][1],y,x,r,intersezioni[1][2])
                if yp-1 >= y:
                        return area
                elif yp <= y:
                        return 1.0-area
                else:
                        if xp-1 >= x:
                                return area
                        elif xp <= x:
                                return 1-area
        else:
                dist = math.sqrt((x-xp)**2+(y-yp)**2)
                if dist < r:
                        return 1.0
                else:
                        return 0.0
        
        
def sumApert (table, x, y, r):
        if math.floor(x-r) < 1:
                xmin = 1
        else:
                xmin = int(math.floor(x-r))
        if math.ceil(x+r) > table.shape[1]:
                xmax = table.shape[1]
        else:
                xmax = int(math.ceil(x+r))
        if math.floor(y-r) < 1:
                ymin = 1
        else:
                ymin = int(math.floor(y-r)) 
        if math.ceil(y+r) > table.shape[0]:
                ymax = table.shape[0]
        else:
                ymax = int(math.ceil(y+r)) 
        field = table[(ymin-1):ymax,(xmin-1):xmax]
        tot = 0.0
#        npix = 0
        npixbis = 0
        maxf = 0.0
        for i in range(field.shape[1]):
                for l in range(field.shape[0]):
                        dist = math.sqrt((x-(l+xmin-0.5))**2+(y-(i+ymin-0.5))**2)
                        if dist <= r-0.5*math.sqrt(2):
                                tot = tot + field[l,i]
#                                npix = npix + 1
                                npixbis = npixbis + 1
                                if field[l,i] > maxf:
                                        cy,cx = i,l
                                        maxf = field[l,i]
                        elif r-0.5*math.sqrt(2) < dist <= r+0.5*math.sqrt(2):
#                                pa = findPercArea (x,y,r,l+xmin,i+ymin)
                                pabis = findPercAreaBis (x,y,r,l+xmin,i+ymin)
                                tot = tot + pabis*field[l,i]
#                                npix = npix + pa
                                npixbis = npixbis + pabis
        if math.fabs((math.pi*r**2-npixbis)/npixbis) > 1.0:
                sys.exit(1)
        return tot, npixbis, maxf
     
     




def computeMag (flux,back,ebg,npix,gain=1.0,ron=0.0):
        nflux = flux-npix*back
        enflux = math.sqrt(math.fabs(flux)*gain + npix*(ebg*gain)**2 + npix*ron**2)
#        print nflux,enflux,flux,back,ebg,npix
        if nflux > 0.0:
            emag = (2.5/math.log(10.0))*enflux/(nflux*gain)
            mag = -2.5*math.log10(nflux)
        else:
            mag = 99.0
            emag = 99.0
        return mag,emag



## Average sigma clipping for arrays
#def averageSigmaClippingIter (wlst, siglev = 2.0):
#        if len(wlst) < 1:
#                return None,None,None
#        elif len(wlst) == 1:
#                return wlst[0],0.0,0.0 
#        limits = (None,None)
#	while True:
#		wa = scipy.stats.tmean(wlst,limits,(1,1))
#		ws = scipy.stats.tstd(wlst,limits,(1,1))
#		we = ws/math.sqrt(len(wlst))
#		wmin, wmax = wa - siglev*ws, wa + siglev*ws
#               newlimits = (wmin,wmax)
##		print wmin, wmax, limits, wa, ws, we
#	        if limits <> newlimits:
#			limits = newlimits
#		else:
#			return wa,ws,we



def AverWeight(wlst,wei):
        if len(wlst) == 0:
                return None, None
        elif len(wlst) == 1:
                return wlst[0],wei[0]
        sum = 0.0
        wsum = 0.0
        for i in range(len(wlst)):
                sum = sum + wlst[i]*wei[i]**-2
                wsum = wsum + wei[i]**-2
#                print wlst[i],wei[i]
        err = 0.0
        ave = sum/wsum
        for i in range(len(wlst)):
                err = err + (ave-wlst[i])**2
        errf = math.sqrt(err/(len(wlst)-1))
#        print ave, errf/math.sqrt(len(wlst))
        return ave, errf/math.sqrt(len(wlst))

        

def averageZeroPoint (inplst, einplst, siglev = 2.0):
	wlst = copy.copy(inplst)
        ewlst = copy.copy(einplst)
	card = len(wlst)
	while True:
#                print wlst
#                print ewlst
                if len(wlst) < 1:
                        return None,None
                elif len(wlst) == 1:
                        return wlst[0],ewlst[0]
                elif len(wlst) == 2:
                        return AverWeight(wlst,ewlst)
                elif 3 <= len(wlst) <= 10:
                        wa = stats.mean(wlst)
                        dst = 0.0
                        for i,l in zip(wlst,ewlst):
                                dstil = math.fabs(wa-i)/l
                                if dstil > dst:
                                        dst = dstil
                                        refi,refl = i,l
                        if dst > 3:
                                wlst.remove(refi)
                                ewlst.remove(refl)
#                                print wa,refi,refl,dst
                        else:
                                return AverWeight(wlst,ewlst)
                else:
        		wa = stats.mean(wlst)
        		ws = stats.samplestdev(wlst)
        		wmin, wmax = wa - siglev*ws, wa + siglev*ws
#                        print wa,ws,wmin,wmax
        		for i,l in zip(wlst,ewlst):
        			if not wmin <= i <= wmax:
        				wlst.remove(i)
                                        ewlst.remove(l)
        	        if card <> len(wlst):
        			card = len(wlst)
        		else:
                               return AverWeight(wlst,ewlst)



def simplerAverageZeroPoint (inplst, einplst):
	wlst = copy.copy(inplst)
        ewlst = copy.copy(einplst)
        if len(wlst) < 1:
            return None,None
        elif len(wlst) == 1:
            return wlst[0],ewlst[0]
        else:
            wl = stats.mean(wlst)
            ws = stats.samplestdev(wlst)
            we = ws/math.sqrt(len(wlst))
            return wl,we




def MinMax (table, x, y, r):
        if math.floor(x-r) < 1:
                xmin = 1
        else:
                xmin = int(math.floor(x-r))
        if math.ceil(x+r) > table.shape[1]:
                xmax = table.shape[1]
        else:
                xmax = int(math.ceil(x+r))
        if math.floor(y-r) < 1:
                ymin = 1
        else:
                ymin = int(math.floor(y-r)) 
        if math.ceil(y+r) > table.shape[0]:
                ymax = table.shape[0]
        else:
                ymax = int(math.ceil(y+r)) 
        field = table[(ymin-1):ymax,(xmin-1):xmax]
        maxf = field[0,0]
        minf = field[0,0]
        cMx,cMy = 0.0,0.0
        cmx,cmy = 0.0,0.0
        for i in range(field.shape[1]):
                for l in range(field.shape[0]):
                    if field[l,i] > maxf:
                        maxf = field[l,i]
                        cMx = i
                        cMy = l
                    if field[l,i] < minf:
                        minf = field[l,i]
                        cmx = i
                        cmy = l
        return minf, maxf, (cmx+xmin,cmy+ymin), (cMx+xmin,cMy+ymin)
