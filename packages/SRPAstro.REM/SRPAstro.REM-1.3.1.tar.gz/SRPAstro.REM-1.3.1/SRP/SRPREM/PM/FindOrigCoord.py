""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.0.0
Author  : Stefano Covino
Date    : 24/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (24/08/2012) First version.

"""

import numpy

TOLAZ = 1e-5
TOLALT = 1e-5
MAXITER = 100

def FindOrigCoord (az,alt,func,pars):
    offaz = 1
    offalt = 1
    niter = 0
    taz = az
    talt = alt
    while numpy.all(offaz > TOLAZ) and numpy.all(offalt > TOLALT) and niter <= MAXITER:
        naz,nalt = func((taz,talt),pars)
        #print naz,nalt,az,alt
        offaz = numpy.absolute(naz-az)
        offalt = numpy.absolute(nalt-alt)
        taz = numpy.where(naz >= az, taz - offaz/2., taz + offaz/2.)
        talt = numpy.where(nalt >= alt, talt - offalt/2., talt + offalt/2.)
        niter = niter + 1
    return taz, talt, niter <= MAXITER

