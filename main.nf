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
multiconfig                 : ${params.multiconfig}
features 					: ${params.features}
inserts 					: ${params.inserts}
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

multiconfig = file(params.multiconfig)
if( !multiconfig.exists() ) exit 1, "Missing multiconfig file: ${params.multiconfig}"

tooldb = file(params.tooldb)
if( !tooldb.exists() ) exit 1, "Missing tooldb file: ${params.tooldb}"



outputQC		= "${params.output}/QC"
outputAssembly  = "${params.output}/Assembly"
outputBlast  	= "${params.output}/Blast"
outputRE  		= "${params.output}/REsites"
outputPlot  	= "${params.output}/Plots"
outputGBK		= "${params.output}/GenBank"
outputMultiQC	= "${params.output}/multiQC"
outputReport    = file("${outputMultiQC}/multiqc_report.html")



// move old multiQCreport in case it already exists 
if( outputReport.exists() ) {
  log.info "Moving old report to multiqc_report.html multiqc_report.html.old"
  outputReport.moveTo("${outputMultiQC}/multiqc_report.html.old")
}

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
   	 file("*_filt_fastqc.zip") into trimmed_fastqc_files

    script:
    def qc = new QualityChecker(input:filtered_read, cpus:task.cpus)
	qc.fastqc()
}

/*
 * Run assembly of input sequence
 */
 
process assemble {
	tag { pair_id }

    label 'big_mem_cpus'

    input:
    set pair_id, file(readsA), file(readsB) from  filtered_reads_for_assembly.flatten().collate( 3 )

    output:
   	set pair_id, file("${pair_id}_assembly.fa") into scaffold_for_evaluation

    script:
	"""
	   spades.py --cov-cutoff auto --careful --pe1-1 ${readsA} --pe1-2 ${readsB} -o ${pair_id} -t ${task.cpus} -m ${task.memory.giga} 
	   cp ${pair_id}/scaffolds.fasta ${pair_id}_assembly.fa
	"""
}

process evaluateAssembly {
	tag { pair_id }
    publishDir outputAssembly, mode: 'copy'
    echo true

    label 'big_mem_cpus'

    input:
    set pair_id, file(scaffolds) from  scaffold_for_evaluation
    
    output:
   	set pair_id, file("${pair_id}_assembly_ev.fa") into scaffold_file_for_blast, scaffold_file_for_re, scaffold_file_for_parsing

    script:
	"""
		evaluateAssembly.py -i ${scaffolds} -o ${pair_id}_assembly_ev.fa -n ${pair_id}
	"""
}

/*
 * joine db files
 */
process makeInsertDB {
	tag { params.inserts }

	when:
	params.inserts

    input:
    file(features_file) from featuresdb
	
	output:
	file("whole_db_pipe.fasta") into whole_db_fasta
	
	"""
		parseInserts.py -i ${params.inserts} -o  whole_db_pipe.fasta
     	if [ `echo ${features_file} | grep ".gz"` ]; then 
			zcat ${features_file} >> whole_db_pipe.fasta
		else 
			cat zcat ${features_file} >> whole_db_pipe.fasta
		fi
	"""

}

if (whole_db_fasta) {
	fasta_for_blast_db = whole_db_fasta
} else {
	fasta_for_blast_db = featuresdb
}

/*
 * Make blast db
 */
 
process makeblastdb {
	tag { features_file }
	
    input:
    file(features_file) from fasta_for_blast_db

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
* Make section of multiQC report about the tools used. 
*/
 
process tool_report {

	input:
	file(tooldb)

    output:
	file("tools_mqc.txt") into tool_report_for_multiQC 
		
	script:
	"""
		 make_tool_desc_for_multiqc.pl -c ${tooldb} -l fastqc,skewer,spades,blastn,cgview,emboss > tools_mqc.txt
	"""
}

process multiQC {
    publishDir outputMultiQC, mode: 'copy'

    input:
    file '*' from raw_fastqc_files.mix(logTrimming_for_QC,trimmed_fastqc_files).flatten().collect()
    file 'pre_config.yaml.txt' from multiconfig
    file (tool_report_for_multiQC)

    output:
    file("multiqc_report.html") into multiQC 
	
    script:
	def reporter = new Reporter(title:"VectorQC screening", application:"Mi-seq", subtitle:"", PI:"CRG", user:"CRG", id:"vectors", email:params.email, config_file:multiconfig)
	reporter.makeMultiQCreport()
}

/*
 * Mail notification
 */
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

    sendMail(to: params.email, subject: "VectorQC execution", body: msg,  attach: "${outputMultiQC}/multiqc_report.html")
}
