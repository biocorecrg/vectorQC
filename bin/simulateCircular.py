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

# Define options
def options_arg():
    usage = "usage: %prog "
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input', help='Input sequence name', dest="input")
    parser.add_option('-o', '--output', help='Output prefix file', dest="outfile" )
    parser.add_option('-x', '--xfold', help='Fold Coverage', dest="xfold", default=100)
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.input:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.input
outfile = opts.outfile
xfold = int(opts.xfold)

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

# read fasta file for extending the sequence 
sequence = ""
fahandle	= open(fafile, 'rb')
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			seqname  = line[1:].rstrip()
		else:
			sequence += line

seqout = ">" + seqname + "\n"
for x in range(0, xfold):
	seqout += sequence

outhandle.write(seqout)			
outhandle.close()		

os.system("art_illumina -ss MSv3 -na -i " + outfile + " -p -l 250 -f 1 -m 400 -s 200 -o " + outfile + "; rm " + outfile)	
	




	


