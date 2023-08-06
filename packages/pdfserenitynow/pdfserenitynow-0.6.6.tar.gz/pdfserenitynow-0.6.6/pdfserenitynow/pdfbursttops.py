#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Split a PDF into individual Postscript pages.

    * PDF reading and Postscript generation performed by Poppler.
    * Postscript files named based on `<original file name>-<page number>.PS`.

    Usage: pdftoindps <pdf_file> <ps_dir>
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

from pdfserenitynow.psn_utils import count_pdf_pages
from pdfserenitynow.psn_utils import is_pdf_package
from pdfserenitynow.psn_utils import ExeNotFound, find_exe


RETURN_VALUES = {0: "Success: No errors",
                 1: "Error 1: Couldn't find `pdftotext` (poppler-utils)",
                 2: "Error 2: Couldn't find `pdftops` (poppler-utils)",
                 3: "Error 3: PDF file not found or invalid PDF file.",
                 4: "Error 4: Couldn't find `pdfinfo` (poppler-utils)",
                 5: "Error 5: Cannot handle PDF Packages",
                 6: "Error 6: Zero pages in PDF or not a PDF file",
                 7: "Error 7: Non-critical error while extracting a PDF" }


def extract_ps_page_from_pdf(pdftops, pdf, page_num, ps):
    ''' Extracts a single PDF page to a Postcript file
    '''
    ret_val = subprocess.call([pdftops,
                                '-f', str(page_num),
                                '-l', str(page_num),
                                '-origpagesizes',
                                pdf,
                                ps])
    if not ret_val:   # No return value means success
        print("Successfully extracted {0} from {1}".format(ps, pdf))
    else:
        print("Error while extracting {0} from {1}".format(ps, pdf))
    return ret_val


def burstit(pdf_fil, ps_dir):
    ''' Main function: split the PDF into postscript files
    '''

    # Make sure pdftops in installed and working
    try:
        pdftops_path = find_exe("pdftops")
    except ExeNotFound:
        print("Error: `pdftops` is not installed or is not on the path.")
        print("       I can't continue until `pdftops` is installed and on the path.")
        print("       You may need to install the poppler-utils package.")
        return(2) 

    # Set postscript storage dir based on pdf's location
    try:
        os.makedirs(ps_dir)
    except OSError:
        pass
    
    # Check to see if file is a PDF Package. Packages are not handled in this script.
    try:
        if is_pdf_package(pdf_fil):
            print("Error: {0} appears to be a PDF package.".format(pdf_fil))
            print("       Sorry, I can't handle those buggers.")
            print("       Use PDFTK to unpack the package then run this script on the unpacked PDFs.")
            return(5)
    except ExeNotFound:
        print("Error: `pdftotext` is not installed or is not on the path.")
        print("       I can't continue until `pdftotext` is installed and on the path.")
        print("       You may need to install the poppler-utils package.")
        return(1)
    except IOError:
        print("Error: PDF file not found or invalid PDF file:")
        print("       {0}".format(pdf_fil))
        print("       Make sure the file exists and is a valid PDF file.")
        return(3)
        
    # Count the number of pages in the PDF file
    try:
        num_pages_pdf = count_pdf_pages(pdf_fil)
    except ExeNotFound:
        print("Error: `pdfinfo` is not installed or is not on the path.")
        print("       I can't continue until `pdfinfo` is installed and on the path.")
        print("       You may need to install the poppler-utils package.")
        return(4)
    except IOError:
        print("Error: PDF file not found or invalid PDF file:")
        print("       {0}".format(pdf_fil))
        print("       Make sure the file exists and is a valid PDF file.")
        return(3)
        
    print("There are {0} pages in {1}".format(num_pages_pdf, pdf_fil))
    if num_pages_pdf == 0:
        print("Error: counted zero pages in the PDF, or it's not a PDF file.")
        print("       Nothing to do.")
        print("       Make sure you have specified a valid PDF file.")
        return(6) 

    # Extract the PDF pages into Postscript files
    ps_prefix = os.path.splitext(os.path.basename(pdf_fil))[0]
    extraction_errors = 0
    for p in range(0, num_pages_pdf):
        print("Processing page {0}".format(p+1,))
        ps_filename = "{0}-{1:0>4d}.PS".format(ps_prefix, p+1) # prefix-0001.PS, prefix-0002.PS, etc
        ps_pathfile = os.path.join(ps_dir, ps_filename)
        ret_val = extract_ps_page_from_pdf(pdftops_path, pdf_fil, p, ps_pathfile)
        if ret_val:
            extraction_errors += 1
    if extraction_errors:
        print("There were {0} errors while extracting PDFs.".format(extraction_errors,))
        return(7)
    else:
        print("All of the pages from {0} have been extracted to Postscript files in {1}.".format(pdf_fil, ps_dir))
        return 0
