#!/usr/bin/env python
"""Example of dipole_error usage"""
import uncertainties
import dipole_error


QSO_RA = "22h20m06.757" # RA
QSO_DEC = "-28d03m23.34" # DEC
THETA = 1.02 # radians
REDSHIFT = 1.5 # Just pick a redshift to start
RADIAL_DISTANCE = 1.3 # GLyr

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

print "Using default inputs: "
print dipole_error.dipole_monopole()

print
print "Different RA values: "
for ra_value in ["12h20m06.757", 17.2, "17h12m"]:
    print "RA:", ra_value, "\n  da/a:", dipole_error.dipole_monopole(right_ascension=ra_value, \
                        declination=QSO_DEC, \
                        dipole_ra=DIPOLE_RA, \
                        dipole_dec=DIPOLE_DEC, \
                        amplitude=DIPOLE_AMPLITUDE, \
                        monopole=MONOPOLE)
                    
print 
print "Different DEC values: "
for dec_value in ["-28d03m23.34", "-61d03m", 15.0]:
    print "DEC:", dec_value, "\n  da/a:", \
          dipole_error.dipole_monopole(right_ascension=QSO_RA, \
                        declination=dec_value, \
                        dipole_ra=DIPOLE_RA, \
                        dipole_dec=DIPOLE_DEC, \
                        amplitude=DIPOLE_AMPLITUDE, \
                        monopole=MONOPOLE)

print
print "Different Amplitude/error values: "
for amplitude_error in [0.1e-5, 2.0e-5]:
    print "Amplitude error:", amplitude_error, "\n  da/a:", \
    dipole_error.dipole_monopole(right_ascension=QSO_RA, \
                  declination=QSO_DEC, \
                  dipole_ra=DIPOLE_RA, \
                  dipole_dec=DIPOLE_DEC, \
                  amplitude=uncertainties.ufloat((DIP_AMPLITUDE, amplitude_error)), \
                  monopole=MONOPOLE)
        
print 
print "If you want to do it by hand: "
print dipole_error.dipole_monopole(\
        right_ascension="22h20m06.757", \
        declination="-28d03m23.34", \
        dipole_ra=uncertainties.ufloat((17.3, 1.0)), \
        dipole_dec=uncertainties.ufloat((-61.0, 10.0)), \
        amplitude=uncertainties.ufloat((0.97e-5, 0.21e-5)), \
        monopole=uncertainties.ufloat((-0.178e-5, 0.084e-5)),\
        )

print 
print "If you don't want error, just pass a float (note monopole term):"
print dipole_error.dipole_monopole(\
        right_ascension="22h20m06.757", \
        declination="-28d03m23.34", \
        dipole_ra=uncertainties.ufloat((17.3, 1.0)), \
        dipole_dec=uncertainties.ufloat((-61.0, 10.0)), \
        amplitude=uncertainties.ufloat((0.97e-5, 0.21e-5)), \
        monopole=0.,\
        )

print 
print "Same functionality with the two other models: z_dipole_monopole and r_dipole_monopole:"

# =====================
# = z_dipole_monopole =
# =====================
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

print "z_dipole_monopole: "
print dipole_error.z_dipole_monopole(right_ascension=QSO_RA, \
                      declination=QSO_DEC, \
                      dipole_ra=Z_DIPOLE_RA, \
                      dipole_dec=Z_DIPOLE_DEC, \
                      prefactor=Z_DIP_PREFACTOR, \
                      z_redshift=REDSHIFT, \
                      beta=Z_DIP_BETA, \
                      monopole=Z_DIP_MONOPOLE)

# =====================
# = r_dipole_monopole =
# =====================
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

print 
print "r_dipole_monopole"
print dipole_error.r_dipole_monopole(right_ascension=QSO_RA, \
                      declination=QSO_DEC, \
                      dipole_ra=R_DIPOLE_RA, \
                      dipole_dec=R_DIPOLE_DEC, \
                      amplitude=R_DIPOLE_AMPLITUDE, \
                      radial_distance=RADIAL_DISTANCE, \
                      monopole=R_DIPOLE_MONOPOLE)
                      

# def monte_carlo(value, error):
#     """Return a random value around value +/- error"""
#     if error == 0:
#         return value
#     else:
#         return np.random.normal(value, error)
# 
# def monte_carlo_angle(right_ascension, right_ascension_error, declination, declination_error, qso=QSO_POSITION):
#     """Return the radians between the two points """
#     # return np.radians(angles.r2d(qso.sep(angles.AngularPosition(alpha=monte_carlo(ra_0, ra_err), delta=monte_carlo(dec_0, dec_err)))))
#     return np.radians(angles.r2d(qso.sep(angles.AngularPosition(alpha=monte_carlo(right_ascension, right_ascension_error), delta=monte_carlo(declination, declination_error)))))
# 
# 
# def mc_theta(right_ascension, \
#             declination, qso=sky_position(QSO_RA, QSO_DEC), *args, **kwargs):
#     """docstring for mc_theta"""
#     dipole_sky_position = angles.AngularPosition(alpha=right_ascension, delta=declination)
#     return np.radians(angles.r2d(qso.sep(dipole_sky_position)))
# 
# def theta(right_ascension, declination, qso=sky_position(QSO_RA, QSO_DEC), *args, **kwargs):
#     """Returns the radian angle between two RA and DECs.
#     
#     Arguments:
#     :param right_ascension: right ascension of position, e.g., "22h20m06.757"
#     :type right_ascension: string
#     :param declination: declination of position, e.g., "-28d03m23.34"
#     :type declination: string
#     :param qso: angles position of point on sky
#     :type qso: number
#     """
#     dipole_sky_position = angles.AngularPosition(alpha=right_ascension, delta=declination)
#     return np.radians(angles.r2d(qso.sep(dipole_sky_position)))
# 
# uncertainty_theta = uncertainties.wrap(theta)
# 
# uncertainty_theta = uncertainties.wrap(theta)
# uncertainty_theta2 = uncertainties.wrap(theta2)
# uncertainty_theta3 = uncertainties.wrap(theta3)
#     
# # print "Test 1:", theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION)
# # print "Test 2:", uncertainty_theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION)
# # print "Test 3:", uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=QSO_POSITION)
# # print "Test 4:", uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=sky_position(QSO_RA, QSO_DEC))
# # print "Test 5:", uncertainty_theta2(DIPOLE_RA, DIPOLE_DEC, QSO_RA, QSO_DEC)
# # print "Test 5a:", theta2(DIPOLE_RA, DIPOLE_DEC, QSO_RA, QSO_DEC)
# # print "Test 5b:", theta3(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, QSO_RA, QSO_DEC)
# # print "Test 5c:", uncertainty_theta3(DIPOLE_RA, DIPOLE_DEC, QSO_RA, QSO_DEC)
# 
# 
# # print "Test 6:", dipole_monopole(AMPLITUDE.nominal_value, theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION), MONOPOLE.nominal_value)
# # print "Test 7:", uncertainty_dipole_monopole(AMPLITUDE.nominal_value, \
# #                                             theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION), MONOPOLE.nominal_value)
# # print "Test 8 (Amp):", uncertainty_dipole_monopole(AMPLITUDE, theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION), MONOPOLE.nominal_value)
# # print "Test 9 (Mono):", uncertainty_dipole_monopole(AMPLITUDE.nominal_value, theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION), MONOPOLE)
# # print "Test 10 (Amp/Mono):", uncertainty_dipole_monopole(AMPLITUDE, theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION), MONOPOLE)
# # print "Test 11 (all):", uncertainty_dipole_monopole(AMPLITUDE, uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=QSO_POSITION), MONOPOLE)
# # 
# # dipole_monopole_dict = {
# #     'amplitude': AMPLITUDE,
# #     'theta': uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=QSO_POSITION),
# #     'monopole': MONOPOLE,
# # }
# # 
# # # print dipole_monopole_dict
# # print uncertainty_dipole_monopole(**dipole_monopole_dict)
# # print uncertainty_dipole_monopole(theta=uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=QSO_POSITION))
# # print "Test 13", uncertainty_dipole_monopole2(theta=uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=QSO_POSITION))
# # print "Test 12:", uncertainty_dipole_monopole(theta=uncertainty_theta(DIPOLE_RA, DIPOLE_DEC, qso=sky_position("22h20m06.757", "-28d03m23.34")))
# # print dipole_monopole(theta=uncertainty_theta(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value, qso=QSO_POSITION))
# # 
# # 
# # 
# # 
# # # wrapped_f = uncertainties.wrap(predicted_alpha)
# # # x = uncertainties.ufloat((A_0, A_err))
# # # y = uncertainties.ufloat((m_0, m_err))
# # # raz = uncertainties.ufloat((ra_0, ra_err))
# # # 
# # 
# # # measured_da_a = -1.0904e-6
# # # da_a_stat_error = 2.35e-6
# # # da_a_sys_error = 1.6549e-6
# # 
# # # print "Test3:", dipole2(QSO_RA, QSO_DEC, raz, decz)
# # # 
# # # 
# # # numerical_alpha_error =  wrapped_f(x, wrapped_dipole_angle(raz, decz), y)
# # # print numerical_alpha_error
# # # 
# # # measured_da_a_error = uncertainties.ufloat((measured_da_a, da_a_stat_error))
# # # numerical_alpha_error.std_score(measured_da_a_error)
# # 
# # # print uncertainty_theta(right_ascension=QSO_RA, declination=QSO_DEC, **dipole_monopole_dict)
# # # print uncertainty_dipole_monopole(theta=uncertainty_theta(right_ascension=QSO_RA, declination=QSO_DEC, **dipole_monopole_dict), **dipole_monopole_dict)    
# # # def dipole_only(amplitude, theta, **kwargs):
# # #     """Returns the predicted value of da/a as given by S5.3 in King et al. 2012.
# # #     
# # #     Arguments:
# # #     :param amplitude: Amplitude of dipole.
# # #     :type amplitude: number
# # #     :param theta: angle in radians between two positions considered on sky.
# # #     :type theta: number
# # #     """
# # #     return amplitude * np.cos(theta)
# # # 
# # # 
# # # def z_dipole_monopole(amplitude, redshift, beta, theta, monopole, **kwargs):
# # #     """Returns the predicted da/a given by eq. 18 in King et al. 2012.
# # #     
# # #     Arguments:
# # #     :param amplitude: Amplitude of dipole.
# # #     :type amplitude: number
# # #     :param redshift: Redshift of position considered.
# # #     :type redshift: number
# # #     :param beta: power law exponent.
# # #     :type beta: number
# # #     :param theta: angle in radians between two positions considered on sky.
# # #     :type theta: number    
# # #     :param monopole: monopole term.
# # #     :type monopole: number
# # #     """
# # #     return amplitude * redshift ** (beta) * np.cos(theta) + monopole
# # #     
# # # def r_dipole_monopole(amplitude, distance, theta, monopole, **kwargs):
# # #     """Returns the predicted da/a given by eq. 19 in King et al. 2012
# # #     
# # #     Arguments:
# # #     :param amplitude: Amplitude of dipole.
# # #     :type amplitude: number
# # #     :param distance: Distance of position considered in G Lyr.
# # #     :type distance: number
# # #     :param theta: angle in radians between two positions considered on sky.
# # #     :type theta: number    
# # #     :param monopole: monopole term.
# # #     :type monopole: number
# # #     """
# # #     return amplitude * distance * np.cos(theta) + monopole
# # #     
# # #     
# # # def r_dipole_only(amplitude, distance, theta, **kwargs):
# # #     """Returns the predicted da/a given by eq. 20 in King et al. 2012
# # #     
# # #     Arguments:
# # #     :param amplitude: Amplitude of dipole.
# # #     :type amplitude: number
# # #     :param distance: Distance of position considered in G Lyr.
# # #     :type distance: number
# # #     :param theta: angle in radians between two positions considered on sky.
# # #     :type theta: number    
# # #     :param monopole: monopole term.
# # #     :type monopole: number
# # #     """
# # #     return amplitude * distance * np.cos(theta)
# # # 
# # # models = {
# # #     dipole_monopole
# # # }
# # # # dipole = angles.AngularPosition(alpha=17.3, delta=-61)
# # 
# # # RA and DEC of position under consideration here
# # # J222
# # # qso = angles.AngularPosition(alpha=22.20, delta=-28.03)
# # # measured_da_a = -1.0904e-6
# # # da_a_stat_error = 2.35e-6
# # # da_a_sys_error = 1.6549e-6
# # 
# # 
# # # 
# # # x = uncertainties.ufloat((A_0, A_err))
# # # y = uncertainties.ufloat((m_0, m_err))
# # # raz = uncertainties.ufloat((ra_0, ra_err))
# # # decz = uncertainties.ufloat((dec_0, dec_err))
# # # 
# # 
# # # positions.append(np.radians(angles.r2d(qso.sep(dipole_m_ra_m_dec))))
# # # print "Separation angle between dipole and qso: ", round(np.degrees(positions[0]), 3), \
# # #     "degrees or", round(positions[0], 5), "radians."
# # # print "Predicted da/a: ", round(predicted_alpha_value, 10)
# # # print "Error: ", round(predicted_error, 10)
# # # print "Measured da/a: ", round(measured_da_a, 10)
# # # print "Statistical error: ", round(da_a_stat_error, 10)
# # # print "Systematic error: ", round(da_a_sys_error, 10)
# # # # Add statistical errors in quadrature -- total statistical 
# # # total_error = np.sqrt(predicted_error ** 2 + da_a_stat_error ** 2)
# # # print "Total statistical error (in quad): ", round(total_error, 10)
# # # 
# # # # Minimize difference between predicted and measured results (within systematic error)
# # # best_difference = np.abs(predicted_alpha_value - measured_da_a) - da_a_sys_error
# # # worst_difference = np.abs(predicted_alpha_value - measured_da_a) + da_a_sys_error
# # # if best_difference < 0:
# # #     # If true
# # #     print "Within systematic error"
# # # else: 
# # #     print "Best sigmas away: ", round(best_difference / total_error, 2)
# # #     print "Worst sigmas away: ", round(worst_difference / total_error, 2)
# # # 
# # # qso_total_error = np.sqrt(da_a_stat_error ** 2 + da_a_sys_error ** 2)
# # # print qso_total_error
# # # print np.sqrt(qso_total_error ** 2 + predicted_error ** 2)
# # # 
# # # # Test RA/DEC behaving like expected.
# # # # test1 = angles.AngularPosition(alpha=15.3, delta=-60)
# # # # test2 = angles.AngularPosition(alpha=15.3, delta=-40)
# # # # print angles.r2d(test1.sep(test2)), 20.
# # # # test3 = angles.AngularPosition(alpha=15.3, delta=0)
# # # # test4 = angles.AngularPosition(alpha=14.3, delta=0)
# # # # print angles.r2d(test3.sep(test4)), 360/24.
# # # 
# # # # Test of what Paolo did to get 5.9 as prediction.
# # # # Didn't work: 
# # # # print predicted_alpha(A_prefactors[0], angles.r2d(qso.sep(dipole)), m_values[0])
# # # 
# # # # Expected da/a at pole
# # # # ======================
# # # # Separation angle between dipole and qso:  0.97 degrees or 0.01693 radians.
# # # # Predicted da/a:  7.9186e-06
# # # # Error:  3.0308e-06
# # # # Measured da/a:  -1.0904e-06
# # # # Statistical error:  2.35e-06
# # # # Systematic error:  1.6549e-06
# # # # Total statistical error (in quad):  3.8352e-06
# # # # Sigmas away:  1.92
# # # 
# # # 
# # # # np.sqrt(1.1 ** 2 + 1.4 ** 2)
# # # 
# # # print np.average(alpha_mc), np.std(alpha_mc)
# # # print predicted_alpha(A_0, positions[0], m_0)
# # # print np.degrees(positions[0])
# # # print np.degrees(np.radians(angles.r2d(qso.sep(angles.AngularPosition(alpha=ra_0, delta=dec_0)))))
# # # print predicted_alpha(A_0, np.degrees(np.radians(angles.r2d(qso.sep(angles.AngularPosition(alpha=A_0, delta=dec_0))))), m_0)
# # # 
# # # 
# # # print "Separation angle between dipole and qso: ", round(np.degrees(positions[0]), 3), \
# # #     "degrees or", round(positions[0], 5), "radians."
# # # predicted_alpha_value = predicted_alpha(A_prefactors[0], positions[0], m_values[0])
# # # monte_carlo_alpha = np.average(alpha_mc)
# # # monte_carlo_error = np.std(alpha_mc)
# # # print "Predicted da/a: ", round(predicted_alpha_value, 10)
# # # print "Monte Carlo da/a: ", round(monte_carlo_alpha, 10)
# # # print "Monte Carlo error: ", round(monte_carlo_error, 10)
# # # print "Measured da/a: ", round(measured_da_a, 10)
# # # print "Statistical error: ", round(da_a_stat_error, 10)
# # # print "Systematic error: ", round(da_a_sys_error, 10)
# # # # Add statistical errors in quadrature -- total statistical 
# # # total_error = np.sqrt(monte_carlo_error ** 2 + da_a_stat_error ** 2)
# # # print "Total statistical error (in quad): ", round(total_error, 10)
# # # 
# # # # Minimize difference between predicted and measured results (within systematic error)
# # # best_difference = np.abs(predicted_alpha_value - measured_da_a) - da_a_sys_error
# # # worst_difference = np.abs(predicted_alpha_value - measured_da_a) + da_a_sys_error
# # # if best_difference < 0:
# # #     # If true
# # #     print "Within systematic error"
# # # else: 
# # #     print "Best sigmas away: ", round(best_difference / total_error, 2)
# # #     print "Worst sigmas away: ", round(worst_difference / total_error, 2)
# # # 
# # # qso_total_error = np.sqrt(da_a_stat_error ** 2 + da_a_sys_error ** 2)
# # # print qso_total_error
# # # print np.sqrt(qso_total_error ** 2 + monte_carlo_error ** 2)
# # # 
# # # 
# # # cospositions = [np.cos(x) for x in positions]
# # # cosposition_err = np.max(cospositions) - np.min(cospositions)
# # # np.sqrt(np.cos(positions[0])**2 * A_err**2 + A**2 * cosposition_err**2 + 1**2 * m_err**2)
# # # np.sqrt(np.cos(positions[0])**2 * A_err**2 + A_0**2 * (cosposition_err/2)**2 + 1**2 * m_err**2)
