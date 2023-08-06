#!/usr/bin/env python
# Written by: DGC

# python imports
import os

# local imports

resource_directory = os.path.dirname(__file__)

#==============================================================================
def find_resource_file(file_name):
    """ 
    file_name should be a relative path under Resources, this will return the 
    absolute path of the file.
    """
    path = os.path.join(resource_directory, file_name)
    assert os.path.isfile(path)
    return path

#==============================================================================
def find_image_file(file_name):
    """ 
    file_name should be a relative path under Resources, this will return the 
    absolute path of the file.
    """
    return find_resource_file(os.path.join("Images", file_name))

#==============================================================================
def resource_file_exists(file_name):
    """ Returns if file_name exists """
    path = os.path.join(resource_directory, file_name)
    return os.path.isfile(path)
