""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : return angle is in radians, inputs are I, Q, U, V

History : (19/02/2012) First version.

"""

import numpy


def Stokes2Pol (i, q, u, v):
    pol = numpy.sqrt(q**2 + u**2 + v**2) / i
    theta = 0.5 * numpy.arctan2(u,q)
    chi = 0.5 * numpy.arctan2(v, numpy.sqrt(q**2 + u**2))
    return i, pol, theta, chi