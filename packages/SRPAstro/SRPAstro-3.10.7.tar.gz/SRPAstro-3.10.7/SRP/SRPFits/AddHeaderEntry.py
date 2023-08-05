""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.2.0
Author  : Stefano Covino
Date    : 14/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)
            "fitfile" is the FITS file name.
            "keylist" is a list of keywords to be added to the FITS file headers.
            "entrylist" is a list of the same length than "keylist" with keywords values.
            "commentlist" is a list of the same length of "keylist" with comments (units, etc.)
                to the new headers.
            "outfilename" optional filename for output. Else input file file is overwritten.
            
            Function returns two values: (res, code). If res is False code reports the problem 
                (codes are in SRP.SRPFits.FitsConstants). Else res is True.

Remarks :

History : (12/10/2010) First version.
        : (25/04/2011) Output and input file names can be different.
        : (27/04/2011) Always list in output. Keywords longer than 8 characters.
        : (14/02/2012) Possibilty to write in other extensions.

"""

import warnings

import pyfits
import FitsConstants

def AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None, ext=0):
    try:
        hdr = pyfits.open(fitsfile)
    except IOError:
        return False,FitsConstants.FitsFileNotFound
    heder = hdr[ext].header    
    for i,l,m in zip(keylist,entrylist,commentlist):
        try:
            heder.update(i,l,m)
        except ValueError:
            heder.update(i.split()[0][:8],l,m)
    #
    warnings.resetwarnings()
    warnings.filterwarnings('ignore', category=UserWarning, append=True)
    if outfilename == None:
        hdr.writeto(fitsfile,clobber=True)
    else:
        hdr.writeto(outfilename,clobber=True)    
    warnings.resetwarnings() 
    warnings.filterwarnings('always', category=UserWarning, append=True)    
    return True,FitsConstants.FitsOk