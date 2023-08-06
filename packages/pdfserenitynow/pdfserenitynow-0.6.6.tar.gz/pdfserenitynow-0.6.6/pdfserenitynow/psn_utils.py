#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Various utilities used by PdfSerenityNow

    * count_pdf_pages: counts the number of pages in a PDF file
    * is_pdf_package: determines if a PDF is a PDF Package
    * verify_file_read_access: verifies that we can read a file
    * whereis_exe: finds a program on the system path
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


def count_pdf_pages(pdf):
    pdfinfo = find_exe('pdfinfo')
    info = subprocess.getoutput(pdfinfo+' '+pdf)
    page_count = 0
    if info.startswith("Error:"): # File not found or invalid PDF file
        raise IOError(info)
    lines = info.split('\n')
    for line in lines:
        if line.startswith("Pages:"):
            page_count = int(line.split()[1])
    return page_count


def is_pdf_package(pdf, preserve_check_file=False):
    ''' Returns True if the file is a PDF Package.
        Returns False if the file is not a package.
        You may want to preserve the text file generated to aid with debugging.
        What is a PDF Package? http://kb.datalogics.com/articles/FAQ/What-is-a-PDF-Package-or-a-PDF-Portfolio-1322829100147
    '''
    page_count = count_pdf_pages(pdf)
    if page_count == 1: # Package always shows 1 page
        pdftotext = find_exe('pdftotext')
        # TODO: Check and report failure here
        fil_base = os.path.splitext(pdf)[0]
        text_file = os.path.join(os.path.dirname(pdf), fil_base+'.txt')
        ret_val = subprocess.call([pdftotext,
                                   '-f', '1',
                                   '-l', '1',
                                   pdf, text_file ])
        # TODO: Check and report failure on ret_val
        package_text = "Multiple files are bound together in this PDF Package."
        f = open(text_file, "r")
        line = f.readline()
        f.close()
        if not preserve_check_file:
            os.remove(text_file)
            # TODO: Check and report failure here
        if line.startswith(package_text):
            return True
    return False


class ExeNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def find_exe(program):
    ''' Tries to find 'program' on the system path.
        Returns the path if it is found.
        Raises an ExeNotFound exception if it's not found.
    '''
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
            not os.path.isdir(os.path.join(path, program)):
            return os.path.join(path, program)
    raise ExeNotFound("Couldn't locate `{0}` on the system path.".format(program,))
