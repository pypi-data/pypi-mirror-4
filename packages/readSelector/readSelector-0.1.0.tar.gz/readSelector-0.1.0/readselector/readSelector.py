#!/usr/bin/env python
###############################################################################
#                                                                             #
#    readSelector.py                                                          #
#                                                                             #
#    Wraps coarse workflows                                                   #
#                                                                             #
#    Copyright (C) Michael Imelfort                                           #
#                                                                             #
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__author__ = "Michael Imelfort"
__copyright__ = "Copyright 2012"
__credits__ = ["Michael Imelfort"]
__license__ = "GPL3"
__version__ = "0.1.0"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"
__status__ = "Development"

###############################################################################

import sys
import os 
import argparse
import gzip

# readSelector imports
from fileParser import FileParser

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class FileOpenException(BaseException): pass

###############################################################################

class ReadSelectorOptionsParser():
    def __init__(self): pass
    
    def readSelectorUnpaired(self, options, shuffled=False):
        """Parse unpaired or shuffled reads"""
        FP = FileParser()

        if options.outfile[0] == '':
            # stdout!
            outfh = sys.stdout
        else:
            # check if we need to zip output
            if options.outfile[0].endswith('.gz'):
                fopen = gzip.open
            else:
                fopen = open

            try:
                outfh = fopen(options.outfile[0], "w") 
            except:
                raise FileOpenException("Could not open output file!") 
    
        # extract the reads
        if shuffled:
            FP.extractShuffledReads(options.files, outfh, options.number, options.verbose)
        else:
            FP.extractUnpairedReads(options.files, outfh, options.number, options.verbose)
        
        # clean up
        outfh.close()
    
    def readSelectorPaired(self, options):
        """Parse paired reads"""
        FP = FileParser()
        # we need to find the file type (fasta, fasta.gz, etc...)
        file_type = os.path.splitext(options.files[0].replace('.gz',''))[1]
        if not options.large:
            file_type += '.gz'
            fopen = gzip.open
        else:
            fopen = open
        if options.prefix[0] == '':
            # stdout!
            outfh_1 = sys.stdout
            outfh_2 = sys.stdout
        else:
            try:
                outfh_1 = fopen("%s_1%s" % (options.prefix[0], file_type), "w") 
                outfh_2 = fopen("%s_2%s" % (options.prefix[0], file_type), "w") 
            except:
                raise FileOpenException("Could not open output files!") 

        # extract the reads
        FP.extractPairedReads(options.files, [outfh_1, outfh_2], options.number, options.verbose)

        # clean up
        outfh_1.close()
        outfh_2.close()
        
    def parseOptions(self, options):
        """Parse user options and call the correct pipeline(s)"""
        
        if(options.subparser_name == 'unpaired'):
            # unpaired read parsing
            if not options.outfile:
                options.outfile = ['']
            if options.verbose:
                print "Extracting from unpaired files..."
            self.readSelectorUnpaired(options)
                            
        elif(options.subparser_name == 'shuffled'):
            # shuffled read parsing
            if not options.outfile:
                options.outfile = ['']
            if options.verbose:
                print "Extracting from shuffled files..."
            self.readSelectorUnpaired(options, shuffled=True)
                            
        elif(options.subparser_name == 'paired'):
            # paired read parsing
            if not options.prefix:
                options.prefix = ['']
            if options.verbose:
                print "Extracting from paired files..."
            self.readSelectorPaired(options)

        return 0

###############################################################################
###############################################################################
###############################################################################
###############################################################################
