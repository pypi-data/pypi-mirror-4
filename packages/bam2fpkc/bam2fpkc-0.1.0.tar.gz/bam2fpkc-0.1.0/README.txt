.
.                                                                             
. 888                              .d8888b.  .d888          888               
. 888                             d88P  Y88 d88P"           888               
. 888                                    88 888             888               
. 88888b.   8888b.  88888b.d88b.       .d88 888888 88888b.  888  888  .d8888b  
. 888 "88b     "88b 888 "888 "88b  .od888P" 888    888 "88b 888 .88P d88P"    
. 888  888 .d888888 888  888  888 d88P"     888    888  888 888888K  888      
. 888 d88P 888  888 888  888  888 888"      888    888 d88P 888 "88b Y88b.    
. 88888P"  "Y888888 888  888  888 88888888  888    88888P"  888  888  "Y8888P 
.                                                  888                        
.                                                  888                        
.                                                  888                        
.                                                                             

Overview
=========

This script works out how many reads are mapping to each contig OR if you ask it
nicely, it will find the median number of reads mapping to all contigs in your bins.

The number of fragments mapping to any contig is normalised for contig length to give
the average number of fragments mapping per 1000 bases of contig or.. fpkc

Installation
=========

Should be as simple as

    pip install bam2fpkc

Data preparation and running bam2fpkc
=========

You'll always need a set of contigs and a corresponding set of sorted indexed bam files.
Then you just need to decide if you want to get fpkc values for a set of contigs or a 
the median fpkc for all contigs in your bins.

Contigs:

    Options are in flux, use:
        
        bam2fpkc contig -h
        
    for more info...

Bins:

    For this you'll need a 'bins file'. This is a TAB separated file of the form
    
        cid -> bid
    
    Currently, the cid MUST exactly match the contig headers in the fasta file AND
    all cids must be accounted for. IE. unbinned contigs should be assigned to bin 0
    or some other sensible assignment.
    
    Otherwise use:
    
        bam2fpkc bin -h
        
    for more info...

Licence and referencing
=========

Project home page, info on the source tree, documentation, issues and how to contribute, see http://github.com/minillinim/bam2fpkc

This software is currently unpublished. Please contact me at m_dot_imelfort_at_uq_dot_edu_dot_au for more information about referencing this software.

Copyright © 2013 Michael Imelfort. See LICENSE.txt for further details.
