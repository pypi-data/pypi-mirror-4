#!/usr/bin/env python
###############################################################################
#                                                                             #
#    fileParser.py                                                            #
#                                                                             #
#    Parse individual files                                                   #
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

import gzip
import zlib
import os
from sys import exc_info, exit
from random import randint
from itertools import izip

# readSelector imports

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class ReadParseException(BaseException): pass

###############################################################################

class FileParser():
    def __init__(self): pass

    def extractPairedReads(self, files, outfhs, n, verbose):
        """Randomly extract n reads from paired infh(s) and pipe to outfh(s)"""
        i = 0
        num_infiles = len(files)
        store_list = []     # for storing reads
        num_pairs_parsed = 0
        while i < num_infiles:
            # work out how to open the file 
            if files[i].endswith('.gz'):
                r1_fh = gzip.open(files[i])
                r2_fh = gzip.open(files[i+1])
            else:
                r1_fh = open(files[i])
                r2_fh = open(files[i+1])
            
            # get some file handles
            if verbose:
                print "Extracting reads from [%s %s]" % (files[i], files[i+1])
            CP1 = ContigParser()
            CP2 = ContigParser()
            r1_reads = CP1.readfq(r1_fh)
            r2_reads = CP1.readfq(r2_fh)
            paired_reads = izip(r1_reads, r2_reads)
            
            for paired_read in paired_reads:
                if num_pairs_parsed < n:
                    # we're still filling the list
                    store_list.append(paired_read)
                    num_pairs_parsed += 1
                else:
                    # the list is full, we may need to shuffle things around
                    num_pairs_parsed += 1
                    replace_index = randint(0,num_pairs_parsed)
                    if replace_index < n:
                        # we will store this guy at this index!
                        store_list[replace_index] = paired_read 
                    #else nothing

            r1_fh.close()
            r2_fh.close()
            i += 2

        # print to file
        fastq = store_list[0][0][2] != None
        for pr in store_list:
            if fastq:
                outfhs[0].write("%s\n%s\n+\n%s\n" %(pr[0][0], pr[0][1], pr[0][2]))
                outfhs[1].write("%s\n%s\n+\n%s\n" %(pr[1][0], pr[1][1], pr[1][2]))
            else:
                outfhs[0].write("%s\n%s\n" %(pr[0][0], pr[0][1]))
                outfhs[1].write("%s\n%s\n" %(pr[1][0], pr[1][1]))

    def extractShuffledReads(self, files, outfh, n, verbose):
        """Randomly extract n reads from shuffled infh(s) and pipe to outfh"""
        store_list = []     # for storing reads
        num_pairs_parsed = 0
        grab_next_index = -1 # set to anything other than -1 to store in that index
                             # set to -2 to append
                             # set to -3 to skip this read
        for infile in files:
            # work out how to open the file 
            if infile.endswith('.gz'):
                fh = gzip.open(infile)
            else:
                fh = open(infile)
            
            # get some file handles
            if verbose:
                print "Extracting reads from [%s]" % (infile)
            
            CP = ContigParser()
            for cid,seq,qual in CP.readfq(fh):
                if grab_next_index == -3:
                    #skip!
                    num_pairs_parsed += 1
                    grab_next_index = -1
                elif grab_next_index == -2:
                    # append to the last guy in the store_list
                    # no questions asked!
                    store_list[-1][1] = (cid,seq,qual)

                    num_pairs_parsed += 1
                    grab_next_index = -1
                elif grab_next_index != -1:
                    # place this guy in this position
                    store_list[grab_next_index][1] = (cid,seq,qual)

                    num_pairs_parsed += 1
                    grab_next_index = -1
                else:
                    if num_pairs_parsed < n:
                        # we're still filling the list
                        store_list.append([
                                           (cid,seq,qual),
                                           None
                                           ])
                        grab_next_index = -2
                    else:
                        # the list is full, we may need to shuffle things around
                        replace_index = randint(0,num_pairs_parsed+1)
                        if replace_index < n:
                            # we will store this guy at this iindex!
                            grab_next_index = replace_index
                            store_list[grab_next_index][0] = (cid,seq,qual)
                        else:
                            # remember to skip the next read
                            grab_next_index = -3
                
            fh.close()
        
        # now print to file
        fastq = store_list[0][0][2] != None
        for pr in store_list:
            if fastq:
                outfh.write("%s\n%s\n+\n%s\n%s\n%s\n+\n%s\n" %(pr[0][0], pr[0][1], pr[0][2], pr[1][0], pr[1][1], pr[1][2]))
            else:
                outfh.write("%s\n%s\n%s\n%s\n" %(pr[0][0], pr[0][1], pr[1][0], pr[1][1]))
        
    def extractUnpairedReads(self, files, outfh, n, verbose):
        """Randomly extract n reads from unpaired infh(s) and pipe to outfh"""
        store_list = []     # for storing reads
        num_parsed = 0
        grab_next_index = -1 # set to anything other than -1 to store in that index
                             # set to -2 to append
                             # set to -3 to skip this read
        for infile in files:
            # work out how to open the file 
            if infile.endswith('.gz'):
                fh = gzip.open(infile)
            else:
                fh = open(infile)
            
            # get some file handles
            if verbose:
                print "Extracting reads from [%s]" % (infile)
            CP = ContigParser()
            for cid,seq,qual in CP.readfq(fh):
                if num_parsed < n:
                    # we're still filling the list
                    store_list.append((cid,seq,qual))
                    num_parsed += 1
                else:
                    # the list is full, we may need to shuffle things around
                    num_parsed += 1
                    replace_index = randint(0,num_parsed)
                    if replace_index < n:
                        # we will store this guy at this index!
                        store_list[replace_index] = (cid,seq,qual) 
                    #else nothing

            fh.close()

        # print to file
        fastq = store_list[0][2] != None
        for pr in store_list:
            if fastq:
                outfh.write("%s\n%s\n+\n%s\n" % pr)
            else:
                outfh.write("%s\n%s\n" %(pr[0], pr[1]))
                
###############################################################################
###############################################################################
###############################################################################
###############################################################################

class ContigParser:
    """Main class for reading in and parsing contigs"""
    def __init__(self): pass

    def readfq(self, fp): # this is a generator function
        """https://github.com/lh3"""
        last = None # this is a buffer keeping the last unprocessed line
        while True: # mimic closure; is it a bad idea?
            if not last: # the first record or a record following a fastq
                for l in fp: # search for the start of the next record
                    if l[0] in '>@': # fasta/q header line
                        last = l[:-1] # save this line
                        break
            if not last: break
            #name, seqs, last = last[1:].split()[0], [], None
            name, seqs, last = last, [], None # we don;t want to change the line at all!
            for l in fp: # read the sequence
                if l[0] in '@+>':
                    last = l[:-1]
                    break
                seqs.append(l[:-1])
            if not last or last[0] != '+': # this is a fasta record
                yield name, ''.join(seqs), None # yield a fasta record
                if not last: break
            else: # this is a fastq record
                seq, leng, seqs = ''.join(seqs), 0, []
                for l in fp: # read the quality
                    seqs.append(l[:-1])
                    leng += len(l) - 1
                    if leng >= len(seq): # have read enough quality
                        last = None
                        yield name, seq, ''.join(seqs); # yield a fastq record
                        break
                if last: # reach EOF before reading enough quality
                    yield name, seq, None # yield a fasta record instead
                    break
                
    def parse(self, contigFile, kse):
        """Do the heavy lifting of parsing"""
        pass

###############################################################################
###############################################################################
###############################################################################
###############################################################################
