#!/usr/bin/env python
# Written by: DGC

# python imports
import os
import xml.etree.ElementTree as ET

# local imports
import Resources.finder

#==============================================================================
class Program(object):
    """ Class to store all the data about the program, version etc. """
    # this is now a singleton so that data reading gets done once.

    __instance = None

    def __new__(new_singleton):
        """Override the __new__ method so that it is a singleton."""
        if not new_singleton.__instance:
            new_singleton.__instance = object.__new__(new_singleton)
            new_singleton.__instance.init()
        return new_singleton.__instance

    def init(self):
        # cache these
        self.__info = None
        self.__dice_library = None

    @property
    def info(self):
        if (self.__info is None):
            self.__info = dict()
    
            # read the information from Config.xml
            tree = ET.parse(Resources.finder.find_resource_file("Config.xml"))
            node = tree.find("ProgramInformation")
            for item in node:
                self.__info[item.tag] = item.text
        return self.__info
    
    @property
    def dice_library(self):
        if (self.__dice_library is None):
            self.__dice_library = DiceLibrary()
        return self.__dice_library

    def restore_defaults(self):
        self.__dice_library = DiceLibrary(custom = False)

#==============================================================================
class DiceLibrary(dict):

    def __init__(self, custom = True):
        super(DiceLibrary, self).__init__()
        # find Custom.xml over the "installed" version Config.xml
        exists = Resources.finder.resource_file_exists("Custom.xml")
        if (exists and custom):
            xml = Resources.finder.find_resource_file("Custom.xml")
        else:
            xml = Resources.finder.find_resource_file("Config.xml")
        
        # read the xml file to get the dice
        tree = ET.parse(xml)
        if (float(tree.getroot().get("version")) == 1):
            dice_pools = tree.findall("DicePool")
            for pool in dice_pools:
                dice = pool.findall("Dice")
                for die in dice:
                    current_dice = DiceLibraryEntry(
                        die.findtext("name"), 
                        int(die.findtext("sides")),
                        die.findtext("icon")
                        )
                    self[current_dice.label] = current_dice

    def add_dice(self, dice):
        """ 
        Adds a new DiceLibraryEntry to the Custom DicePool element in 
        Config.xml.
        """
        tree = ET.parse(Resources.finder.find_resource_file("Config.xml"))
        if (float(tree.getroot().get("version")) == 1):
            dice_pools = tree.findall("DicePool")
            for pool in dice_pools:
                if (pool.get("name") == "Custom"):
                    new_dice = ET.Element("Dice")

                    name = ET.Element("name")
                    name.text = dice.label
                    new_dice.append(name)

                    sides = ET.Element("sides")
                    sides.text = str(dice.sides)
                    new_dice.append(sides)

                    icon = ET.Element("icon")
                    icon.text = dice.image
                    new_dice.append(icon)

                    pool.append(new_dice)
                    tree.write(
                        os.path.join(
                            Resources.finder.resource_directory, 
                            "Custom.xml"
                            )
                        )
        self[dice.label] = dice
                    
#==============================================================================
class DiceLibraryEntry(object):

    def __init__(self, name, sides, image):
        self.label = name
        self.sides = sides
        self.image = None
        if (not image is None):
            self.image = self.find_image(image)

    def find_image(self, icon_name):
        # first try the installed images
        image = Resources.finder.find_image_file(icon_name)
        if (image is None):
            # if it isn't there then try as an absolute path
            if (os.path.isfile(icon_name)):
                image = icon_name
        return image
