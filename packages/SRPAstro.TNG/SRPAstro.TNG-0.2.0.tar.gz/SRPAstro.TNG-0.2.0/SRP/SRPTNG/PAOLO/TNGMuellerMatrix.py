""" Utility functions and classes for SRP

Context : SRP
Module  : PAOLO
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angles are in degrees
            From Giro et al., SPIE, 4843. 456 (2003)

History : (23/02/2012) First version.

"""

import math
import numpy


from SRP.SRPPolarimetry.MuellerMetallicMirrorMatrix import MuellerMetallicMirrorMatrix
from SRP.SRPPolarimetry.MuellerRotationMatrix import MuellerRotationMatrix
from SRP.SRPPolarimetry.MuellerTransmissionMatrix import MuellerTransmissionMatrix


def TNGMuellerMatrix (parallactic, refrindex, extcoeff, offset=0.0):
    m0 = MuellerRotationMatrix(math.radians(offset))
    m1 = MuellerRotationMatrix(math.radians(parallactic))
    m2 = MuellerMetallicMirrorMatrix(refrindex,extcoeff)
    m3 = MuellerRotationMatrix(math.radians(parallactic))
    return m0*m1*m2*m3