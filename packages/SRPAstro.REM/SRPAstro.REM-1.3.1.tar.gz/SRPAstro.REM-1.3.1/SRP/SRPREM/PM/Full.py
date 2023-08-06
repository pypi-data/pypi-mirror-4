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


def Full ((az,alt),(f_AN,f_AE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS)):
    # AN: error in the leveling of the telescope toward north
    # AE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # AES, AEC, EES, EEC:  eccentricity of the encoders
    # AOFS: azimuth zero point correction
    # EOFS: altitude zero point correction
    naz = az + f_AN * numpy.sin(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) - f_AE * numpy.cos(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) + f_NPAE * numpy.tan(numpy.radians(alt))  - f_BNP / numpy.cos(numpy.radians(alt)) + f_AOFS + f_AES * numpy.sin(numpy.radians(az)) + f_AEC * numpy.cos(numpy.radians(az))
    nalt = alt + f_AN * numpy.cos(numpy.radians(az)) + f_AE * numpy.sin(numpy.radians(az)) + f_EOFS + f_EES * numpy.sin(numpy.radians(alt)) + f_EEC * numpy.cos(numpy.radians(alt))
    return naz, nalt

