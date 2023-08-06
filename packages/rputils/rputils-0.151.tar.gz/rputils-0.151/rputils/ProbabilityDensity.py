#!/usr/bin/env python
# Written by: DGC

# python imports
import itertools
# local imports

#==============================================================================
class ProbabilityDensity(object):
    
    def __init__(self, dice_pool):
        self.dice_pool = dice_pool
        self.make_density()

    def __getitem__(self, index):
        ret = None
        if index in self.density:
            ret = self.density[index] / float(self.possibilities)
        else:
            ret = 0
        return ret

    def make_density(self):
        self.find_possibilities()
        if (self.possibilities < 1000000):
            possible = []
            for dice in self.dice_pool.pool:
                # do this once for each dice of that type in the pool
                for i in range(self.dice_pool[dice]):
                    current = []
                    for j in range(1, dice.sides + 1):
                        current.append(j)
                    possible.append(current)
            
            self.density = dict()
            for possibility in list(itertools.product(*possible)):
                score = 0
                for result in possibility:
                    score += result
                if score in self.density:
                    self.density[score] += 1
                else:
                    self.density[score] = 1
        else:
            # too many to calculate
            self.density = None
            
    def find_possibilities(self):
        """ Finds the number of possible outcomes in the density function. """
        if (len(self.dice_pool) == 0):
            self.possibilities = 0
        else:
            self.possibilities = 1
            for dice in self.dice_pool:
                self.possibilities *= (dice.sides ** self.dice_pool[dice])
