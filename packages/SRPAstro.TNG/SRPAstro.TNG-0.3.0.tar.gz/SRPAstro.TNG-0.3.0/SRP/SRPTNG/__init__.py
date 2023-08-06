""" 

Context : SRP
Module  : TNG
Version : 1.0.12
Author  : Stefano Covino
Date    : 22/04/2013
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
        : (18/03/2013) New filter names and V. 0.2.1b1.
        : (22/03/2013) New command SRPTNGPAOLOSpectrumMatch, V. 0.3.0b1.
        : (08/04/2013) V. 0.3.0b2.
        : (09/04/2013) V. 0.3.0b3.
        : (22/04/2013) V. 0.3.0.
"""

__version__ = '0.3.0'


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
Ub  =   'U_John_29'
B   =   'B_John_10'
Bb  =   'B_Jogn_02'
V   =   'V_John_11'
Vb  =   'V_Jogn_03'
R   =   'R_John_12'
Rb  =   'R_Jogn_04'
I   =   'I_John_13'
Ib  =   'I_Jogn_05'
u   =   'u_SDSS_29'
ub  =   'u_SDSS_34'
g   =   'g_SDSS_30'
gb  =   'g_SDSS_35'
r   =   'r_SDSS_31'
rb  =   'r_SDSS_36'
i   =   'i_SDSS_32'
ib  =   'i_SDSS_37'
z   =   'z_SDSS_33'
zb  =   'z_SDSS_38'
DW  =   'D_WOLL'
OP  =   'OPEN'
HA  =   'H_alpha_22'



LRSFiltCentrWaveDict = {U : 0.364, Ub : 0.364, B : 0.42, Bb : 0.42, V : 0.527, Vb : 0.527,
    R : 0.625, Rb : 0.625, I : 0.878, Ib : 0.878, u : 0.349, ub : 0.349, g : 0.478, gb : 0.478,
    r : 0.629, rb : 0.629, i : 0.77, ib : 0.77, z : 0.8931, zb : 0.8931, HA : 0.656}



# Observatory location
TNGLAT = '28:46:00'
TNGLONG = '-17:53:00'
TNGHEIGHT = 2400.0

