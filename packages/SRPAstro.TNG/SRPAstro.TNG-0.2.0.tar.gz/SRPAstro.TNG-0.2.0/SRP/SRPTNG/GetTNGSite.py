""" get TNG site information

Context : PAOLO
Module  : PAOLO.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (18/02/2012) First version.

"""

import ephem
import SRP.SRPTNG as ST


def GetTNGSite ():
    site = ephem.Observer()
    site.lat = str(ST.TNGLAT)
    site.long = str(ST.TNGLONG)
    site.elevation = ST.TNGHEIGHT
    return site