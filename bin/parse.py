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

def getFeatureStrand(feturetype, strand):
	featurestrand = feturetype
	if (feturetype == "arrow" and strand == "forward"):
		featurestrand = "clockwise-arrow"
	if (feturetype == "arrow" and strand == "reverse"):
		featurestrand = "counterclockwise-arrow"
	return featurestrand
	
opts = options_arg()
fafile = opts.fafile
binfile = opts.binfile
rinfile = opts.rinfile
outfile = opts.outfile
seqname = opts.seqname

minidentity = 95
maxtolerance = 5

# feat info code
feat_info = defaultdict(dict)
feat_info['HYB'] = {'color' : 'red', 'style' : "arc", "label": "Hyper activation domain", "gb": "misc_feature"} # Hyper activation domain 
feat_info['LOC'] = {'color' : 'gray', 'style' : "arc", "label": "Locus", "gb": "misc_feature"} # Locus
feat_info['ORI'] = {'color' : 'black', 'style' : "arc", "label": "Origin of replication", "gb": "rep_origin"} # Origin of replication
feat_info['OTH'] = {'color' : 'gray', 'style' : "arc", "label": "Other", "gb": "misc_feature"}
feat_info['PRO'] = {'color' : 'green', 'style' : "arrow", "label": "Promoter", "gb": "promoter"} # Promoter
feat_info['REG'] = {'color' : 'lime', 'style' : "arc", "label": "Regulatory sequence", "gb": "misc_feature"}
feat_info['REP'] = {'color' : 'yellow', 'style' : "arrow", "label": "Reporter gene", "gb": "Marker"} 
feat_info['INS'] = {'color' : 'red', 'style' : "arrow", "label": "Inserted gene", "gb": "CDS"} # Insert 
feat_info['SEL'] = {'color' : 'orange', 'style' : "arrow", "label": "Gene for selection", "gb": "CDS"} # gene for selection TAG
feat_info['TAG'] = {'color' : 'gray', 'style' : "arrow", "label": "affinity TAG", "gb": "misc_feature"} # Affinity TAG
feat_info['TER'] = {'color' : 'maroon', 'style' : "arc", "label": "Terminator", "gb": "terminator"} # Terminator 
feat_info['RESTR'] = {'color' : 'blue', 'style' : "arc", "label": "Unique restriction site", "gb": "misc_binding"} # Restriction site

# read input and prepare output
fahandle	= open(fafile, 'rb')
xmlhandle	= open(outfile + ".xml", 'w+')
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
	
outXMLstring = '<?xml version="1.0" encoding="ISO-8859-1"?>' + "\n"
outXMLstring += '<cgview backboneRadius="160" sequenceLength="' + str(seqsize) + '">' + "\n"

gbkstring = "LOCUS\t" + seqname + "\t" + str(seqsize) + " bp\tDNA\tcircular\nFEATURES\tLocation/Qualifiers\n"

coords = defaultdict(dict)
inserts = []
xmlarr = defaultdict(dict)
xmlarrOrig = defaultdict(dict)

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

		feat = {"featname": featname, "featsize": featsize, "feattype": feattype, "start":qstart, "end":qend, "strand":strand}
			
		if (featsize<=50):
			minsize = int(round(featsize/10))
		else:
			minsize = maxtolerance
		
		if (featsize - qlength <= minsize and identity>=minidentity): 
			if feattype not in xmlarr:
				xmlarr[feattype] = []
				xmlarr[feattype].append( feat )
			else:
				xmlarr[feattype].append( feat )
				
		if (qstart <= maxtolerance and identity>=minidentity): # special case circular genome!!
			if ("A") not in xmlarrOrig[featname].keys():
				xmlarrOrig[featname]["A"] = feat
			elif(xmlarrOrig[featname]["A"]['end'] - xmlarrOrig[featname]["A"]['start'] < feat['end'] - feat['start']):
				xmlarrOrig[featname]["A"] = feat
										
		if (qend >= seqsize - maxtolerance and identity>=minidentity):
  			# Override in case the next match is longer than the previous and the subject matched is the same       
			if ("B") not in xmlarrOrig[featname].keys():
				xmlarrOrig[featname]["B"] = feat
			elif(xmlarrOrig[featname]["B"]['end'] - xmlarrOrig[featname]["B"]['start'] < feat['end'] - feat['start']):
				xmlarrOrig[featname]["B"] = feat


for featname_broken in xmlarrOrig:
	sizeA = 0
	sizeB = 0
	start = 0
	end = seqsize
	if ("A") in xmlarrOrig[featname_broken].keys():
		featsize = xmlarrOrig[featname_broken]["A"]["featsize"]
		feattype = xmlarrOrig[featname_broken]["A"]["feattype"]
		sizeA = xmlarrOrig[featname_broken]["A"]['end'] - xmlarrOrig[featname_broken]["A"]['start']

		# Start is bigger than end when crossing the origin
		start = xmlarrOrig[featname_broken]["A"]['start']
		end = xmlarrOrig[featname_broken]["A"]['end']
		
	if ("B") in xmlarrOrig[featname_broken].keys():
		featsize = xmlarrOrig[featname_broken]["B"]["featsize"]
		feattype = xmlarrOrig[featname_broken]["B"]["feattype"]
		sizeB = xmlarrOrig[featname_broken]["B"]['end'] - xmlarrOrig[featname_broken]["B"]['start']
		
		start = max(start, xmlarrOrig[featname_broken]["B"]['start'])
		end = min(end, xmlarrOrig[featname_broken]["B"]['end'])
	size = sizeA+sizeB
	feat = {"featname": featname_broken, "feattype": feattype, "start":start, "end":end, "strand":strand}
	if (featsize<=50):
		minsize = int(round(size/10))
	else:
		minsize = maxtolerance
	if (featsize - size <= minsize): 
		if feattype not in xmlarr:
			xmlarr[feattype] = []
			xmlarr[feattype].append( feat )
		else:
			xmlarr[feattype].append( feat )
		
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
				feat = 	{"featname": fields[4], "feattype": "RESTR", "start":str(start), "end": str(end), "strand": strand}
				if "RESTR" not in xmlarr:
					xmlarr["RESTR"] = []
					xmlarr["RESTR"].append( feat )
				else:
					xmlarr["RESTR"].append( feat )

#Write XML files and GeneBank file
for feature_type, features in xmlarr.iteritems():
	featcolor = feat_info[feature_type]['color']
	outXMLstring += " <featureSlot strand=\"direct\">" + "\n"
	for featdata in features:
		start = featdata['start']
		end = featdata['end']
		featname = featdata['featname']
		featstrand = getFeatureStrand(feat_info[feature_type]['style'], featdata['strand'])
		outXMLstring += "  <feature color=\""+ featcolor +"\" decoration=\"" + featstrand + "\" label=\"" + featname + "\">" + "\n"
		outXMLstring += "    <featureRange start=\"" + str(start) + "\" stop=\"" + str(end) + "\" />" + "\n"
		outXMLstring += "    </feature>" + "\n"

		if (featdata['strand'] == "reverse"):
			gbcoords = "complement(" + str(start) + ".." + str(end) + ")"
		else:
			gbcoords = str(start) + ".." + str(end)
		gbkstring += feat_info[feature_type]['gb'] + "\t" + gbcoords + "\n" + "\t\t/label=" + featname + "\n"
		
	outXMLstring += " </featureSlot>" + "\n"
outXMLstring += "<legend position=\"upper-right\">" + "\n"

for feature_type, features in xmlarr.iteritems():
	featcolor = feat_info[feature_type]['color']
	featlab = feat_info[feature_type]['label']
	outXMLstring += "  <legendItem text=\"" + featlab + "\" drawSwatch=\"true\" swatchColor=\"" + featcolor + "\" />" + "\n"
	
outXMLstring += "</legend>" + "\n"
outXMLstring += '</cgview>' + "\n"


gbkstring += "ORIGIN\n" + gbseq + "\n"



xmlhandle.write(outXMLstring)
xmlhandle.close()

outhandlegb.write(gbkstring)
outhandlegb.close()

if len(inserts)==0:
	 inserts.append("-")
outhandlog.write(",".join(inserts))
outhandlog.close()


