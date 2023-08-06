""" get OBJ site information

Module  : SRPREM.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 31/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (31/08/2012) First version.

"""

import ephem
from SRP.SRPMath.AstroCoordInput import AstroCoordInput


def GetObj (ra,dec):
    coords = AstroCoordInput(ra,dec)
    nb = ephem.FixedBody()
    nb._ra = str(coords.EphemCoord.ra)
    nb._dec = str(coords.EphemCoord.dec)
    nb._epoch = ephem.date(ephem.J2000)
    return nb