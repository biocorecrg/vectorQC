#!/usr/bin/env python

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
from collections import defaultdict

# Define options
def options_arg():
    usage = "usage: %prog "
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input', help='Input sequence name', dest="input")
    parser.add_option('-o', '--output', help='Output prefix file', dest="outfile" )
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.input:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.input
outfile = opts.outfile

# trans code
trans_code = {'HYB': 'score',
'LOC': 'score',
'ORI': 'origin_of_replication',
'OTH': 'score',
'PRO': 'promoter',
'REG': 'regulatory_sequence',
'REP': 'gene',
'SEL': 'gene',
'TAG': 'score',
'TER': 'terminator'}

# read input and prepare output
fahandle	= open(fafile, 'rb')
outhandle	= open(outfile, 'w+')

sizes = []
size = 0
# read fasta file for getting the size
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			sizes.append(size)
			size = 0
		else:
			size = size + len(line.rstrip())

sizes.append(size)
del sizes[0]

# read fasta file for changing the header
num = 0
fahandle	= open(fafile, 'rb')
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			seqname  = line[1:].rstrip()
			pseqname = ">" + seqname + "[INS]" + "{" + seqname + "}," + str(sizes[num]) + " bases\n"
			num = num + 1
			outhandle.write(pseqname)
		else:
			outhandle.write(line)			

outhandle.close()			
	




	


