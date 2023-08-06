""" Utility functions and classes for SRP

Context : SRP
Module  : PAOLO.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site and object should be valid pyephem objects.

History : (18/02/2012) First version.

"""

import ephem, numpy
import math
from SRP.SRPSky.ParallacticAngle import ParallacticAngle


def AverParallacticAngle (object,site,expt):
    sequen = numpy.linspace(0.0,expt,math.ceil(expt))
    orgdate = site.date
    paran = []
    for i in sequen:
        site.date = orgdate + i*ephem.second
        object.compute(site)
        paran.append(ParallacticAngle(object,site))
    return numpy.array(paran).sum()/len(sequen)