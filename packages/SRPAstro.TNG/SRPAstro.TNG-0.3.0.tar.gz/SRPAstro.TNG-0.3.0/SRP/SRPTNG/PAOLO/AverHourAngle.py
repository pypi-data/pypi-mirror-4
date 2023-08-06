""" Utility functions and classes for SRP

Context : SRP
Module  : PAOLO.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 20/09/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site and object should be valid pyephem objects.

History : (21/02/2012) First version.
        : (20/09/2012) Hour angles phased.

"""

import ephem, numpy
import math
from SRP.SRPMath.PhaseAngle import PhaseAngle
from SRP.SRPSky.HourAngle import HourAngle


def AverHourAngle (object,site,expt):
    sequen = numpy.linspace(0.0,expt,math.ceil(expt))
    orgdate = site.date
    houa = []
    for i in sequen:
        site.date = orgdate + i*ephem.second
        object.compute(site)
        houa.append(PhaseAngle(HourAngle(math.degrees(float(object.a_ra)),site),-180.0,180.0))
    return numpy.array(houa).sum()/len(sequen)
    
