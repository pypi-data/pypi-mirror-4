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
from SRP.SRPMath.AstroCoordInput import AstroCoordInput


def GetObj (ra,dec):
    coord = AstroCoordInput(ra,dec)
    nb = ephem.readdb('SRPTNGPALO Object,f|M|sp,'+str(ephem.hours(ephem.degrees(str(coord.RA))))+','+str(ephem.degrees(str(coord.DEC)))+',0,'+'2000')
    return nb