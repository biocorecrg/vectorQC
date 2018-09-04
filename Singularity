BootStrap: debootstrap
OSVersion: stretch
MirrorURL:  http://ftp.fr.debian.org/debian/
Include: build-essential curl libncurses5-dev liblzma-dev python python-dev python-setuptools python-pip bzip2 zlib1g-dev libbz2-dev zip unzip

%runscript
    echo "Welcome to VectorQC Singularity Image"


%post

    SKEWER_VERSION=0.2.2
    MULTIQC_VERSION=1.6
    FASTQC_VERSION=0.11.5
    SPARSE_VERSION=2.0.3
    SAMTOOLS_VERSION=1.4.1
    SPADES_VERSION=3.12.0
    BLAST_VERSION=2.7.1
    EMBOSS_VERSION=6.6.0

    # Needed for EMBOSS
    LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

    # Install
    apt-get install -y --allow-unauthenticated default-jdk


    # Installing samtools
    curl -k -L https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2 > samtools.tar.bz2
    tar -jvxf samtools.tar.bz2
    cd samtools-${SAMTOOLS_VERSION}; ./configure; make; make install; cd ../
    
    # Installing spades
    curl -k -L http://cab.spbu.ru/files/release${SPADES_VERSION}/SPAdes-${SPADES_VERSION}-Linux.tar.gz > spades.tar.gz
    tar -zvxf spades.tar.gz
    
    #INSTALLING FASTQC
    curl -k -L https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v${FASTQC_VERSION}.zip > fastqc.zip
    unzip fastqc.zip; chmod 775 FastQC/fastqc; ln -s $PWD/FastQC/fastqc /usr/local/bin/fastqc
    
    
    # Installing MULTIQC_VERSION // Latest dev version is much better. 
    pip install -Iv https://github.com/ewels/MultiQC/archive/v${MULTIQC_VERSION}.tar.gz
    
    
    # Installing Skewer
    curl -k -L https://downloads.sourceforge.net/project/skewer/Binaries/skewer-${SKEWER_VERSION}-linux-x86_64 > /usr/local/bin/skewer
    chmod +x /usr/local/bin/skewer
    
    # Installing Blast
    cd /usr/local; curl --fail --silent --show-error --location --remote-name ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/${BLAST_VERSION}/ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz
    cd /usr/local; tar zxf ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz; rm ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz
    cd /usr/local/bin; ln -s /usr/local/ncbi-blast-${BLAST_VERSION}+/bin/* .
    
    # Installing CGVIEW
    curl -k -L http://wishart.biology.ualberta.ca/cgview/application/cgview.zip > cgview.zip
    unzip cgview.zip; rm cgview.zip
    
    # INSTALLING EMBOSS 
    # curl -k -L ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-${EMBOSS_VERSION}.tar.gz > emboss.tar.gz
    # tar -zvxf emboss.tar.gz; cd EMBOSS-${EMBOSS_VERSION}; ./configure; make; make install
    # Installing EMBOSS via APT
    apt-get install -y --allow-unauthenticated emboss
    
    # Downloading REBASE
    mkdir data; cd data
    curl -k -L ftp://ftp.ebi.ac.uk/pub/databases/rebase/withrefm.txt.gz > withrefm.txt.gz
    curl -k -L ftp://ftp.ebi.ac.uk/pub/databases/rebase/proto.txt.gz > proto.txt.gz
    
    gunzip withrefm.txt.gz; gunzip proto.txt.gz; rebaseextract -infile withrefm.txt -protofile proto.txt
    
    chmod +x /usr/local/bin/*
    
    rm -fr fastqc.zip  samtools-*


%environment
    export PATH="/project/SPAdes-${SPADES_VERSION}-Linux/bin/:${PATH}"
    export CGVIEW="java -jar /project/cgview/cgview.jar"


%labels
    Maintainer Biocorecrg
    Version 0.1.0

