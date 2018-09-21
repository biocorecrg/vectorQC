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

