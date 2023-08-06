""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.0.0
Author  : Stefano Covino
Date    : 22/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (22/08/2012) First version.

"""



def Simple ((az,alt),(s_AOFS,s_EOFS)):
    # AOFS: azimuth zero point correction
    # EOFS: altitude zero point correction
    naz = az + s_AOFS  
    nalt = alt+s_EOFS
    return naz, nalt

