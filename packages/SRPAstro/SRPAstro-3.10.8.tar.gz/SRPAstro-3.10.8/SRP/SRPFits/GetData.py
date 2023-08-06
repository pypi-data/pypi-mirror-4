""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/05/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (21/05/2010) First version.

"""

import pyfits
import FitsConstants

def GetData (fitsfile, extension=0):
    try:
        hdr = pyfits.open(fitsfile)
    except IOError:
        return None,FitsConstants.FitsFileNotFound
    try:
        dataval = hdr[extension].data
    except IndexError:
        return None,FitsConstants.FitsDataSetNotFound
    return dataval,FitsConstants.FitsDataSetFound
    

    
