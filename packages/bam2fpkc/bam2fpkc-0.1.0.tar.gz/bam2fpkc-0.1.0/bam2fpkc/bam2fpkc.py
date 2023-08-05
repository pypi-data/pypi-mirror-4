#!/usr/bin/env python
###############################################################################
#                                                                             #
#    bam2fpkc.py                                                              #
#                                                                             #
#    Wraps coarse workflows                                                   #
#                                                                             #
#    Copyright (C) Michael Imelfort                                           #
#                                                                             #
###############################################################################
#                                                                             #
# 888                              .d8888b.  .d888          888               #
# 888                             d88P  Y88 d88P"           888               #
# 888                                    88 888             888               #
# 88888b.   8888b.  88888b.d88b.       .d88 888888 88888b.  888  888  .d8888b # 
# 888 "88b     "88b 888 "888 "88b  .od888P" 888    888 "88b 888 .88P d88P"    #
# 888  888 .d888888 888  888  888 d88P"     888    888  888 888888K  888      #
# 888 d88P 888  888 888  888  888 888"      888    888 d88P 888 "88b Y88b.    #
# 88888P"  "Y888888 888  888  888 88888888  888    88888P"  888  888  "Y8888P #
#                                                  888                        #
#                                                  888                        #
#                                                  888                        #
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
__copyright__ = "Copyright 2013"
__credits__ = ["Michael Imelfort"]
__license__ = "GPL3"
__version__ = "0.1.0"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"
__status__ = "Development"

###############################################################################

import argparse
import sys
import pysam
import numpy as np
from os import makedirs
from os.path import dirname, splitext, basename
import errno
import threading
import time

np.seterr(all='raise')  

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class CouldNotOpenMappingException(BaseException): pass
class MappingNotOpenException(BaseException): pass
class BinLengthError(BaseException): pass
 
def makeSurePathExistsFor(filename):
    """AUX: Ensure it's possible to make an output file"""
    path = dirname(filename)
    if path != '':
        try:
            makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
def getBamDescriptor(fullPath):
    """AUX: Reduce a full path to just the file name minus extension"""
    return splitext(basename(fullPath))[0]
   
###############################################################################
###############################################################################
###############################################################################
###############################################################################
     
class Bam2fpkcOptionsParser():
    def __init__(self):
        self.headers = None                 # sorted contig headers
        self.binIDs = []                    # sorted list of binIDs
        self.binAssignments = {}            # cid -> bid
        self.fpkc = {}                      # cid -> fpkc 
        self.mfpkc = {}                     # bid -> mfpkc 
        self.numBams = 0
        self.numParsed = 0
        self.bamNames = []
        
        # threads
        self.varLock = threading.Lock() # we don't have many variables here, so use one lock for everything
        self.totalThreads = 1               # single threaded by defaultly
        self.threadPool = None
        
    def parseOptions(self, options):
        """organise all the stuff what needs doing"""
        self.numBams = len(options.bams)

        # thready stuff
        self.totalThreads = options.threads
        self.threadPool = threading.BoundedSemaphore(self.totalThreads)
        
        #-----
        # check to make sure we can write out what we make
        if options.outfile != 'stdout':
            makeSurePathExistsFor(options.outfile)
        
        #-----
        # get a list of contig headers
        self.parseContigs(options.contigs)
        
        #-----
        # make space for the various measurements we'll be taking
        for cid in self.headers:
            self.fpkc[cid] = [0.0]*self.numBams

        if(options.subparser_name == 'bin'):
            # we'll also need room for the bins
            self.parseBinsFile(options.bins)
            for bid in self.binIDs:
                self.mfpkc[bid] = [[] for i in range(self.numBams)]
        #-----
        # get fancy names for the bam files we'll be parsing
        for bam_counter in range(self.numBams):
            self.bamNames.append(getBamDescriptor(options.bams[bam_counter]))        
        
        #-----
        # now parse the bams
        for bam_counter in range(self.numBams):
            t = threading.Thread(target=self.parseBamfile,
                                 args = (options.bams[bam_counter], bam_counter)
                                 )
            t.start()
            
        while True:
            # don't exit till we're done!
            self.varLock.acquire()
            doned = False
            try:
                doned = self.numParsed >= self.numBams
            finally:
                self.varLock.release()
            
            if doned:
                break
            else:
                time.sleep(1)

        #-----
        # print results        
        if options.outfile != 'stdout':
            fs = open(options.outfile, 'w')
        else:
            fs = sys.stdout

        if(options.subparser_name == 'contig'):
            self.printFpkc(fs)

        elif(options.subparser_name == 'bin'):
            self.printMfpkc(fs)

        if options.outfile != 'stdout':
            fs.close()
            
        
        return 0

    def parseBamfile(self, bamFileName, bamCounter):
        """ munge a bamfile and add the output to the global store"""
        BP = BamParser()
        BP.openBam(bamFileName)
        
        # now work out the fpkc for all contigs for this sample
        tmp_fpkc = BP.getFpkc(self.headers)

        # add to the main store but be threadsafe!
        try:
            self.varLock.acquire()
            for cid in tmp_fpkc.keys():
                self.fpkc[cid][bamCounter] = tmp_fpkc[cid] 
            self.numParsed += 1
        finally:
            self.varLock.release()

        # clean up
        BP.closeBam()

    def parseContigs(self, contigs_file):
        """Parse the contigs file and get headers"""
        CP = ContigParser()
        try:
            with open(contigs_file) as con_fh:
                self.headers = CP.getHeaders(con_fh)
        except:
            print "Could not parse contig file: %s %s" % (contigs_file,sys.exc_info()[0])
            raise

    def parseBinsFile(self, bins_file):
        """Extract contig Id to bins assignments
        
        bfh should be a tab sep'd bins file which looks like:
        
        # header
        cid1 -> bid
        cid2 -> bid
        ...
        """
        tmp_bids = {}
        try:
            with open(bins_file) as bin_fh:
                for line in bin_fh:
                    line = line.rstrip()
                    if len(line) > 0:
                        if line[0] != '#':
                            parts = line.split('\t')
                            self.binAssignments[parts[0]] = parts[1]
                            tmp_bids[parts[1]] = True
        except:
             print "Could not parse bins file: %s %s" % (bins_file,sys.exc_info()[0])
             raise

        # make sure that all contigs are assigned to a bin
        if len(self.binAssignments.keys()) != len(self.headers):
            raise BinLengthError("bin file does not match headers",
                                 "B: %d != H: %d " % (len(self.binAssignments.keys()),
                                                      len(self.headers)
                                                      )
                                 )
        # we'll need a list of binIDs later
        self.binIDs = sorted(tmp_bids.keys())

    def printFpkc(self, fileStream):
        """print the results of our labour"""
        fileStream.write("\t".join(['cid',
                                    "\t".join(self.bamNames)
                                    ])+"\n")
        for cid in self.headers:
            fileStream.write("\t".join([cid,
                                        "\t".join(["%0.4f" % i for i in self.fpkc[cid]])
                                        ]
                                       )+"\n"
                             )

    def printMfpkc(self, fileStream):
        """break fpkc results into bin specific units and print"""
        fileStream.write("\t".join(['bid',
                                    "\t".join(self.bamNames)
                                    ])+"\n")
        # first sort the cid_fpkc's into bin specific groups
        for cid in self.headers:
            for bam_counter in range(self.numBams):
                self.mfpkc[self.binAssignments[cid]][bam_counter].append(self.fpkc[cid][bam_counter])
        
        # take the median on the fly and print
        for bid in self.binIDs:
            #for bam_counter in range(self.numBams):
            fileStream.write("\t".join([bid,
                                        "\t".join(["%0.4f" % np.median(i) for i in self.mfpkc[bid]])
                                        ]
                                       )+"\n"
                             )
    
###############################################################################
###############################################################################
###############################################################################
###############################################################################

class BamParser:
    def __init__(self):
        self.bamFile = None

    def openBam(self, bf):
        """Open the bamfile and set the file handle"""
        try:
            self.bamFile = pysam.Samfile(bf, 'rb')
        except:
            raise CouldNotOpenMappingException("Unable to open mapping file file: %s -- did you supply a SAM file?" % bf)        
    
    def closeBam(self):
        """close the open bamfile"""
        if self.bamFile is not None:
            self.bamFile.close()
        
    def getFpkc(self, headers):
        """Parse a bam file (handle) """
        if self.bamFile is None:
            raise MappingNotOpenException("No file handle to work on!")
        
        # get some storage
        fpkc = {}
        for cid in headers:
            fpkc[cid] = 0.0
        
        for reference, length in zip(self.bamFile.references, self.bamFile.lengths):
            fc = FragCounter()
            self.bamFile.fetch(reference, 0, length, callback = fc )
            fpkc[reference] = (float(fc.count) * 1000 )/ float(length)
        
        return fpkc

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class FragCounter:
    """AUX: Call back for counting aligned reads
    Used in conjunction with pysam.fetch
    """
    def __init__(self):
        self.count = 0
        
    def __call__(self, alignedRead):
        if not alignedRead.is_unmapped:
            self.count += 1

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
            name, seqs, last = last[1:].split()[0], [], None
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
    def getHeaders(self, contigFile):
        """All we want id the headers"""
        headers = []
        for cid,seq,qual in self.readfq(contigFile):
            headers.append(cid)
        return sorted(headers)
       
###############################################################################
###############################################################################
###############################################################################
###############################################################################
