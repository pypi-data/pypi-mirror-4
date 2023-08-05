""" Utility functions and classes for SRP

Context : SRP
Module  : Frames.py
Version : 1.2.1
Author  : Stefano Covino
Date    : 18/10/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (25/06/2010) First version.
        : (24/08/2010) Possibility to choose the minimum number of pixel per source.
        :               and management of the 'total flux negative' case.
        : (28/09/2010) Upgraded code as a class.
        : (18/10/2010) Coding correction.
"""


import scipy.ndimage.measurements as snm
import astLib.astStats as aa
import math, os



# Source data
class SourceObjects:
    class Object:
        def __init__ (self, dlista):
            self.Id = dlista[0]
            self.X = float(dlista[1])
            self.Y = float(dlista[2])
            self.Npix = float(dlista[3])
            self.Mag = float(dlista[4])
            self.RA = self.X
            self.DEC = self.Y


        def __str__ (self):
            msg = ''
            msg = msg + '%10d\t%10.3f\t%10.3f\t' % (self.Id, self.X, self.Y)
            msg = msg + '%10.6f\t%10.6f\t%5d\t%5.1f\n' % (self.RA, self.DEC, self.Npix, self.Mag)
            msg = msg + os.linesep
            return msg

        def __cmp__ (self, other):
            if self.Mag < other.Mag:
                return 1
            elif self.Mag == other.Mag:
                return 0
            else:
                return -1


    def __init__ (self, fitsfile):
        self.FitsFile = fitsfile
        self.ListEntries = []


    def FindObjects (self, table, sigma=5, filtsing=3):
        # statistiche iniziali
        tt = aa.clippedMeanStdev(table)
        totbck = tt['clippedMean']
        totstd = tt['clippedStdev']

        # selezione pixel
        datapos = []
        for x in xrange(table.shape[1]):
            for y in xrange(table.shape[0]):
                if table[y][x] > totbck+sigma*totstd:
                    datapos.append((y,x))


        # Scelta pixel connessi
        totloc = []
        for i in datapos:
            cn = []
            cn.append(i)
            for l in datapos:
                if (i[0]-l[0])**2 + (i[1]-l[1])**2 <= 2.0:
                    if l not in cn:
                        cn.append(l)
            ass = False
            for p in range(len(totloc)):
                for q in cn:
                    if q in totloc[p]:
                        totloc[p] = totloc[p] + cn
                        ass = True
                        break
                if ass == True:
                    break
            else:
                totloc.append(cn)


        # Eliminazione doppioni
        finloc = []
        for t in totloc:
            finpos = []
            for p in t: 
                if p not in finpos:
                    finpos.append(p)
            finloc.append(finpos)


        # Calcolo baricentro e pseudomagnitudine  
        finlist = []
        objl = 0
        for fc in finloc:
            minx = table.shape[1]
            miny = table.shape[0]
            maxx = 0
            maxy = 0
            for e in fc:
                if e[0] < miny:
                    miny = e[0]
                if e[0] > maxy:
                    maxy = e[0]
                if e[1] < minx:
                    minx = e[1]
                if e[1] > maxx:
                    maxx = e[1]
            cm = snm.center_of_mass(table[miny:maxy+1,minx:maxx+1])
            sm = snm.sum((table[miny:maxy+1,minx:maxx+1]))
            if len(fc) >= filtsing:
                logarg = sm-(maxy+1-miny)*(maxx+1-minx)*totbck
                if logarg < 0.0:
                    signum = -1.0
                elif logarg == 0.0:
                    signum = 1.0
                    logarg = 1e-30
                else:
                    signum =  1.0
                objl = objl + 1
                finlist.append(self.Object([objl,minx+cm[1]+1,miny+cm[0]+1,len(fc),(-2.5*signum*math.log10(math.fabs(logarg)))]))
        
        #
        self.ListEntries = finlist
        #
        return len(self.ListEntries)
