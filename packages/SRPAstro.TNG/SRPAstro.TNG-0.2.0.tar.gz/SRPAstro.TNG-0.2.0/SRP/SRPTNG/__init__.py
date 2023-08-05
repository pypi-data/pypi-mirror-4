""" 

Context : SRP
Module  : TNG
Version : 1.0.7
Author  : Stefano Covino
Date    : 06/12/2012
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (29/02/2012) First version.
        : (31/07/2012) V. 0.1.1b1.
        : (20/09/2012) V. 0.1.1b2.
        : (27/09/2012) V. 0.1.1b3.
        : (29/09/2012) SRPTNGPAOLOSelectCoord and V. 0.2.0b1.
        : (28/11/2012) V. 0.2.0.b2 and new DATE keyword.
        : (01/12/2012) V. 0.2.0b3
        : (04/12/2012) V. 0.2.0b4
        : (06/12/2012) V. 0.2.0.
"""

__version__ = '0.2.0'


__all__ =  ['GetObj', 'GetTNGSite'] 


# TNG Dolores header keywords
EXPTIME = 'EXPTIME'
RADEG   = 'RA-DEG'
DECDEG  = 'DEC-DEG'
POSANG  = 'POSANG'
AZ      = 'AZ'
ALT     = 'EL'
ROTPOS  = 'ROT-POS'
PARANG  = 'PARANG'
LST     = 'LST'
DATE    = 'DATE-OBS'
DATES   = 'DATE'
TIME    = 'EXPSTART'
FILTER  = 'FLT_ID'
GRISM   = 'GRM_ID'
SLIT    = 'SLT_ID'
PSLR    = 'PSLR_ID'
RTRY1   = 'RTY1_ID'
RTRY2   = 'RTY2_ID'
OBJECT  = 'OBJCAT'



# TNG LRF filters
# LRS filter
U   =   'U_John_01'
B   =   'B_John_10'
V   =   'V_John_11'
R   =   'R_John_12'
I   =   'I_John_13'
u   =   'u_sdss_29'
g   =   'g_sdss_30'
r   =   'r_sdss_31'
i   =   'i_sdss_32'
z   =   'z_sdss_33'

LRSFiltCentrWaveDict = {U : 0.364, B : 0.42, V : 0.527, R : 0.625, I : 0.878, 
    u : 0.349, g : 0.478, r : 0.629, i : 0.77, z : 0.8931}


# Observatory location
TNGLAT = '28:46:00'
TNGLONG = '-17:53:00'
TNGHEIGHT = 2400.0
