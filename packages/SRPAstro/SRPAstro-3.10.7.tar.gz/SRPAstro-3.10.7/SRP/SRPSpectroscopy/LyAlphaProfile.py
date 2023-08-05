""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (05/09/2011) First version.

"""


import SRP.SRPSpectroscopy as SS
from SRP.SRPSpectroscopy.VoigtProfileWells import VoigtProfileWells
from SRP.SRPSpectroscopy.LymAlphaDumpConst import LymAlphaDumpConst


def LyAlphaProfile (lambd,bpar):
    res = VoigtProfileWells (lambd,bpar,SS.LambdaLymanAlpha,LymAlphaDumpConst(),SS.AbsOscillStrength)
    return res

