FROM biocorecrg/centos-perlbrew-pyenv-java

# File Author / Maintainer
MAINTAINER Luca Cozzuto <lucacozzuto@gmail.com> 

ARG SKEWER_VERSION=0.2.2
ARG MULTIQC_VERSION=1.6
ARG FASTQC_VERSION=0.11.5
# tool wgsim this is needed by the simulator NextFlow pipeline
ARG SAMTOOLS_VERSION=1.9
ARG BCFTOOLS_VERSION=1.9
ARG BWA_VERSION=0.7.17
ARG SPADES_VERSION=3.12.0
ARG BLAST_VERSION=2.7.1
ARG EMBOSS_VERSION=6.6.0
ARG TOOL_MULTIQC_VERSION=1.3
ARG FLASH_VERSION=1.2.11

#upgrade pip
RUN pip install --upgrade pip

# Installing samtools
RUN yum install -y xz-devel.x86_64
RUN bash -c 'curl -k -L https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2 > samtools.tar.bz2' 
RUN tar -jvxf samtools.tar.bz2
RUN cd samtools-${SAMTOOLS_VERSION}; ./configure; make; make install; cd ../ 

# Installing BCFtools
RUN bash -c 'curl -k -L https://github.com/samtools/bcftools/releases/download/${BCFTOOLS_VERSION}/bcftools-${BCFTOOLS_VERSION}.tar.bz2 > bcftools.tar.bz2'
RUN tar -jvxf bcftools.tar.bz2
RUN cd bcftools-${BCFTOOLS_VERSION}; ./configure; make; make install; cd ../

# Installing BWA
RUN bash -c 'curl -k -L https://sourceforge.net/projects/bio-bwa/files/bwa-${BWA_VERSION}.tar.bz2/download > bwa.tar.bz2'
RUN tar -jvxf bwa.tar.bz2
RUN cd bwa-${BWA_VERSION}; make; ln -s $PWD/bwa /usr/local/bin/bwa; cd ../

# Installing FLASH
RUN bash -c 'curl -k -L http://ccb.jhu.edu/software/FLASH/FLASH-${FLASH_VERSION}-Linux-x86_64.tar.gz > flash.tar.gz'
RUN tar -zvxf flash.tar.gz; cp FLASH-${FLASH_VERSION}-Linux-x86_64/flash /usr/local/bin/flash
RUN chmod +x /usr/local/bin/flash

# Installing spades
RUN bash -c 'curl -k -L http://cab.spbu.ru/files/release${SPADES_VERSION}/SPAdes-${SPADES_VERSION}-Linux.tar.gz > spades.tar.gz'
RUN tar -zvxf spades.tar.gz

#INSTALLING FASTQC
RUN bash -c 'curl -k -L https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v${FASTQC_VERSION}.zip > fastqc.zip'
RUN unzip fastqc.zip; chmod 775 FastQC/fastqc; ln -s $PWD/FastQC/fastqc /usr/local/bin/fastqc

# Installing MULTIQC_VERSION // Latest dev version is much better. 
RUN pip install -Iv https://github.com/ewels/MultiQC/archive/v${MULTIQC_VERSION}.tar.gz 
#RUN pip install --upgrade --force-reinstall git+https://github.com/ewels/MultiQC.git 

# Installing Skewer
RUN bash -c 'curl -k -L https://downloads.sourceforge.net/project/skewer/Binaries/skewer-${SKEWER_VERSION}-linux-x86_64 > /usr/local/bin/skewer'
RUN chmod +x /usr/local/bin/skewer

# Installing Blast
RUN cd /usr/local; curl --fail --silent --show-error --location --remote-name ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/${BLAST_VERSION}/ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz
RUN cd /usr/local; tar zxf ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz; rm ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz
RUN cd /usr/local/bin; ln -s /usr/local/ncbi-blast-${BLAST_VERSION}+/bin/* .

# Installing CGVIEW
RUN bash -c 'curl -k -L http://wishart.biology.ualberta.ca/cgview/application/cgview.zip > cgview.zip'
RUN unzip cgview.zip; rm cgview.zip

# INSTALLING EMBOSS 
RUN bash -c 'curl -k -L ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-${EMBOSS_VERSION}.tar.gz > emboss.tar.gz'
RUN tar -zvxf emboss.tar.gz; cd EMBOSS-${EMBOSS_VERSION}; ./configure; make; make install

# Downloading REBASE
RUN mkdir data; cd data
RUN bash -c 'curl -k -L ftp://ftp.ebi.ac.uk/pub/databases/rebase/withrefm.txt.gz > withrefm.txt.gz'
RUN bash -c 'curl -k -L ftp://ftp.ebi.ac.uk/pub/databases/rebase/proto.txt.gz > proto.txt.gz'

RUN gunzip withrefm.txt.gz; gunzip proto.txt.gz; rebaseextract -infile withrefm.txt -protofile proto.txt

#Adding perl script for improving multiQC report
RUN bash -c 'curl -k -L  https://github.com/CRG-CNAG/make_tool_desc_for_multiqc/archive/${TOOL_MULTIQC_VERSION}.tar.gz > tool_ver.tar.gz'
RUN tar -zvxf tool_ver.tar.gz; mv make_tool_desc_for_multiqc-${TOOL_MULTIQC_VERSION}/make_tool_desc_for_multiqc.pl /usr/local/bin/ ; chmod +x /usr/local/bin/make_tool_desc_for_multiqc.pl

#Adding perl module
RUN cpanm List::MoreUtils

# Clean cache
RUN yum clean all 
#chmod

#cleaning
RUN rm -fr *.tar.gz; rm -fr *.bz2
RUN rm -rf /var/cache/yum
RUN rm -fr fastqc.zip  samtools-*

ENV PATH="/project/SPAdes-${SPADES_VERSION}-Linux/bin/:${PATH}"
ENV CGVIEW="java -jar /project/cgview/cgview.jar"
