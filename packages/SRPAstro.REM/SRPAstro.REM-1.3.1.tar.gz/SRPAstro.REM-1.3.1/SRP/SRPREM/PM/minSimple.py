""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/08/2012) First version.

"""


from Simple import Simple
from SRP.SRPMath.FastAngularDistance import FastAngularDistance


def minSimple ((s_AOFS,s_EOFS),taz,talt,oaz,oalt):
    caz, calt = Simple((oaz,oalt),(s_AOFS,s_EOFS))
    return FastAngularDistance(taz,talt,caz,calt).sum()
