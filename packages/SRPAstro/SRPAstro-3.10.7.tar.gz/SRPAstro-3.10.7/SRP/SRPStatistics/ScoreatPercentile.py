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


import SRP.stats as SS
from scipy.stats import scoreatpercentile


def ScoreatPercentile(vl, percdown=31.7, percc=50.0, percup=68.3):
    if SS.stdev(list(vl)) != 0.0:
        vd = scoreatpercentile(list(vl),percdown)
        vc = scoreatpercentile(list(vl),percc)    
        vu = scoreatpercentile(list(vl),percup)
        return vd,vc,vu,(vu-vd)/2.0
    else:
        return list(vl)[0],list(vl)[0],list(vl)[0],0.0