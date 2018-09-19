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
    parser.add_option('-d', '--outerd', help='Outer distance', dest="outerd", default=600)
    parser.add_option('-e', '--stdev', help='Outer distance standard error', dest="stdev", default=100)
    parser.add_option('-s', '--readsize', help='Read size', dest="readsize", default=300)
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.input:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.input
outfile = opts.outfile
xfold = int(opts.xfold)
readsize = int(opts.readsize)
stdev = int(opts.stdev)
outerd = int(opts.outerd)

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

os.system("wgsim -d " + str(outerd) + " -s " + str(stdev) + " -N " + str(int(size*xfold/readsize)) + " -1 " + str(readsize) + " -2 " + str(readsize) + " " + outfile + " " + outfile + "_1.fq " + outfile + "_2.fq; rm " + outfile)	
	




	


