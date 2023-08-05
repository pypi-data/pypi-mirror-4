""" Utility functions and classes for SRP

Context : SRP
Module  : PAOLO
Version : 1.0.0
Author  : Stefano Covino
Date    : 01/03/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angles are in degrees

History : (01/03/2012) First version.

"""

import math
import numpy

from SRP.SRPPolarimetry.MuellerQuarterWavePlateMatrix import MuellerQuarterWavePlateMatrix
from SRP.SRPPolarimetry.MuellerMetallicMirrorMatrix import MuellerMetallicMirrorMatrix
from SRP.SRPPolarimetry.MuellerRotationMatrix import MuellerRotationMatrix
from SRP.SRPPolarimetry.MuellerTransmissionMatrix import MuellerTransmissionMatrix


def TNGMuellerMatrixPlate4 (parallactic, refrindex, extcoeff, rot=0.0, offset=0.0):
    m0 = MuellerRotationMatrix(math.radians(offset))
    m1 = MuellerQuarterWavePlateMatrix(math.radians(rot))
    m2 = MuellerRotationMatrix(math.radians(parallactic))
    m3 = MuellerMetallicMirrorMatrix(refrindex,extcoeff)
    m4 = MuellerRotationMatrix(math.radians(parallactic))
    return m0*m1*m2*m3*m4