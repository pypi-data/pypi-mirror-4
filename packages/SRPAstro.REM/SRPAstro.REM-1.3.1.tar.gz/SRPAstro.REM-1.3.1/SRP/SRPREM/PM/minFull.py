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

from Full import Full
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minFull ((f_AN,f_AE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS),taz,talt,oaz,oalt):
    caz, calt = Full((oaz,oalt),(f_AN,f_AE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS))
    return FastAngularDistance(taz,talt,caz,calt).sum()

