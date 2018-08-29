#!/usr/bin/env nextflow

// Copyright (c) 2018, Centre for Genomic Regulation (CRG) and the authors.



/*
===========================================================
vectorQC pipeline for Bioinformatics Core @ CRG

 @authors
 Luca Cozzuto <lucacozzuto@gmail.com>
=========================================================== 
*/

version = '0.1'

/*
* Input parameters: read pairs, db fasta file, 
*/

params.help            = false
params.resume          = false


log.info """
Biocore@CRG VectorQC - N F  ~  version ${version}

╔╗ ┬┌─┐┌─┐┌─┐┬─┐┌─┐╔═╗╦═╗╔═╗  ┬  ┬┌─┐┌─┐┌┬┐┌─┐┬─┐╔═╗ ╔═╗
╠╩╗││ ││  │ │├┬┘├┤ ║  ╠╦╝║ ╦  └┐┌┘├┤ │   │ │ │├┬┘║═╬╗║  
╚═╝┴└─┘└─┘└─┘┴└─└─┘╚═╝╩╚═╚═╝   └┘ └─┘└─┘ ┴ └─┘┴└─╚═╝╚╚═╝
                                                                                       
====================================================
seqs                                            : ${params.seqs}
email for notification                          : ${params.email}
output (output folder)                          : ${params.output}
fold                                            : ${params.fold}
outerd (outer distance)                         : ${params.outerd}
stdev (outer distance standard error)           : ${params.stdev}
inserts                                         : ${params.inserts}
size                                            : ${params.size}
"""

if (params.help) {
    log.info 'This is the Biocore\'s vectorQC pipeline'
    log.info '\n'
    exit 1
}
if (params.resume) exit 1, "Are you making the classical --resume typo? Be careful!!!! ;)"  

Channel
    .fromFilePairs( params.seqs, size: 1)                                     
    .ifEmpty { error "Cannot find any reads matching: ${params.seqs}" }
    .set { sequences}    



/*
 * Run simulate NGS reads on singular vectors
 */
process simulateVectors {
	tag { sequence }
    publishDir params.output, mode: 'copy'

    input:
    set id, file(sequence) from sequences

    output:
   	file("*.fq") 

    script:
	"""
		simulateCircular.py -i ${sequence} -o ${id} -x ${params.fold} -d ${params.outerd} -e ${params.stdev} -s ${params.size}
	"""
}


