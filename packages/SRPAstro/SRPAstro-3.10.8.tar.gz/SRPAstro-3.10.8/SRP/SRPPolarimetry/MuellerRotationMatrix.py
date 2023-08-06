""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
            From Joos et al., SPIE, 7016

History : (04/02/2012) First version.

"""

import math
import numpy


def MuellerRotationMatrix (angle=0.0):
    r1 = [1., 0., 0., 0.]
    r2 = [0., math.cos(2*angle), math.sin(2*angle), 0.]
    r3 = [0., -math.sin(2*angle), math.cos(2*angle), 0.]
    r4 = [0., 0., 0., 1.]
    return numpy.matrix([r1, r2, r3, r4])
