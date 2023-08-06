#!/usr/bin/env python
"""Calculates the expected $\Delta \alpha/\alpha$ from the King, et al. (2012) and error estimate. Section 5.3.

King, J.A., Webb, J.K., Murphy, M.T., Flambaum, V.V., Carswell, R.F., Bainbridge, M.B., Wilczynska, M.R., Koch, F.E., 
Spatial variation in the fine-structure constant - new results from VLT/UVES, 
Monthly Notices of the Royal Astronomical Society, 422, 3370-3414. (2012)
"""
try:
    import angles
except:
    print """python package ''angles'' is required. Try running: 
    $ sudo pip install -U angles"""
    raise 
try:
    import uncertainties
except:
    print """python package ''uncertainties'' is required. Try running: 
    $ sudo pip install -U uncertainties"""
    raise 
from uncertainties import umath

# Define exceptions
class DipoleError(Exception): 
    pass

# Some default starting points on the sky to consider
QSO_RA = "22h20m06.757" # RA
QSO_DEC = "-28d03m23.34" # DEC
THETA = 1.02 # radians
REDSHIFT = 1.5 # Just pick a redshift to start
RADIAL_DISTANCE = 1.3 # GLyr

# =====================================================================
# = Wrap angles package functions with uncertainties package wrappers =
# =====================================================================
wrap_radian_RA = uncertainties.wrap(angles.h2r)
wrap_radian_DEC = uncertainties.wrap(angles.d2r)
wrap_sep = uncertainties.wrap(angles.sep)

# ============================
# = dipole and monopole term =
# ============================
# eq. 15 in King et al. 2012
DIP_RA = 17.3
DIP_RA_ERR = 1.0
DIP_DEC = -61.0
DIP_DEC_ERR = 10.0
DIP_AMPLITUDE = 0.97e-5
DIP_AMPLITUDE_ERR = 0.21e-5 # average of asymmetric errors
DIP_MONOPOLE = -0.178e-5
DIP_MONOPOLE_ERR  = 0.084e-5

# Values and errors combined for uncertainties package.
DIPOLE_AMPLITUDE = uncertainties.ufloat((DIP_AMPLITUDE, DIP_AMPLITUDE_ERR))
MONOPOLE = uncertainties.ufloat((DIP_MONOPOLE, DIP_MONOPOLE_ERR))
DIPOLE_RA = uncertainties.ufloat((DIP_RA, DIP_RA_ERR))
DIPOLE_DEC = uncertainties.ufloat((DIP_DEC, DIP_DEC_ERR))

def basic_dipole_monopole(amplitude=DIP_AMPLITUDE, \
                          theta=THETA, \
                          monopole=DIP_MONOPOLE, \
                          *args, \
                          **kwargs):
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
    return amplitude * umath.cos(theta) + monopole

wrap_dipole_monopole = uncertainties.wrap(basic_dipole_monopole)

def dipole_monopole(right_ascension=QSO_RA, \
                    declination=QSO_DEC, \
                    dipole_ra=DIPOLE_RA, \
                    dipole_dec=DIPOLE_DEC, \
                    amplitude=DIPOLE_AMPLITUDE, \
                    monopole=MONOPOLE):
    """Takes a position on the sky (in RA and DEC), and returns the predicted value of the dipole.
    This equation propogates the relevant errors through the dipole equation, returns value and error estimate.
    
    Arguments:
    :param right_ascension:right ascension of point in sky under consideration. 
    :type right_ascension: number
    :param declination: declination of point in sky under consideration.
    :type declination: number
    :param dipole_ra: RA of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_ra: uncertainties.AffineScalarFunc
    :param dipole_dec: DEC of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_dec: uncertainties.AffineScalarFunc
    :param amplitude: Amplitude term of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type amplitude: uncertainties.AffineScalarFunc
    :param monopole: Monopole term (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type monopole: uncertainties.AffineScalarFunc
    returns
    """
    pos1 = angles.AngularPosition(alpha=right_ascension, delta=declination)
    return wrap_dipole_monopole(amplitude, \
                                wrap_sep(wrap_radian_RA(dipole_ra), \
                                         wrap_radian_DEC(dipole_dec), \
                                         pos1.alpha.r, \
                                         pos1.delta.r), \
                                monopole)

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

def basic_z_dipole_monopole(prefactor=Z_DIP_PREFACTOR, \
                            z_redshift=REDSHIFT, \
                            beta=Z_DIP_BETA, \
                            theta=THETA, \
                            monopole=Z_DIP_MONOPOLE,\
                            *args,\
                            **kwargs):
    """
    Arguments:
    :param prefactor: Amplitude of dipole.
    :type prefactor: number
    :param z_redshift: Redshift of absorber in sky.
    :type z_redshift: number
    :param beta: power law exponent.
    :type beta: number
    :param theta: angle in radians between the dipole and a positions on the sky.
    :type theta: number
    :param monopole: monopole term.
    :type monopole: number
    :returns: value of predicted dipole at a theta radians away from dipole.
    :rtype: number
    """
    return prefactor * z_redshift ** beta * umath.cos(theta) + monopole

wrap_z_dipole_monopole = uncertainties.wrap(basic_z_dipole_monopole)

def z_dipole_monopole(right_ascension=QSO_RA, \
                      declination=QSO_DEC, \
                      dipole_ra=Z_DIPOLE_RA, \
                      dipole_dec=Z_DIPOLE_DEC, \
                      prefactor=Z_DIP_PREFACTOR, \
                      z_redshift=REDSHIFT, \
                      beta=Z_DIP_BETA, \
                      monopole=Z_DIP_MONOPOLE):
    """Returns the predicted value of alpha from the z_dipole equation.
    
    Arguments:
    :param right_ascension:right ascension of point in sky under consideration. 
    :type right_ascension: number
    :param declination: declination of point in sky under consideration.
    :type declination: number
    :param dipole_ra: RA of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_ra: uncertainties.AffineScalarFunc
    :param dipole_dec: DEC of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_dec: uncertainties.AffineScalarFunc
    :param prefactor: Prefactor term of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type prefactor: uncertainties.AffineScalarFunc
    
    :param monopole: Monopole term (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type monopole: uncertainties.AffineScalarFunc
    returns
    """
    pos1 = angles.AngularPosition(alpha=right_ascension, delta=declination)
    return wrap_z_dipole_monopole(prefactor, \
                                  z_redshift, \
                                  beta, \
                                  wrap_sep(wrap_radian_RA(dipole_ra), \
                                           wrap_radian_DEC(dipole_dec), \
                                           pos1.alpha.r, \
                                           pos1.delta.r), \
                                  monopole)

# ======================
# = r-dependent dipole =
# ======================
# eq. 19 

R_DIP_RA = 17.5
R_DIP_RA_ERR = 1.0
R_DIP_DEC = -62.0
R_DIP_DEC_ERR = 10.0
R_DIP_AMPLITUDE = 1.1e-6 # in GLyr 
R_DIP_AMPLITUDE_ERR = 0.2e-6 # average of asymmetric errors
R_DIP_MONOPOLE = -0.187e-5
R_DIP_MONOPOLE_ERR  = 0.084e-5

# Uncertainties
R_DIPOLE_AMPLITUDE = uncertainties.ufloat((R_DIP_AMPLITUDE, R_DIP_AMPLITUDE_ERR))
R_DIPOLE_MONOPOLE = uncertainties.ufloat((R_DIP_MONOPOLE, R_DIP_MONOPOLE_ERR))
R_DIPOLE_RA = uncertainties.ufloat((R_DIP_RA, R_DIP_RA_ERR))
R_DIPOLE_DEC = uncertainties.ufloat((R_DIP_DEC, R_DIP_DEC_ERR))

def basic_r_dipole_monopole(amplitude=R_DIPOLE_AMPLITUDE,\
                            radial_distance=RADIAL_DISTANCE,\
                            theta=THETA,\
                            monopole=R_DIPOLE_MONOPOLE,\
                            *args,\
                            **kwargs):
    """
    
    Arguments:
    :param amplitude: Amplitude term of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type amplitude: number
    :param radial_distance: Radial distance in GLyr
    :type radial_distance: number
    :type theta: number
    :param monopole: monopole term.
    :type monopole: number
    returns
    """
    return amplitude * radial_distance * umath.cos(theta) + monopole

wrap_r_dipole_monopole = uncertainties.wrap(basic_r_dipole_monopole)

def r_dipole_monopole(right_ascension=QSO_RA, \
                      declination=QSO_DEC, \
                      dipole_ra=R_DIPOLE_RA, \
                      dipole_dec=R_DIPOLE_DEC, \
                      amplitude=R_DIPOLE_AMPLITUDE, \
                      radial_distance=RADIAL_DISTANCE, \
                      monopole=R_DIPOLE_MONOPOLE):
    """docstring for r_dipole_monopole
    
    Arguments:
    :param right_ascension:right ascension of point in sky under consideration. 
    :type right_ascension: number
    :param declination: declination of point in sky under consideration.
    :type declination: number
    :param dipole_ra: RA of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_ra: uncertainties.AffineScalarFunc
    :param dipole_dec: DEC of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type dipole_dec: uncertainties.AffineScalarFunc
    :param amplitude: Amplitude term of dipole (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type amplitude: uncertainties.AffineScalarFunc
    :param radial_distance: Radial distance in GLyr
    :type radial_distance: uncertainties.AffineScalarFunc
    :param monopole: Monopole term (optional with uncertainty via uncertainties.ufloat((value, error)) ).
    :type monopole: uncertainties.AffineScalarFunc
    returns
    """
    pos1 = angles.AngularPosition(alpha=right_ascension, delta=declination)
    return wrap_r_dipole_monopole(amplitude, \
                                  radial_distance, \
                                  wrap_sep(wrap_radian_RA(dipole_ra), \
                                           wrap_radian_DEC(dipole_dec), \
                                           pos1.alpha.r, \
                                           pos1.delta.r), \
                                  monopole)


# TODO: monte carlo verification of these calculations
# TODO: verbose version of these
# TODO: Systematic error and statistical error considerations
# TODO: unit testing
