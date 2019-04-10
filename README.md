<img align="right" href="https://biocore.crg.eu/" src="https://github.com/CRG-CNAG/BioCoreMiscOpen/blob/master/logo/biocore-logo_small.png" />

# ![vectorQC](https://github.com/biocorecrg/vectorQC/blob/master/plots/logo_vectorQC_small.png) 

----------



[![DOI](https://zenodo.org/badge/144697659.svg)](https://zenodo.org/badge/latestdoi/144697659)
[![Build Status](https://travis-ci.org/biocorecrg/vectorQC.svg?branch=master)](https://travis-ci.org/biocorecrg/vectorQC)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Nextflow version](https://img.shields.io/badge/nextflow-%E2%89%A50.31.0-brightgreen.svg)](https://www.nextflow.io/)
[![Docker Build Status](https://img.shields.io/docker/automated/biocorecrg/vectorqc.svg)](https://cloud.docker.com/u/biocorecrg/repository/docker/biocorecrg/vectorqc/builds)


This Nextflow pipeline analyzes the results of the MiSeq sequencing of a collection of circular DNA vectors (paired ends). 
The input is a pair of fastq files per sample (a vector) and a fasta file of inserts introduced in the vectors.
For the input detail see description of the **params.config** file below. 
For each vector, the pipeline outputs an image of the DNA map with annotation and the GenBank file.


## Software Requirements 
**Docker** (https://www.docker.com/) or **Singularity** (https://www.sylabs.io/) Linux containers and **NextFlow** workflow manager (https://www.nextflow.io/). 
On Mac OS, Docker can be installed, with the Homebrew manager (https://brew.sh), as:

     brew cask install docker
     
After Docker is installed, to be able to run the pipeline, you need to launch Docker (e.g., on Mac, clicking on it from the Launchpad; for the first time launch, Docker will ask you to register on its website).

NextFlow needs both **Java RE** and **Java SE Developer Kit (JDK)** version 1.8 or later (JDK is not automatically updated on MAC; it needs to be manually installed; check its version with "java -version"). 
To install NextFlow:

     curl -s https://get.nextflow.io | bash 

To test it:

    ./nextflow run hello
    
-----
## Download VectorQC (current version 1.5)

    curl -s -L https://github.com/biocorecrg/vectorQC/archive/v1.5.tar.gz > v1.5.tar.gz
    tar -zvxf v1.5.tar.gz

-----
## Install VectorQC 

     sh INSTALL.sh 

This downloads the **BioNextflow library** and the file conf_tools.txt containing information about tools used by the pipeline. 

-----
## Modify nextflow.config and Dockerfile (optional) 

The config file **nextflow.config** provides the computational parameters (memory, CPUs, run time) that you might want to change; if the pipeline is run on the cluster, the batch system parameters might need to be provided (e.g., queue names). By default, the Docker container is used (see Dockerfile); although Singularity can be used instead using the nextflow parameter **-with-singularity** (in this case, the Docker image will be converted to the Singularity image). 
In **Dockerfile**, you can change versions of software used by the pipeline.  

-----
## Check required parameters and modify params.config
To check the required parameters type 

    nextflow run main.nf --help

For the test run, the only parameter you might want to change is the email address if you want to recieve an email upon finishing the run. The e-mail will arrive with the MultiQC report attached.

Below all parameters in params.config are explained in detail.

-----
## Input 
### Reads (param _reads_ in the file _params.config_)
This parameters indicate the path where the fastq files are stored. Each file pairs matching a glob pattern indicated by the asterisk will be analyzed in parallel. 
**!!Important!!** when specifying the parameters **reads** by command line you should use **"quotation marks"**. Be careful with file names as the naming can vary among facilities, instruments, etc. 

### Inserts (param _inserts_ in the file _params.config_)
A custom fasta file with the header containing the name of the inserted genes/DNA. No whithe-spaces are allowed in the fasta header! 

An example can be found in:
     
    examples/inserts/genes.fa

### Features (param _features_ in the file _params.config_)
The fasta file (in the folder **db**) downloaded using the **Plasmapper** tool (http://wishart.biology.ualberta.ca/PlasMapper/). The fasta header is formatted in this way:

*lpp_promoter[PRO]{lpp},30 bases, 1123 checksum.* 

- [] is a category. HYB (hyper activation binding doamin), LOC (locus), ORI (Origin of replication), OTH (other gene), PRO (promoter), REG (regulatory sequence), REP (reporter gene), SEL (gene for selection), TAG (affinity TAG) and TER (terminator).
- {} contains a small string of the sequence decription that is shown on the plot.
- Sequence length. 

### Common enzymes (param _commonenz_ in the file _params.config_)
A list of restriction enzymes for the vectors (the file **db/common.ids**). 

### Parameter for reads trimming (using _skewer_) 
The following parameters (in the file _params.config_) are used by the skewer algorithm for trimming reads (for further detail on the algorithm, see https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-15-182): 
- _adapter_ [in skewer: -x <str> Adapter sequence/file] (by default, the universal Illumina adapter is used), 
- _minsize_ [ in skewer: -l, --min <int> The minimum read length allowed after trimming; (18)],
- _trimquality_ [in skewer: -q, --end-quality  <int> Trim 3' end until specified or higher quality reached; (0)], and 
- _meanquality_ [in skewer: -Q, --mean-quality <int> The lowest mean quality value allowed before trimming; (0)].          

### Output (param _output_ in the file _params.config_)
The output folder. Default is **output**. Outputs of the pipelines run with different parameters can be saved in different folders. 

### Email (param _email_ in the file _params.config_)
This parameter is useful to receive an e-mail once the process is finished or crashed.


-----
## Run VectorQC test example 

First, simulate paired reads for vectors in ./examples, running:

     nextflow run ./simulate/simulate.nf

The result of running this pipeline is the fastq files in ./simulate/output. The parameters for the coverage and reads are provided and can be changed in ./simulate/params.config. For detail, see ./simulate/README.md.

Now, the pipeline can be run on these simulated fastq files:

     nextflow run main.nf
     
The run takes 3-5 mins.
The results are in ./output folder. For more detail on the output, see the description of the pipeline below.


To override the parameters, run the pipeline with those parameters specified in the command line; for example, to simulate reads of the length 250bp, run

     nextflow run ./simulate/simulate.nf --size 250 --output simulate_250
   
The pipeline can be resumed and run in the background

     nextflow run main.nf --reads "./simulate/simulate_250/*{1,2}.fq" --output output_250 -resume -bg > log_250.txt


---------

## Pipeline
1. **QC**. Run _FastQC_ [1] on raw reads. Results are in the folder **QC**.
1. **Trimming reads**. Remove the adapter by using _skewer_ [2]. Results are in the folder **QC**.
1. **QC of trimmed reads**. Results are in the folder **QC**.
1. **Indexing features**. Index the fasta file of features using _makeblastdb_ from NCBI BLAST+ toolbox [3].
1. **Read assembly**. Assemble trimmed reads and merged them, if needed (default is no) using the SPAdes assembler [4]. If the parameter _merge = "yes"_, the FLASH algorithm [5] is used to merge overlapping paired reads. 
1. **Assembly evaluation**. Evaluate and merge assembled contigs using the in-house script _evaluateAssembly.py_ (in ./bin). If more than one contig was assembled for a vector, contigs are merged into a circular DNA randomly. Contigs with coverage lower than 50% or more than 150% than the average are removed. Results are in the folder **Refined_Assembly**, while the original assembly is stored in the folder **Assembly**.
1. **Alignment**. Align assembled scaffolds to the feature database using BLAST [6]. Results are stored in the folder **Blast**.
1. **Annotation of the restriction enzyme sites**. The scaffolds are scanned for the presence of RE sites using the EMBOSS tool _restrict_ [7] over the REBASE database [8] and the list of common enzymes specified in the  parameter _commonenz_ in **params.config**. Results are in the folder **REsites**.
1. **Generation of results**. Make a vector map using the Circular Genome Viewer (http://wishart.biology.ualberta.ca/cgview/) [9] and the GenBank-formatted file for each sample. Results are in the folders 
1. **Variant calling**. If reference sequences are provided, the pipeline will align the assembled vectors to the refence one by using BWA[10] and it will call the variants with BCFtools[11]. Variants are then stored within the folder **Variants** 
**Plots** and **GenBank**. Generate the MultiQC [12] report and send an e-mail.

-----
## Pipeline output

### An example of the MultiQC Report
![multiQC report](https://github.com/biocorecrg/vectorQC/blob/master/plots/report_example.png)

### An example of the vector map:
![vector ploth](https://github.com/biocorecrg/vectorQC/blob/master/plots/pTAZ.svg)


------
-----
## DAG graph
![DAG graph](https://github.com/biocorecrg/vectorQC/blob/master/plots/grafico.png)

## Run VectorQC on AWS Batch

For running VectorQC on [AWS Batch](https://aws.amazon.com/batch/), we provide a sample profile in ```nextflow.config```.
You need to adapt your parameters according to your deployment. For more detail, see [this blogpost](https://apeltzer.github.io/post/01-aws-nfcore/).

Once your parameters are set, you can run the pipeline by using this commandline from an [EC2](https://aws.amazon.com/ec2/) instance:

     nextflow run main.nf -profile awsbatch -bucket-dir s3://mys3bucket/work



-----
## References
1. Andrews, S., https://www.bioinformatics.babraham.ac.uk/projects/fastqc/. 2010.
2. Jiang, H., et al., Skewer: a fast and accurate adapter trimmer for next-generation sequencing paired-end reads. BMC Bioinformatics, 2014. 15: p. 182.
3. Camacho, C., et al., BLAST+: architecture and applications. BMC Bioinformatics, 2009. 10: p. 421.
4. Bankevich, A., et al., SPAdes: a new genome assembly algorithm and its applications to single-cell sequencing. J Comput Biol, 2012. 19(5): p. 455-77.
5. Magoč, T. and S.L. Salzberg, FLASH: fast length adjustment of short reads to improve genome assemblies. Bioinformatics, 2011. 27(21): p. 2957-63.
6. Altschul, S.F., et al., Basic local alignment search tool. J Mol Biol, 1990. 215(3): p. 403-10.
7. Rice, P., I. Longden, and A. Bleasby, EMBOSS: the European Molecular Biology Open Software Suite. Trends Genet, 2000. 16(6): p. 276-7.
8. Roberts RJ, Vincze T, Posfai J, Macelis D. REBASE--a database for DNA restriction and modification: enzymes, genes and genomes. Nucleic Acids Res. 2015 Jan;43(Database issue) http://rebase.neb.com/rebase/rebase.html 
9. Stothard, P. and D.S. Wishart, Circular genome visualization and exploration using CGView. Bioinformatics, 2005. 21(4): p. 537-9.
10. Li H, Durbin R. Fast and accurate long-read alignment with Burrows-Wheeler transform. Bioinformatics. 2010 Mar 1;26(5):589-95.
11. Li H, Handsaker B, Wysoker A, Fennell T, Ruan J, Homer N, Marth G, Abecasis G, Durbin R; 1000 Genome Project Data Processing Subgroup. The Sequence Alignment/Map format and SAMtools. Bioinformatics. 2009 Aug 15;25(16):2078-9
12. Ewels, P., et al., MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics, 2016. 32(19): p. 3047-8.
