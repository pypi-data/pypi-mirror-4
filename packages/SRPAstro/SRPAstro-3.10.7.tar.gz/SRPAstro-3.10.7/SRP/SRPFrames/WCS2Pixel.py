""" Utility functions and classes for SRP

Context : SRP
Module  : Frames.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 22/09/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (22/09/2010) First version.

"""

import astLib.astWCS as astWCS
import math


def WCS2Pixel (fitsheader, poslist):
    outlist = []
    WCS = astWCS.WCS(fitsheader, mode="pyfits")
    for i in poslist:
        outlist.append(WCS.wcs2pix(i[0],i[1]))
    return outlist
    