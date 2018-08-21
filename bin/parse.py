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
    parser.add_option('-b', '--blastinput', help='Input m 6 blast', dest="binfile" )
    parser.add_option('-r', '--restrinput', help='Input Emboss restrict file', dest="rinfile" )
    parser.add_option('-f', '--fasta', help='Input fasta file', dest="fafile" )
    parser.add_option('-o', '--output', help='Output parsed file', dest="outfile" )
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.rinfile and opts.binfile:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.fafile
binfile = opts.binfile
rinfile = opts.rinfile
outfile = opts.outfile

minidentity = 95
maxtolerance = 5

# color code
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
inhandle	= open(binfile, 'rb')
rihandle	= open(rinfile, 'rb')

seqsize = 0
# read fasta file for getting the size
with fahandle as fa:
	for line in fa:
		if (line[:1]== ">"):
			nameseq = line[1:].rstrip()
		else:
			seqsize += len(line.rstrip())

outstring = "#" + nameseq + "\n%" + str(seqsize) + "\n" + "!strand	slot	start	stop	opacity	thickness	type	label\n"

coords = defaultdict(dict)
# read blast tabular output file
with inhandle as fi:
	for line in fi:
		fields		= line.rstrip().split("\t") 
		feature		= fields[1]
		identity	= float(fields[2])
		qlength		= int(fields[3])
		qstart		= int(fields[6])
		qend		= int(fields[7])
		sstart		= int(fields[8])
		send		= int(fields[9])
		
		featname = feature[feature.find("{")+1:feature.find("}")]
		feattype = feature[feature.find("[")+1:feature.find("]")]
		featsize = int(feature[feature.find(",")+1:len(feature)])

		if (sstart-send<0):	#plus strand
			strand = "forward"
		else:
			strand = "reverse"
		
		if (featsize<=50):
			minsize = int(round(featsize/10))
		else:
			minsize = maxtolerance
		
		if (featsize - qlength <= minsize and identity>=minidentity): 
			outstring = outstring  + strand + "\t1\t" + str(qstart) + "\t" + str(qend) + "\t1\t1\t" + trans_code[feattype] + "\t" + featname + "\n"

		if (qstart <= maxtolerance and identity>=minidentity): # special case circular genome!!
			if (featname not in coords):
				coords[featname]["5p"] = seqsize
				coords[featname]["3p"] = 0
				coords[featname]["string5"] = ""
				coords[featname]["string3"] = ""
				coords[featname]["minsize"] = featsize - minsize
			if (coords[featname]["3p"]< qend):
				coords[featname]["3p"] = qend
				coords[featname]["string3"] = strand + "\t1\t" + str(qstart) + "\t" + str(qend) + "\t1\t1\t" + trans_code[feattype] + "\t" + featname + "\n"
			
		if (qend >= seqsize - maxtolerance and identity>=minidentity):
			if (featname not in coords):
				coords[featname]["5p"] = seqsize
				coords[featname]["3p"] = 0
				coords[featname]["string5"] = ""
				coords[featname]["string3"] = ""
				coords[featname]["minsize"] = featsize - minsize
	
			if (coords[featname]["5p"]> qstart):
				coords[featname]["5p"] = qstart
				coords[featname]["string5"] = strand + "\t1\t" + str(qstart) + "\t" + str(qend) + "\t1\t1\t" + trans_code[feattype] + "\t" + featname + "\n"


for featname_break in coords:
	size = coords[featname_break]["3p"] + seqsize - coords[featname_break]["5p"]
	if (size>=coords[featname_break]["minsize"]):
			outstring = outstring  + coords[featname_break]["string5"] + coords[featname_break]["string3"]
		
with rihandle as fi:
	for line in fi:
		if (line[0] != "#"):
			line	= line.rstrip()
			fields  = re.split('\s+', line)
			if (len(fields)>1 and fields[1]!="Start"):
				if (fields[3] == "-"):
					strand = "reverse"
				else:
					strand = "forward"	
				outstring = outstring + strand + "\t2\t" + fields[1] + "\t" + fields[2] + "\t1\t1\trestriction_site\t" + fields[4] + "\n"

outhandle.write(outstring)
outhandle.close()
		
		
	


