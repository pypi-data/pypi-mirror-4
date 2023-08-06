""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 11/08/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Output coordinates in degrees.

History : (06/08/2010) First version.
        : (11/08/2010) Check on not physical input.

"""


import ephem
import math


class AstroCoordInput:
    def __init__ (self, ra, dec, inp_equinox=2000.0, out_equinox=2000.0):
        # check if the character ':' is part of the input, then let's read hour rather
        #   than degrees.
        # RA
        if str(ra).find(':') > 0:
            ira = ephem.hours(ra)
        else:
            ira = ephem.degrees(str(ra))
        # DEC
        idec = ephem.degrees(str(dec))
        icoordset = ephem.Equatorial(ira,idec,epoch=inp_equinox)
        ocoordset = ephem.Equatorial(icoordset,epoch=out_equinox)
        self.RA = math.degrees(ocoordset.ra)
        self.DEC = math.degrees(ocoordset.dec)
        self.Epoch = float(ocoordset.epoch)
        self.EphemCoord = ocoordset
        if not ((0.0 <= self.RA <= 360.0) and (-90.0 <= self.DEC <= 90.0)):
            self.Valid = False
        else:
            self.Valid = True
        
    def __str__ (self):
        msg = '%s %s' % (self.EphemCoord.ra, self.EphemCoord.dec)
        return msg
        
        