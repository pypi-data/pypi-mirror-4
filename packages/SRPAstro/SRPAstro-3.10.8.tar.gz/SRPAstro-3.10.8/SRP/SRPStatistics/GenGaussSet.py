""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input is a list of (x,sigmax)

History : (19/02/2012) First version.

"""


import numpy


def GenGaussSet (vl, evl, ntrial=100):
    if evl != 0.0:
        return numpy.random.normal(vl,2*evl,ntrial)
    else:
        return vl