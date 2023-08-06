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

import numpy


def Classic ((az,alt),(c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFS,c_EOFS)):
    # AN: error in the leveling of the telescope toward north
    # AE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # TF: sagging of the tube
    # AOFS: azimuth zero point correction
    # EOFS: altitude zero point correction
    naz = az + c_AN * numpy.sin(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) - c_AE * numpy.cos(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) + c_NPAE * numpy.tan(numpy.radians(alt)) - c_BNP / numpy.cos(numpy.radians(alt)) + c_AOFS
    nalt = alt + c_AN * numpy.cos(numpy.radians(az)) + c_AE * numpy.sin(numpy.radians(az)) + c_TF * numpy.cos(numpy.radians(alt)) + c_EOFS
    return naz, nalt

