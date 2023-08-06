#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Produce print-quality TIFFs and JPGs from a directory of PDFs.

    * Works on multilayer PDFs and some types of files with bad vectors
    * Each page of a multi-page PDF will become one TIFF
    * Hard-coded values for output file format and DPI
    * ImageMagic (convert) must be installed and on your system path
 
    Usage: serenifypdf <pdf_fil> [<tif dpi>] [--preserve-ps]
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
import shutil
from argparse import ArgumentParser

# Compentsate for path silliness when running directly
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
from pdfserenitynow import pdfbursttops
from pdfserenitynow import psconverttotif


QUALITY = '10' # JPG quality (not currently used)
OUTPUT_FORMAT = 'tif' # TIFF is the only current conversion target


RETURN_VALUES = {0: "No errors.",
                 1: "Non-critical errors during some conversions.",
                 2: "Critical error while converting from PDF to PS.",
                 3: "Critical error while converting from PS to TIF.",}


def parse_command_line():
    ''' Parses the command line arguments.
        Returns the arguments dict.
    '''
    parser = ArgumentParser(description='Produce print-quality TIFFs '+\
                                        'from a directory of PDFs')
    parser.add_argument('pdf_file', help='Directory with PDFs to convert')
    parser.add_argument('-dpi', type=int, default=300,
                        help='DPI of output TIFFs. Default: 300')
    parser.add_argument('--preserve-ps', 
                        dest='preserve_ps',
                        action='store_const',
                        const=True,
                        default=False,
                        help="Do not delete the intermediate postscript files")
    return parser.parse_args()


def main():
    ''' Runs the script.
    '''
    args = parse_command_line()
    had_error = False
    print("Converting from PDF to PS: {0}".format(args.pdf_file,))
    base_dir = os.path.join(os.path.dirname(args.pdf_file), 
                            os.path.splitext(args.pdf_file)[0]) # Name of file without extension
    ps_dir = os.path.join(base_dir, 'PS')
    ret_val = pdfbursttops.burstit(args.pdf_file, ps_dir)
    if ret_val > 0:
        had_error = True
        print("Encountered an error during conversion from PDF to PS of {0}.".format(args.pdf_file,))
        print("The error was: {0}".format(pdfbursttops.RETURN_VALUES[ret_val]))
        if ret_val >= 1 and ret_val <= 5:
            print("This is a critical error, so the conversion has been aborted.")
            return(2)
        else:
            print("This is not a critical error, so the conversion will continue.")
    
    # Get the list of files to convert and start converting from PS to TIF  
    tif_dir = os.path.join(base_dir, 'TIF')
    ps_files_all = os.listdir(ps_dir)
    for fil in ps_files_all:
        fil_base, fil_ext = os.path.splitext(fil)
        if fil_ext.lower() == '.ps':
            ps_full_path = os.path.join(ps_dir, fil)
            tif_full_path = os.path.join(tif_dir, fil_base+'.tif')
            print("Converting from PS to TIF: {0}".format(ps_full_path,))
            ret_val = psconverttotif.convert_it(ps_full_path, tif_full_path, args.dpi)
            if ret_val > 0:
                had_error = True
                print("Encountered an error during conversion from PS to TIF of {0}.".format(ps_full_path,))
                print("The error was: {0}".format(psconverttotif.RETURN_VALUES[ret_val]))
                if ret_val == 2:
                    print("This is a critical error and all conversions have been aborted.")
                    return(3)
                else: # 3, 4
                    print("Going on to the next PS file.")
    

    if not args.preserve_ps:
        print("Deleting intermediate postscript files at {0}".format(ps_dir))
        shutil.rmtree(ps_dir)
        
    if had_error:
        print("Finished conversions, but there were some problems.")
        return 1
    else:
        print("Finished all conversions without problems.")
        return 0


if __name__ == '__main__':
    ret_val = main()
    exit(ret_val)
