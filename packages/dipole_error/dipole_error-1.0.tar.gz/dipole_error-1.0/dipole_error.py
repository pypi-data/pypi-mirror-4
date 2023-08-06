#!/usr/bin/env python
"""Calculates the expected $\Delta \alpha/\alpha$ from the King, et al. (2012) and error estimate. Section 5.3."""
import angles
import uncertainties
from uncertainties.umath import *

# Define exceptions
class DipoleError(Exception): 
    pass

# King et al. (2012) dipole location
DIP_RA = 17.3
DIP_RA_ERR = 1.0
DIP_DEC = -61.0
DIP_DEC_ERR = 10.0

DIPOLE_RA = uncertainties.ufloat((DIP_RA, DIP_RA_ERR))
DIPOLE_DEC = uncertainties.ufloat((DIP_DEC, DIP_DEC_ERR))

wrap_radian_RA = uncertainties.wrap(angles.h2r)
wrap_radian_DEC = uncertainties.wrap(angles.d2r)
wrap_sep = uncertainties.wrap(angles.sep)

QSO_RA = "22h20m06.757" # RA
QSO_DEC = "-28d03m23.34" # DEC

A_0 = 0.97e-5
A_ERR = 0.21e-5 # average of asymmetric errors
AMPLITUDE = uncertainties.ufloat((A_0, A_ERR))

M_0 = -0.178e-5
M_ERR  = 0.084e-5
MONOPOLE = uncertainties.ufloat((M_0, M_ERR))

THETA = 1.02 # radians

def basic_dipole_monopole(amplitude=AMPLITUDE, theta=THETA, monopole=MONOPOLE, *args, **kwargs):
    """Returns the predicted value of da/a as given by eq. 15 in King et al. 2012.
    
    
    Arguments:
    :param amplitude: Amplitude of dipole.
    :type amplitude: number
    :param theta: angle in radians between the dipole and a positions on the sky.
    :type theta: number
    :param monopole: monopole term.
    :type monopole: number
    :returns: value of predicted dipole at a theta radians away from dipole.
    :rtype: number
    """
    return amplitude * uncertainties.umath.cos(theta) + monopole

wrap_dipole_monopole = uncertainties.wrap(basic_dipole_monopole)

def dipole_monopole(right_ascension=QSO_RA, declination=QSO_DEC, dipole_ra=DIPOLE_RA, dipole_dec=DIPOLE_DEC, amplitude=AMPLITUDE, monopole=MONOPOLE):
    """docstring for dipole_mono"""
    pos1 = angles.AngularPosition(alpha=right_ascension, delta=declination)
    return wrap_dipole_monopole(amplitude, wrap_sep(wrap_radian_RA(dipole_ra), wrap_radian_DEC(dipole_dec), pos1.alpha.r, pos1.delta.r), monopole)

# ======================
# = z-dependent dipole =
# ======================
# eq. 18 King et al. 2012

Z_DIP_RA = 17.5
Z_DIP_RA_ERR = 1.0

Z_DIP_DEC = -62.0
Z_DIP_DEC_ERR = 10.0

Z_DIP_PREFACTOR = 0.81e-5
Z_DIP_PREFACTOR_ERR = 0.27e-5 # average of .26 and .28

Z_DIP_MONOPOLE = -0.184e-5
Z_DIP_MONOPOLE_ERR = 0.085e-5

Z_DIP_BETA = 0.46
Z_DIP_BETA_ERR = 0.49

Z_DIPOLE_RA = uncertainties.ufloat((Z_DIP_RA, Z_DIP_RA_ERR))
Z_DIPOLE_DEC = uncertainties.ufloat((Z_DIP_DEC, Z_DIP_DEC_ERR))
Z_DIPOLE_PREFACTOR = uncertainties.ufloat((Z_DIP_PREFACTOR, Z_DIP_PREFACTOR_ERR))
Z_DIPOLE_MONOPOLE = uncertainties.ufloat((Z_DIP_MONOPOLE, Z_DIP_MONOPOLE_ERR))
Z_DIPOLE_BETA = uncertainties.ufloat((Z_DIP_BETA, Z_DIP_BETA_ERR))

REDSHIFT = 1.5 # Just pick a redshift to start

def basic_z_dipole_monopole(prefactor=Z_DIP_PREFACTOR, z_redshift=REDSHIFT, beta=Z_DIP_BETA, theta=THETA, monopole=Z_DIP_MONOPOLE):
    """docstring for basic_z_dipole_monopole"""
    return prefactor * z_redshift ** beta * uncertainties.umath.cos(theta) + monopole

wrap_z_dipole_monopole = uncertainties.wrap(basic_z_dipole_monopole)

def z_dipole_monopole(right_ascension=QSO_RA, declination=QSO_DEC, dipole_ra=Z_DIPOLE_RA, dipole_dec=Z_DIPOLE_DEC, prefactor=Z_DIP_PREFACTOR, z_redshift=REDSHIFT, beta=Z_DIP_BETA, monopole=Z_DIP_MONOPOLE):
    """docstring for z_dipole_monopole"""
    pos1 = angles.AngularPosition(alpha=right_ascension, delta=declination)
    return wrap_z_dipole_monopole(prefactor, \
                                  z_redshift, \
                                  beta, \
                                  wrap_sep(wrap_radian_RA(dipole_ra), wrap_radian_DEC(dipole_dec), \
                                  pos1.alpha.r, pos1.delta.r), \
                                  monopole)

# ======================
# = r-dependent dipole =
# ======================
# eq. 19 

def basic_r_dipole_monopole():
    """docstring for basic_r_dipole_monopole"""
    pass


# 
# # eq. 20
# # Do I need to do this? Can't I set basic_r_dipole_monopole with monopole=0?
# def basic_r_dipole_only():
#     """docstring for basic_r_dipole_only"""
#     pass
# 
# TODO: monte carlo verification of these calculations
# print "1:", prefactor
# print "2:", z_redshift
# print "3:", beta
# print "4:", wrap_sep(wrap_radian_RA(dipole_ra), wrap_radian_DEC(dipole_dec), pos1.alpha.r, pos1.delta.r)
# print "5:", monopole
