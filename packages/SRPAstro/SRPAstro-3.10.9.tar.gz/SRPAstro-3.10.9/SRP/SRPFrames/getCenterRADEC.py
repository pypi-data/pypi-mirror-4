""" Utility functions and classes for SRP

Module  : Frames.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 31/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (31/08/2012) First version.

"""

from SRP.SRPFits.GetWCS import GetWCS


def getCenterRADEC (fitsfile, xpix=None, ypix=None):
    wcs = GetWCS(fitsfile)[0]
    if wcs != None:
        if xpix == None or ypix == None:
            return wcs.getCentreWCSCoords()
        else:
            return wcs.pix2wcs(xpix,ypix)
    else:
        return None