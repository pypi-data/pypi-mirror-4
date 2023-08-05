""" Utility functions and classes for SRP

Context : SRP
Module  : Net.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 16/07/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (16/07/2010) First version.

"""

import NetConstants
import httplib


def GetWebPage (UrlAddress, UrlString):
    conn = httplib.HTTPConnection(UrlAddress)
    try:
        conn.request("GET",UrlString)
    except:
        conn.close()
        return None
    resp = conn.getresponse()
    if resp.status != NetConstants.WebQueryOK:
        conn.close()
        return None
    else:
        data = resp.read()
        conn.close()
        return data
    


