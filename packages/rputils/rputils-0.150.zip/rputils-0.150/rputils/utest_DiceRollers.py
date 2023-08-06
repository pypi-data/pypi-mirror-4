#!/usr/bin/env python
# Written by: DGC

# python imports
import unittest

# local imports
import DiceRollers

#==============================================================================
class utest_DiceRollers(unittest.TestCase):

    def test_range(self):
        for i in range(3, 21):
            die = DiceRollers.Dice(i)
            for j in range(100000):
                num = die.roll()
                assert 1 <= num, "num is under 1"
                assert num <= i, "num is more than it should be"
                assert type(num) == int
            self.assertTrue(True, "Worked for a d" + str(i))
    
    def test_expected(self):
        d3 = DiceRollers.Dice(3)
        self.assertEqual(d3.expected, 2, "D3 expected value is correct.")
    
        d4 = DiceRollers.Dice(4)
        self.assertEqual(d4.expected, 2.5, "D4 expected value is correct.")
    
        d5 = DiceRollers.Dice(6)
        self.assertEqual(d5.expected, 3.5, "D6 expected value is correct.")
    
        d8 = DiceRollers.Dice(8)
        self.assertEqual(d8.expected, 4.5, "D8 expected value is correct.")
    
        d10 = DiceRollers.Dice(10)
        self.assertEqual(d10.expected, 5.5, "D10 expected value is correct.")
    
        d12 = DiceRollers.Dice(12)
        self.assertEqual(d12.expected, 6.5, "D12 expected value is correct.")
    
        d20 = DiceRollers.Dice(20)
        self.assertEqual(d20.expected, 10.5, "D20 expected value is correct.")
    
        d100 = DiceRollers.Dice(100)
        self.assertEqual(
            d100.expected,
            50.5,
            "D100 expected value is correct."
            )
    
        pool = DiceRollers.DicePool()
        self.assertEqual(pool.expected, 0, "Empty pool has expected value 0.")
    
        pool.add_dice("D3")
        self.assertEqual(pool.expected, 2, "Pool [D3] has expected value 2.")
    
        pool.add_dice("D3")
        self.assertEqual(
            pool.expected, 
            4,
            "Pool [D3, D3] has expected value 4."
            )
    
        pool = DiceRollers.DicePool()
        pool.add_dice("D6")
        self.assertEqual(
            pool.expected,
            3.5,
            "Pool [D6] has expected value 3.5."
            )
    
        pool.add_dice("D6")
        self.assertEqual(
            pool.expected, 
            7,
            "Pool [D6, D6] has expected value 7."
            )
    
        pool.add_dice("D3")
        pool.add_dice("D8")
        pool.add_dice("D10")
        pool.add_dice("D12")
        pool.add_dice("D20")
        pool.add_dice("D100")
        
        message = "Pool [D3, D6, D6, D8, D10, D12, D20, D100] "
        message += "has expected value 86.5."
        self.assertEqual(pool.expected, 86.5, message)

#==============================================================================
if (__name__ == "__main__"):
    unittest.main(verbosity=2)
