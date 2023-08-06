#!/usr/bin/env python
import angles
import numpy as np
import dipole_error
import uncertainties
from uncertainties.umath import *
import random
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
class StatisticalSeparationTest(unittest.TestCase):
    """docstring for StatisticalSeparationTest"""
    
    def test_statistical_difference(self):
        """docstring for test_statistical_difference"""
        MEASURE_1 = 2.3
        MEASURE_1_ERR = 2.3
        MEASURE_2 = 4.6
        MEASURE_2_ERR = 2.3
        self.assertEqual(2.3 / np.sqrt(MEASURE_1_ERR**2 + MEASURE_2_ERR**2), \
            dipole_error.statistical_difference(uncertainties.ufloat((MEASURE_1, MEASURE_1_ERR)), \
                                                uncertainties.ufloat((MEASURE_2, MEASURE_2_ERR))))

    def test_systematic_positive(self):
        """check that negative systematic error raises exception."""
        self.assertRaises(dipole_error.NegativeError, \
                            dipole_error.statistical_difference_systematic, \
                            DIPOLE_RA, \
                            DIPOLE_DEC, \
                            -0.3)
    
    def test_result_within_statistical_range(self):
        """docstring"""
        measure_1 = uncertainties.ufloat((5.0, 1.5))
        measure_2 = uncertainties.ufloat((10.0, 1.1))        
        systematic_error = 1.0
        check_total_sys = np.sqrt(1.5**2 + 1.1**2)
        closest = 4.0
        farthest = 6.0
        return1, return2 = dipole_error.statistical_difference_systematic(measure_1, measure_2, systematic_error)
        self.assertAlmostEqual(return1, closest / check_total_sys)
        self.assertAlmostEqual(return2, farthest / check_total_sys)
        
        # test if overlapping -- zero returned.
        measure_1 = uncertainties.ufloat((5.0, 1.5))
        measure_2 = uncertainties.ufloat((5.5, 1.1))        
        systematic_error = 1.0
        check_total_sys = np.sqrt(1.5**2 + 1.1**2)
        closest = 0.0 # the minimum should be zero.
        farthest = 1.5
        return3, return4 = dipole_error.statistical_difference_systematic(measure_1, measure_2, systematic_error)
        self.assertAlmostEqual(return3, closest / check_total_sys)
        self.assertAlmostEqual(return4, farthest / check_total_sys)
        
    # test_prediction < measurement
    # if either one has no std; that std fraction is correct
    # prediction = measurement
    # prediction > measurement
    
    
class DipoleErrorTest(unittest.TestCase):
    """"""
#     def test_theta_transpose(self):
#         """docstring for test_theta"""
#         QSO_POSITION = dipole_error.QSO_POSITION
#         DIPOLE_POSITION = dipole_error.DIPOLE_POSITION
#         QSO_DIPOLE_ANGLE = angles.r2d(QSO_POSITION.sep(DIPOLE_POSITION))
#         DIPOLE_QSO_ANGLE = angles.r2d(DIPOLE_POSITION.sep(QSO_POSITION))
#         self.assertEqual(QSO_DIPOLE_ANGLE, DIPOLE_QSO_ANGLE)
#     
    # def test_dipole_monopole(self):
    #     """docstring for test_dipole_monopole"""
    #     MEASURED_ALPHA = uncertainties.ufloat((-1.09e-6, 2.35e-6))
    #     SYSTEMATIC = 1.65e-6
    #     measure_1 = dipole_error.dipole_monopole()
    #     measure_2 = MEASURED_ALPHA
    #     # print dipole_error.statistical_difference_systematic(measure_1, measure_2, SYSTEMATIC)
    #     print dipole_error.report_stat_difference(measure_1, measure_2, SYSTEMATIC, round_places=2)
        
        
    # def test_sky_position_uncertainties(self):
    #     """docstring for test_sky_position_uncertainties"""
    #     NOMINAL = dipole_error.sky_position(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value)
    #     WRAPPED = dipole_error.wrapped_sky_position(DIPOLE_RA.nominal_value, DIPOLE_DEC.nominal_value)
    #     self.assertAlmostEqual(NOMINAL, WRAPPED)
        
#     # TODO test that each piece of the equation adds uncertainty
#     # TODO test RA +/- 
#     # TODO test DEC +/- 
#     # TODO test AMPLITUDE +/- 
#     # TODO test MONOPOLE +/- 
#     # TODO test QSO RA
#     # TODO test QSO DEC

    
if __name__ == "__main__":
    unittest.main()
    
# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# class TestSequenceFunctions(unittest.TestCase):
# 
#     def setUp(self):
#         self.seq = range(10)
# 
#     def test_shuffle(self):
#         # make sure the shuffled sequence does not lose any elements
#         random.shuffle(self.seq)
#         self.seq.sort()
#         self.assertEqual(self.seq, range(10))
# 
#         # should raise an exception for an immutable sequence
#         self.assertRaises(TypeError, random.shuffle, (1,2,3))
# 
#     def test_choice(self):
#         element = random.choice(self.seq)
#         self.assertTrue(element in self.seq)
# 
#     def test_sample(self):
#         with self.assertRaises(ValueError):
#             random.sample(self.seq, 20)
#         for element in random.sample(self.seq, 5):
#             self.assertTrue(element in self.seq)
