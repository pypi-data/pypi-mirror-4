""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 
    
History : (21/02/2012) First version.

"""

import math
import numpy


def StokesOffsetVector (q0=0.0, u0=0.0, v0=0.0):
    return numpy.matrix([0.0, q0, u0, v0]).transpose()
