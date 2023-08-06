#!/usr/bin/env python
import angles
import numpy as np
import dipole_error
import uncertainties
from uncertainties.umath import *
import unittest

DIP_RA = 17.3
DIP_RA_ERR = 1.0
DIP_DEC = -61.0
DIP_DEC_ERR = 10.0
DIPOLE_RA = uncertainties.ufloat((DIP_RA, DIP_RA_ERR))
DIPOLE_DEC = uncertainties.ufloat((DIP_DEC, DIP_DEC_ERR))

class SkyPositionTest(unittest.TestCase):
    """docstring """
    
    # test angles.r correctly find separation between known RA and DECs
    # 
    # def test_wrap_works_simple(self):
    #     """docstring for test_wrap_works_simple"""
    #     self.assertAlmostEqual(dipole_error.sky_position(DIP_RA, DIP_DEC), dipole_error.wrapped_sky_position(DIP_RA, DIP_DEC))
    # 
    # def test_wrap_works_nominal(self):
    #     """docstring for test_wrap_works_nominal"""
    #     self.assertAlmostEqual(dipole_error.sky_position(DIP_RA, DIP_DEC), dipole_error.wrapped_sky_position(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value))

    # def test_wrap_works_with_uncertainties(self):
    #     """docstring for test_wrap_understands_uncertainties"""
    #     standard_result = dipole_error.sky_position(DIP_RA, DIP_DEC)
    #     print standard_result.alpha.r, standard_result.delta.r, DIPOLE_RA, DIPOLE_DEC
    #     nominal_uncertain_result = dipole_error.wrapped_sky_position(DIPOLE_RA, DIPOLE_DEC)
    #     print nominal_uncertain_result
    #     self.assertAlmostEqual(standard_result, nominal_uncertain_result.nominal_value)

# class MonteCarloTest(unittest.TestCase):
#     """docstring for MonteCarloTest"""
#     def __init__(self, arg):
#         super(MonteCarloTest, self).__init__()
#         self.arg = arg
#         
#     def test_mc_theta(self):
#         DIP_RA = 17.3
#         DIP_RA_ERR = 1.0
#         DIP_DEC = -61.0
#         DIP_DEC_ERR = 10.0        
#         first = theta()
#         QSO_RA = "22h20m06.757" # RA
#         QSO_DEC = "-28d03m23.34" # DEC
#         self.assertAlmostEqual(first, second, places=2, msg=None, delta=None)
#         # self.assertEqual()
#         
#     # def test_mc_(self):
#     #     """docstring for test_mc_"""
#     #     assert
# 
# class DipoleErrorTest(unittest.TestCase):
#     """"""
#     def test_theta_transpose(self):
#         """docstring for test_theta"""
#         QSO_POSITION = dipole_error.QSO_POSITION
#         DIPOLE_POSITION = dipole_error.DIPOLE_POSITION
#         QSO_DIPOLE_ANGLE = angles.r2d(QSO_POSITION.sep(DIPOLE_POSITION))
#         DIPOLE_QSO_ANGLE = angles.r2d(DIPOLE_POSITION.sep(QSO_POSITION))
#         self.assertEqual(QSO_DIPOLE_ANGLE, DIPOLE_QSO_ANGLE)
#     
#     def test_sky_position_uncertainties(self):
#         """docstring for test_sky_position_uncertainties"""
#         DIP_RA = 17.3
#         DIP_RA_ERR = 1.0
#         DIP_DEC = -61.0
#         DIP_DEC_ERR = 10.0
#         DIPOLE_RA = uncertainties.ufloat((DIP_RA, DIP_RA_ERR))
#         DIPOLE_DEC = uncertainties.ufloat((DIP_DEC, DIP_DEC_ERR))
#         NOMINAL = dipole_error.sky_position(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value)
#         WRAPPED = dipole_error.wrapped_sky_position(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value)
#         self.assertAlmostEqual(NOMINAL, WRAPPED)
#         
#     # TODO test that each piece of the equation adds uncertainty
#     # TODO test RA +/- 
#     # TODO test DEC +/- 
#     # TODO test AMPLITUDE +/- 
#     # TODO test MONOPOLE +/- 
#     # TODO test QSO RA
#     # TODO test QSO DEC
#     # #----------------------------------------------------------------------
#     # def test_creation(self):
#     #     """docstring for test_creation"""
#     #     my_obj = dipole_error.MyClass()
#     #     self.assert_(myobj)
#     
#     # def test_all_ones(self):
#     #     """Constructor"""
#     #     game = Game()
#     #     pins = [1 for i in range(11)]
#     #     game.roll(11, pins)
#     #     self.assertEqual(game.score, 11)

    
if __name__ == "__main__":
    unittest.main()
    
# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)