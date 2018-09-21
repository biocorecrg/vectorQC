# [![BioCoreCRG](https://github.com/CRG-CNAG/BioCoreMiscOpen/blob/master/logo/biocore-logo_small.png)](https://biocore.crg.eu/) Biocore @ CRG
----------
# ![vectorQC](https://github.com/biocorecrg/vectorQC/blob/master/plots/logo_vectorQC_small.png)


[![DOI](https://zenodo.org/badge/144697659.svg)](https://zenodo.org/badge/latestdoi/144697659)
[![Build Status](https://travis-ci.org/biocorecrg/vectorQC.svg?branch=master)](https://travis-ci.org/biocorecrg/vectorQC)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Nextflow version](https://img.shields.io/badge/nextflow-%E2%89%A50.31.0-brightgreen.svg)](https://www.nextflow.io/)
![Docker Automated build](https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg)

This Nextflow pipeline analyzes the results of the MiSeq sequencing of a collection of vectors (300 bp x 2 paired ends). The input is a pair of fastq files per sample (vector) and is specified in **params.config** file. The default **feature db** file is obtained by the tool PlasMapper (http://wishart.biology.ualberta.ca/PlasMapper/) using **ReBase** as a database for restriction enzymes (http://rebase.neb.com/rebase/rebase.html).

Once the pipeline is finished you will receive an e-mail with the MultiQC report attached.


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
## Download VectorQC (current version 1.0)

    curl -s -L https://github.com/biocorecrg/vectorQC/archive/v1.0.tar.gz
    tar -zvxf v1.0.tar.gz

-----
## Install VectorQC 

     sh INSTALL.sh 

This downloads the **BioNextflow library** and the file conf_tools.txt containing information about tools used by the pipeline. 

-----
## Modify nextflow.config and Dockerfile (optional) 

The config file **nextflow.config** provides the computational parameters (memory, CPUs, run time) that you might want to change; if the pipeline is run on the cluster, the batch system parameters might need to be provided (e.g., queue names). By default, the Docker container is used (see Dockerfile). Although Singularity can be used instead (uncomment this line); in this case it will be made off the Docker image. 
In Dockerfile, the user can change versions of software used by the pipeline.  

-----
## Check required parameters and modify params.config
To check the required parameters type 

    nextflow run main.nf --help

For the test run, the only parameter you might want to change is the email address, if you want to recieve an email upon finishing the run.
Below are all parameters in params.config are explain one by one.

-----
## Input parameters
### Reads
**!!Important!!** when specifying the parameters **reads** by command line you should use **"quotation marks"** if not the * will be translated in the first file. Be careful with the way you name the file since filenames can vary among facilities, machines etc.

### Common enzymes
A list of restriction enzymes that are supposed to cut within our vectors. 

### Multiconfig
This is the yaml file required by multiQC to group together the information. You can modify or eventually add some information as description.

### Features
The fasta file downloaded by **Plasmapper** tool (http://wishart.biology.ualberta.ca/PlasMapper/). The fasta header is formatted in this way:

*lpp_promoter[PRO]{lpp},30 bases, 1123 checksum.* 

- [] is a category. HYB (hyper activation binding doamin), LOC (locus), ORI (Origin of replication), OTH (other gene), PRO (promoter), REG (regulatory sequence), REP (reporter gene), SEL (gene for selection), TAG (affinity TAG) and TER (terminator).
- {} contains a small string of the sequence decription that is shown in the ploi
- Sequence length is after *{},* 

### Inserts
A custom fasta file with the header containing the name of the inserted genes / piece of DNA. An example is in:
     
    examples/inserts/genes.fa

### Output
Is a parameter that specify the output folder. It is useful in case you want to have different run changing some parameters. Default is **output**.

### tooldb
It is the text file used for generating a report with used tools. It is automatically downloaded when is run INSTALL.sh

### Email
This parameter is useful to receive a mail once the process is finished / crashed.

-----
## Run VectorQC test example

First, simulate paired reads for vectors in ./examples, running:

     ./simulate nextflow run simulate.nf

The result of running this pipeline is fastq files in ./simulate/output. The parameters for the coverage and reads are provided and can be changed in ./simulate/params.config.

Now, the pipeline can be run on these simulated fastq files:

     nextflow run main.nf
     

---------

## The pipeline
1. QC: Run FastQC on raw reads. It stores the results within **QC** folder.
1. Indexing: It makes the index of feature db fasta file using makeblastb.
1. Trimming: It reomve the adapter by using skewer tool. Another FastQC is performed after the trimming.
1. Assembling: It assembles trimmed reads by using SPAdes assembler. Results are stored within the filder **Assembly**
1. Alignment: It aligns assemlbe scaffolds to the feature DB by using blast. Results in tabular format are stored within the folder **Blast**
1. The scaffolds are also scanned for the presence of RE sites using Emboss' restrict tool and list of common enzymes specified in **params.config**. Results are stored in **REsites** folder.
1. The blast output and the RE sites are used for generating a plot using Circular Genome Viewer (http://wishart.biology.ualberta.ca/cgview/) and a genBank file for each sample.
1. Finally a report is generated by using MultiQC and sent by mail.

-----
## Generated plots:
![vector ploth](https://github.com/biocorecrg/vectorQC/blob/master/plots/pTAZ.svg)

## Report
![multiQC report](https://github.com/biocorecrg/vectorQC/blob/master/plots/report_example.png)

------
## The simulator (and test data)
In the folder **simu** there is another NF pipeline for simulating reads starting from vector sequences. It is basically a wrapper of **wgsim** tool adapted to generate sequence from circular genomes. In the folder **examples** there are some inserted genes and vectors.

### Parameters
|parameter name         | value|
|---------------------------------|------------------------|
|seqs                         |"$baseDir/../test/vectors/\*.fa"|
|fold                         |3000|
|outerd                       |600|
|stdev                        |100|
|size                         |300|
|output                       |output|
|email for notification       |yourmail@yourdomain|

-----

### Seqs
Fasta sequences with vectors.

### Fold
Number of time that the vector should be covered by the reads.

### Outerd
Outer read distance.

### Stdev
Standard deviation of the outer read distance

### Output
Output folder

### Email
Mail address for receiving a mail once the process is finished / crashed.

-----
## Running the simulator and the test examples
     nextflow run simulate/simulate.nf 
     nextflow run main.nf

-----
## DAG graph
![DAG graph](https://github.com/biocorecrg/vectorQC/blob/master/plots/grafico.png)


