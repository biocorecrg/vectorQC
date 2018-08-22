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
reads                       : ${params.reads}
email for notification      : ${params.email}
output (output folder)      : ${params.output}
commonenz (common enzymes)  : ${params.commonenz}
features 					: ${params.features}
"""


if (params.help) {
    log.info 'This is the Biocore\'s vectorQC pipeline'
    log.info '\n'
    exit 1
}
if (params.resume) exit 1, "Are you making the classical --resume typo? Be careful!!!! ;)"

featuresdb = file(params.features)
if( !featuresdb.exists() ) exit 1, "Missing feature file: ${params.features}"

commonenz = file(params.commonenz)
if( !commonenz.exists() ) exit 1, "Missing common enzyme file: ${params.commonenz}"

/*
// Setting the reference genome file and the annotation file (validation)

peakconfig = file(params.peakconfig)
if( !peakconfig.exists() ) exit 1, "Missing MACS2 config: '$peakconfig'. Specify path with --peakconfig"

genome_file = file(params.genome)
annotation_file = file(params.annotation)
multiconfig = file(params.multiconfig)
bigConfFolder = file("$baseDir/bigConf")


if( !genome_file.exists() ) exit 1, "Missing genome file: ${genome_file}"
if( !annotation_file.exists() ) exit 1, "Missing annotation file: ${annotation_file}"

outputfolder    = "${params.output}"
*/

outputQC		= "${params.output}/QC"
outputAssembly  = "${params.output}/Assembly"
outputBlast  	= "${params.output}/Blast"
outputRE  		= "${params.output}/REsites"
outputPlot  	= "${params.output}/Plots"
outputGBK		= "${params.output}/GenBank"

/*
outputMultiQC		= "${params.output}/multiQC"
outputMapping	= "${params.output}/Alignments"
outputIndex		= "${params.output}/Index"
peakCalling		= "${params.output}/Peaks"
outputProfiles  = "${params.output}/Profiles"
outputAnnotation  = "${params.output}/Annotation"
outputReport    = file("${outputMultiQC}/multiqc_report.html")
UCSCgenomeID	= "${params.UCSCgenomeID}"
tooldb = file(params.tooldb)

if( UCSCgenomeID != "" ) {
	rootProfiles = outputProfiles
	outputProfiles = "${outputProfiles}/${params.UCSCgenomeID}"
}


// move old multiQCreport in case it already exists 
if( outputReport.exists() ) {
  log.info "Moving old report to multiqc_report.html multiqc_report.html.old"
  outputReport.moveTo("${outputMultiQC}/multiqc_report.html.old")
}
*/

// Create channels for sequences data
Channel
    .fromFilePairs( params.reads)                                       
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}" }
    .set { read_files_for_trimming}    

Channel
    .fromPath( params.reads )                                             
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}" }
    .set {reads_for_fastqc} 


/*
 * Run FastQC on raw data
 */
process raw_fastqc {
	tag { read }
    publishDir outputQC, mode: 'copy'

    input:
    file(read) from reads_for_fastqc

    output:
   	file("*_fastqc.*") into raw_fastqc_files

    script:
    def qc = new QualityChecker(input:read, cpus:task.cpus)
	qc.fastqc()
}

/*
 * Trim reads with skewer for removing the RNA primer at 3p
 */ 
 
process trimReads {
	tag { pair_id }
		
   	input:
	set pair_id, file(reads) from (read_files_for_trimming)

    output:
   	set pair_id, file("${pair_id}-trimmed*.fastq.gz") into filtered_reads_for_assembly
   	file("*trimmed*.fastq.gz") into filtered_read_for_QC
	file("*trimmed.log") into logTrimming_for_QC

    script:	
    def trimmer = new Trimmer(reads:reads, id:pair_id, min_read_size:1, cpus:task.cpus)
	trimmer.trimWithSkewer()
}

/*
 * FastQC
 */ 
process trimmedQC {
	tag { filtered_read }

 	 afterScript 'mv *_fastqc.zip `basename *_fastqc.zip _fastqc.zip`_filt_fastqc.zip'

   	 input:
     file(filtered_read) from filtered_read_for_QC.flatten()

     output:
   	 file("*_filt_fastqc.zip") into fastqc_files

    script:
    def qc = new QualityChecker(input:filtered_read, cpus:task.cpus)
	qc.fastqc()
}

/*
 * Run assembly of input sequence
 */
 
process assemble {
	tag { pair_id }
    publishDir outputAssembly, mode: 'copy'

    label 'big_mem_cpus'

    input:
    set pair_id, file(readsA), file(readsB) from  filtered_reads_for_assembly.flatten().collate( 3 )

    output:
   	set pair_id, file("${pair_id}_assembly.fa") into scaffold_file_for_blast, scaffold_file_for_re, scaffold_file_for_parsing

    script:
	"""
	   spades.py --careful --pe1-1 ${readsA} --pe1-2 ${readsB} -o ${pair_id} -t ${task.cpus} -m ${task.memory.giga} 
	   cp ${pair_id}/scaffolds.fasta ${pair_id}_assembly.fa
	"""
}

/*
 * Make blast db
 */
 
process makeblastdb {
	tag { features_file }
	
    input:
    file(features_file) from featuresdb

    output:
   	set "blast_db.fasta", file("blast_db.fasta*") into blastdb_files

    script:
    def aligner = new NGSaligner(reference_file:features_file, index:"blast_db.fasta", dbtype:"nucl")
	aligner.doIndexing("blast")
}

/*
 * Run blast
 */
 
process runBlast {
	tag { pair_id }
	publishDir outputBlast

    label 'big_mem_cpus'

    input:
    set blastname, file(blastdbs) from blastdb_files
    set pair_id, file(scaffold_file) from scaffold_file_for_blast

    output:
    set pair_id, file("${pair_id}.blastout") into blast_out_for_plot

    script:
    def aligner = new NGSaligner(reads:scaffold_file, output:"${pair_id}.blastout", index:"blast_db.fasta", cpus:task.cpus, extrapars:"-outfmt 6 -word_size 11")
	aligner.doAlignment("blast")
}


/*
 * Run restrict 
 */
 
process runRestrict {
	tag { pair_id }
    publishDir outputRE

    input:
    set pair_id, file(scaffold_file) from scaffold_file_for_re

    output:
    set pair_id, file("${pair_id}.restrict") into restric_file_for_graph

    script:
	"""
		restrict -sequence ${scaffold_file} -outfile ${pair_id}.restrict -single -auto -enzymes @${commonenz} -plasmid
	"""
}


/*
 * make plots
 */
 
process makePlot {
	tag { pair_id }
    publishDir outputPlot, mode: 'copy', pattern: '*.png' 
    publishDir outputGBK, mode: 'copy', pattern: '*.gbk'

    input:
    set pair_id, file(blastout), file(resites), file(scaffold) from blast_out_for_plot.join(restric_file_for_graph).join(scaffold_file_for_parsing)

    output:
    file("${pair_id}.png") 
    file("${pair_id}.gbk") 

    script:
	"""
		parse.py -n ${pair_id} -b ${blastout} -f ${scaffold} -o ${pair_id} -r ${resites}
		\$CGVIEW -i ${pair_id}.tab  -x true -f PNG -H 1000 -o ${pair_id}.png
	"""
}
/*
 * Mail notification

workflow.onComplete {

    def msg = """\
        Pipeline execution summary
        ---------------------------
        Completed at: ${workflow.complete}
        Duration    : ${workflow.duration}
        Success     : ${workflow.success}
        workDir     : ${workflow.workDir}
        exit status : ${workflow.exitStatus}
        Error report: ${workflow.errorReport ?: '-'}
        """
        .stripIndent()

    sendMail(to: params.email, subject: "ChipSeq execution: ${params.title}", body: msg,  attach: "${outputMultiQC}/multiqc_report.html")
}
 */