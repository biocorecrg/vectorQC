#!/usr/bin/env python
# This code parses the assembly generated by Spades and, in case is just one contig,
# it removes the extra sequence due to the circularity of the genome. 
# It also creates a log file useful for the final report.

__author__ = 'luca.cozzuto@crg.eu'
# -*- coding utf-8 -*-

#MODULES
import sys
import re
import optparse
import gzip
import pprint
import uuid
import os
import textwrap

# Define options
def options_arg():
    usage = "usage: %prog "
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input', help='Input sequence name', dest="input")
    parser.add_option('-o', '--output', help='Output prefix file', dest="outfile" )
    parser.add_option('-n', '--seqname', help='Sequence name', dest="seqname", default="sequence")
    parser.add_option('-k', '--kmer', help='Kmer to remove', dest="kmer", default=127)
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.input:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.input
outfile = opts.outfile
stretch = opts.kmer
seqname = opts.seqname

# read input and prepare output
fahandle	= open(fafile, 'rb')
outhandle	= open(outfile, 'w+')
outlhandle	= open(outfile + ".log", 'w+')

num		 = 0
seqout   = ""
fastaout = ""
header   = ">" + seqname
log 	 = ""
fasta_seqs = {}
totlen = 0
weightcov = 0 

# read fasta file for filtering low covered reads
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			header = line[1:].rstrip()
			vals = header.split("_")
			length = int(vals[3])
			cov = float(vals[5])
			totlen += length
			weightcov += length*cov

meancov = weightcov/totlen
fahandle	= open(fafile, 'rb')
# read fasta file for filtering low covered reads
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			header = line[1:].rstrip()
			vals = header.split("_")
			cov = float(vals[5])
			if (cov>=(meancov*0.5) and cov<=(meancov*1.5)): 
				fasta_seqs[header] = ""
		elif (header in fasta_seqs) :
			fasta_seqs[header] += line.rstrip() 

num = len(fasta_seqs)
if (num > 1): 
	print "WARNING FOUND " + str(num) + " SCAFFOLDS in " + seqname + "\n"
	for seqnames in fasta_seqs:
		seqout += fasta_seqs[seqnames]
else:
	for seqnames in fasta_seqs:
		seqout += fasta_seqs[seqnames]	
		seqout = seqout[:-(int(stretch))]
	
seqsize = str(len(seqout))
seqout = ">" + seqname + "," + seqsize + "\n" + textwrap.fill(seqout, width=60)
	
outhandle.write(seqout)			
outhandle.close()

outlhandle.write(seqname + "\t" + str(num) + "\t" + seqsize + "\n")	
outlhandle.close()	


