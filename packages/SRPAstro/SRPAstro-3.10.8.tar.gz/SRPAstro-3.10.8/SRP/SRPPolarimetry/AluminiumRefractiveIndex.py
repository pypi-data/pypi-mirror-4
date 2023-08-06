""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Valid only in 0.2:1.2 micron range
            Aleksandar D. Rakić. Algorithm for the determination of intrinsic 
                optical constants of metal films: application to aluminum, Appl. 
                Opt. 34, 4755-4767 (1995)

History : (05/02/2012) First version.

"""


import atpy
import os
from scipy.interpolate import interp1d
from SRP.SRPSystem.SRPPath import SRPPath


def AluminiumRefractiveIndex ():
    try:
        t = atpy.Table(os.path.join(SRPPath(),'SRPData','RefractiveIndex','METALS_Aluminium_Rakic.csv'), type='ascii')
    except IOError:
        return None
    #
    tw = t.where((t['lambda'] >= 0.2) & (t['lambda'] <= 1.2)) 
    tw.sort('lambda')
    #
    n1 = interp1d(tw['lambda'], tw['n'], kind='quadratic', bounds_error=False)
    k1 = interp1d(tw['lambda'], tw['k'], kind='quadratic', bounds_error=False)
    #
    return n1,k1

