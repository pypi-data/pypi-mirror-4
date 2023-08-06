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


def MuellerOffsetMatrix (q0=0.0, u0=0.0, v0=0.0):
    r1 = [1., 0., 0., 0.]
    r2 = [q0, 1., 0., 0.]
    r3 = [u0, 0., 1., 0.]
    r4 = [v0, 0., 0., 1.]
    return numpy.matrix([r1, r2, r3, r4])
