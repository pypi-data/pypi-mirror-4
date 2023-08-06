#!/usr/bin/env python
# Written by: DGC

# python imports
import random

# local imports
import ProgramUtils

#==============================================================================
class Dice(object):
    
    def __init__(self, sides):
        self.sides = sides
        self.expected = sum(range(1, self.sides + 1)) / float(self.sides)

    def roll(self):
        random.seed()
        return random.randrange(1, self.sides + 1)
        
#==============================================================================
class DicePool(object):
    
    def __init__(self):
        self.dice = dict()

    @property
    def pool(self):
        """ Return a list with one DiceEntry for each die in the pool. """
        return self.dice.keys()
            
    @property
    def expected(self):
        expected = 0
        for die in self:
            expected += (Dice(die.sides).expected * self.dice[die])
        return expected

    @property
    def maximum(self):
        maximum = 0
        for dice in self:
            maximum += (dice.sides * self[dice])
        return maximum

    @property
    def minimum(self):
        minimum = 0
        for dice in self:
            minimum += self[dice]
        return minimum

    def roll(self):
        total = 0
        for die in self.pool:
            for i in range(self[die]):
                total += Dice(die.sides).roll()
        return total

    def add_dice(self, name):
        dice = ProgramUtils.Program().dice_library[name]
        # add one to the dictionary if it exists, otherwise make it equal to 1.
        if (dice in self.dice):
            self.dice[dice] += 1
        else:
            self.dice[dice] = 1

    def remove_dice(self, name):
        dice = ProgramUtils.Program().dice_library[name]
        # assert there is a dice
        assert dice in self.dice, "No " + name + " in dictionary."
        # remove from dictionary if it is 1, otherwise decrement it
        if (self.dice[dice] == 1):
            del self.dice[dice]
        else:
            self.dice[dice] -= 1

    def clear(self):
        self.dice = dict()

    #--------------------------------------------------------------------------
    # Magic methods to implement this as a list
    #--------------------------------------------------------------------------

    def __len__(self):
        """ Returns the number of dice in the pool. """
        return len(self.pool)

    def __getitem__(self, dice):
        return self.dice[dice]

    def __iter__(self):
        """ Iterate over the dice in the pool. """
        return iter(self.pool)
