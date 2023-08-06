""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 20/12/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (15/07/2010) First version.
        : (20/12/2010) Possibility of badly formatted ECS header included.

"""

import FitsConstants
import astLib.astWCS as aw 


def GetWCS (fitsfile, extension=0):
    try:
        wcs = aw.WCS(fitsfile)
    except IOError:
        return None,FitsConstants.FitsFileNotFound
    except ValueError:
        return None,FitsConstants.FitsWCSNotKnown
    return wcs,FitsConstants.FitsWCSFound
    


