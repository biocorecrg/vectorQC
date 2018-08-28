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
import textwrap

# Define options
def options_arg():
    usage = "usage: %prog "
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input', help='Input sequence name', dest="input")
    parser.add_option('-o', '--output', help='Output prefix file', dest="outfile" )
    parser.add_option('-n', '--seqname', help='Sequence name', dest="seqname", default="sequence")
    parser.add_option('-s', '--stretch', help='Stretch to check', dest="stretch", default=127)
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.input:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.input
outfile = opts.outfile
stretch = opts.stretch
seqname = opts.seqname

# read input and prepare output
fahandle	= open(fafile, 'rb')
outhandle	= open(outfile, 'w+')

num		 = 0
seqout   = ""
header   = ">" + seqname
# read fasta file for getting the size
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"): # header
			num += 1
		else:
			seqout += line.rstrip() 

if (num > 1):
	header = header + "_warning_" + str(num) + "_scaffolds," + str(len(seqout)) + "\n"
	seqout = header + textwrap.fill(seqout, width=60)
	print "WARNING FOUND " + str(num) + " SCAFFOLDS in " + seqname + "\n"
else:
	seqout = header + ","+ str(len(seqout)-127) + "\n" + textwrap.fill(seqout[:-127], width=60)
	
outhandle.write(seqout)			
outhandle.close()		

	




	


