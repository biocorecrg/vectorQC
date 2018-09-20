#!/usr/bin/env python
# This code uses the input fasta file, the results of blast in tabular format, 
# the results of the restric program and it generates both a tabular file for being displayed in CGVIEW 
# and a genbank file to be used in other programs. It also allows the mapping of features that overlap 
# with the sequence break in the circular DNA
# for both blast and restrict programs.


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
    parser.add_option('-n', '--seqname', help='Input sequence name', dest="seqname", default="seqname")
    parser.add_option('-b', '--blastinput', help='Input m 6 blast', dest="binfile" )
    parser.add_option('-r', '--restrinput', help='Input Emboss restrict file', dest="rinfile" )
    parser.add_option('-f', '--fasta', help='Input fasta file', dest="fafile" )
    parser.add_option('-o', '--output', help='Output prefix file', dest="outfile" )
    (opts,args) = parser.parse_args()
    if opts.outfile and opts.rinfile and opts.binfile:pass
    else: parser.print_help()
    return (opts)

opts = options_arg()
fafile = opts.fafile
binfile = opts.binfile
rinfile = opts.rinfile
outfile = opts.outfile
seqname = opts.seqname

minidentity = 95
maxtolerance = 5

# trans code
trans_code = {'HYB': 'score',
'LOC': 'score',
'ORI': 'origin_of_replication',
'OTH': 'score',
'PRO': 'promoter',
'REG': 'regulatory_sequence',
'REP': 'gene',
'INS': 'gene',
'SEL': 'gene',
'TAG': 'score',
'TER': 'terminator'}

# gb trans code
gb_trans_code = {'HYB': 'misc_feature',
'LOC': 'misc_feature',
'ORI': 'rep_origin',
'OTH': 'misc_feature',
'PRO': 'promoter',
'REG': 'misc_feature',
'INS': 'CDS',
'REP': 'CDS',
'SEL': 'CDS',
'TAG': 'misc_feature',
'TER': 'terminator'}

# read input and prepare output
fahandle	= open(fafile, 'rb')
outhandle	= open(outfile + ".tab", 'w+')
outhandlegb	= open(outfile + ".gbk", 'w+')
outhandlog	= open(outfile + ".log", 'w+')
inhandle	= open(binfile, 'rb')
rihandle	= open(rinfile, 'rb')

seqsize = 0
flatseq = ""
gbseq   = ""
# read fasta file for getting the size
with fahandle as fa:
	for line in fa:
		if (line[:1]!= ">"):
			seqsize += len(line.rstrip())
			flatseq = flatseq + line.rstrip()

chunksize  = 10
chunkstart = 0
gbarr   = []

while chunkstart <= seqsize:
	if (len(gbarr)==6):
		gbseq = gbseq + str(chunkstart+1-60) + "\t" + " ".join(gbarr) + "\n"
		gbarr   = []
	else :
		gbarr.append(flatseq[chunkstart:chunkstart+chunksize])
		chunkstart = chunkstart + chunksize
	
if (len(gbarr)>0):
	gbseq = gbseq + str(chunkstart+1-60) + "\t" + " ".join(gbarr) + "\n"

gbseq = gbseq + "//"
	
outstring = "#" + seqname + "\n%" + str(seqsize) + "\n" + "!strand	slot	start	stop	opacity	thickness	type	label\n"
gbkstring = "LOCUS\t" + seqname + "\t" + str(seqsize) + " bp\tDNA\tcircular\nFEATURES\tLocation/Qualifiers\n"

coords = defaultdict(dict)
inserts = []
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
			gbcoords =  str(qstart) + ".." + str(qend)
		else:
			strand = "reverse"
			gbcoords =  "complement(" + str(qstart) + ".." + str(qend) + ")"

		rowsrting   = strand + "\t1\t" + str(qstart) + "\t" + str(qend) + "\t1\t1\t" + trans_code[feattype] + "\t" + featname + "-" + feattype + "\n"
		rowgbstring = "\t" +  gb_trans_code[feattype] + "\t" + gbcoords + "\n" + "\t\t/label=" + featname + "\n"			
					
		if (featsize<=50):
			minsize = int(round(featsize/10))
		else:
			minsize = maxtolerance
		
		if (featsize - qlength <= minsize and identity>=minidentity): 
			outstring = outstring + rowsrting
			gbkstring = outstring + rowgbstring
			if (feattype == "INS"): 
				inserts.append(featname)
				
		if (qstart <= maxtolerance and identity>=minidentity): # special case circular genome!!
			if (featname not in coords): # inizialize
				coords[featname]["feattype"]     	= feattype
				coords[featname]["sizeBefore0"]     = 0
				coords[featname]["sizeAfter0"]      = qend
				coords[featname]["stringAfter0"]    = rowsrting
				coords[featname]["stringBefore0"]   = ""
				coords[featname]["stringGBAfter0"]  = rowgbstring
				coords[featname]["stringGBBefore0"] = ""
			# Override in case the next match is longer than the previous and the subject matched is the same
			if (coords[featname]["sizeAfter0"]< qend):
				coords[featname]["sizeAfter0"]     = qend
				coords[featname]["stringAfter0"]   = rowsrting
				coords[featname]["stringGBAfter0"] = rowgbstring
			
		if (qend >= seqsize - maxtolerance and identity>=minidentity):
			if (featname not in coords): # inizialize
				coords[featname]["feattype"]     	= feattype
				coords[featname]["sizeBefore0"]    = seqsize - qstart
				coords[featname]["sizeAfter0"]     = 0
				coords[featname]["stringAfter0"]   = ""
				coords[featname]["stringBefore0"]  = rowsrting
				coords[featname]["stringGBAfter0"] = rowgbstring
				coords[featname]["stringGBBefore0"] = ""
			# Override in case the next match is longer than the previous and the subject matched is the same	
			if (coords[featname]["sizeBefore0"] < seqsize - qstart):
				coords[featname]["sizeBefore0"]    = seqsize - qstart
				coords[featname]["stringBefore0"]  = rowsrting
				coords[featname]["stringGBBefore0"] = rowgbstring


for featname_break in coords:
	size = coords[featname_break]["sizeBefore0"] + coords[featname_break]["sizeAfter0"]
	if (size<=50):
		minsize = int(round(size/10))
	else:
		minsize = maxtolerance

	if (size>=minsize):	
		outstring = outstring  + coords[featname_break]["stringBefore0"] + coords[featname_break]["stringAfter0"]
		gbkstring = gbkstring  + coords[featname_break]["stringGBBefore0"] + coords[featname_break]["stringGBAfter0"]
		if (coords[featname_break]["feattype"] == "INS"):
			inserts.append(featname)

gbkstring = gbkstring + "ORIGIN\n" + gbseq + "\n"

#parsing Restrict file from EMBOSS. Extracts the coordinates
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
				start = int(fields[1])
				end = int(fields[2]) 
				if (end>seqsize):
					end = end - seqsize
				outstring = outstring + strand + "\t2\t" + str(start) + "\t" + str(end) + "\t1\t1\tunique_restriction_site\t" + fields[4] + "\n"

outhandle.write(outstring)
outhandle.close()

outhandlegb.write(gbkstring)
outhandlegb.close()

if len(inserts)==0:
	 inserts.append("-")
outhandlog.write(", ".join(inserts))
outhandlog.close()
