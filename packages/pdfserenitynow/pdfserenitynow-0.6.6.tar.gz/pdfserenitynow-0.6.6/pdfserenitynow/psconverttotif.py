#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Convert a Postscript file into a TIF.
    * PS conversion performed by convert (imagemagick).
'''


__author__ = "Ben Rousch"
__copyright__ = "Copyright 2013, Ben Rousch"
__credits__ = ["Ben Rousch"]
__license__ = "MIT"
__version__ = "0.6.6"
__maintainer__ = "Ben Rousch"
__email__ = "brousch@gmail.com"
__status__ = "Development"


import os
import subprocess

from pdfserenitynow.psn_utils import ExeNotFound, find_exe


RETURN_VALUES = {0: "Success: No errors",
                 2: "Error 2: Couldn't find the 'convert' executable (imagemagick)",
                 3: "Error 3: Cannot read from PS file",
                 4: "Error 4: Imagemagick error while converting file", }


def convert_it(ps_fil, tif_fil, density):
    try:
        convert_path = find_exe("convert")
    except ExeNotFound:
            print("Error: `convert` is not installed or is not on the path.")
            print("       I can't continue until convert is installed and on the path.")
            print("       You may need to install imagemagick.")
            return(2)
    
    # Create the TIF location if it doesn't already exist
    try:
        os.makedirs(os.path.dirname(tif_fil))
    except OSError:
        pass
    
    ret_val = subprocess.call([convert_path,
                               '-compress', 'Group4',
                               '-density', str(density),
                               '-type', 'Grayscale', #1.1 min/file
                               '-background', 'white',
                               '-flatten',
                               ps_fil,
                               tif_fil ])
    if not ret_val:   # No return value means success
        print("Successfully converted: {0}.".format(tif_fil,))
        return(0)
    else:
        print("Imagemagick error while converting: {0}".format(ps_fil,))
        return(4)
    