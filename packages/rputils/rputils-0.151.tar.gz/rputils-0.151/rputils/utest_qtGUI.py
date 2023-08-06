#!/usr/bin/env python
# Written by: DGC

# python imports
import sys
import unittest

from PyQt4 import QtGui, QtCore, QtTest

# local imports
import qtGUI

#==============================================================================
class utest_qtGUI(unittest.TestCase):

    def setUp(self):
        app = qtGUI.MainApp()
        self.dice_selecter = app.window.dice_selecter.dice_selecter

    def test_dice_order(self):
        dice = ["D3", "D4", "D6", "D8", "D10", "D12", "D20", "D100"]
        for i, die in enumerate(dice):
            button = self.dice_selecter.layout.itemAt(i).widget()
            message = str(i) + "th widget is not a " + die
            self.assertEqual(button.toolTip(), die, message)

#==============================================================================
if (__name__ == "__main__"):
    unittest.main(verbosity=2)
