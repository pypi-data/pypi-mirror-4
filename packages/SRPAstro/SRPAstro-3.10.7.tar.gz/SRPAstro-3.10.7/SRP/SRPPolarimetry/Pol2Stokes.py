""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angles are in radians

History : (19/02/2012) First version.

"""

import numpy


def Pol2Stokes (i, p, t, c):
    q = p*i*numpy.cos(2*t)*numpy.cos(2*c)
    u = p*i*numpy.sin(2*t)*numpy.cos(2*c)
    v = p*i*numpy.sin(2*c)
    return i, q, u, v