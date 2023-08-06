#!/usr/bin/env python
# Written by: DGC

# python imports
import unittest

# local imports
import DiceRollers
import ProbabilityDensity

#==============================================================================
class utest_ProbabilityDensity(unittest.TestCase):

    def test_one_d6(self):
        pool = DiceRollers.DicePool()
        pool.add_dice("D6")
        density = ProbabilityDensity.ProbabilityDensity(pool)
        self.assertEqual(
            density[1], 
            1 / 6.0,
            "Probability of rolling a 1 is 1/6"
            )
        self.assertEqual(density[0], 0, "Probability of rolling a 0 is 0")
    
    def test_two_d6(self):
        pool = DiceRollers.DicePool()
        pool.add_dice("D6")
        pool.add_dice("D6")
        density = ProbabilityDensity.ProbabilityDensity(pool)
        self.assertEqual(density[1], 0, "Probability of rolling a 1 is 0")
        self.assertEqual(
            density[2],
            1 / 36.0,
            "Probability of rolling a 2 is 1/36"
            )
        self.assertEqual(
            density[7],
            1 / 6.0,
            "Probability of rolling a 7 is 1/6"
            )
    
    def test_loads_of_dice(self):
        pool = DiceRollers.DicePool()
        pool.add_dice("D100")
        pool.add_dice("D100")
        pool.add_dice("D100")
        pool.add_dice("D100")
    
        density = ProbabilityDensity.ProbabilityDensity(pool)
        self.assertIs(
            density.density, 
            None,
            "Too many possibilities to calculate."
            )
    
#==============================================================================
if (__name__ == "__main__"):
    unittest.main(verbosity=2)
