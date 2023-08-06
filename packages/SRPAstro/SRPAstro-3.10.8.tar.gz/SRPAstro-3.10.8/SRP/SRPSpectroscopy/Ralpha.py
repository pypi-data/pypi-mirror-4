""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 03/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (03/09/2011) First version.

"""

import math
from SRP.SRPSpectroscopy.LymAlphaDumpConst import LymAlphaDumpConst
import SRP.SRPSpectroscopy as SS


def Ralpha (gu=3.0,gl=1.0):
    return (LymAlphaDumpConst() * SS.LambdaLymanAlpha) / (4 * math.pi * SS.SpeedofLight)

