""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 29/06/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : SolarAbundance(element=None)
            the script retrieves the solar abundance according to the table by Asplund et al. (2009)

History : (29/06/2011) First version.

"""

import SRP.SRPSpectroscopy


def SolarAbundance (element=None):
    if element == None:
        return SRP.SRPSpectroscopy.SolAbDict.keys()
    else:
        try:
            return SRP.SRPSpectroscopy.SolAbDict[element]
        except KeyError:
            return None
