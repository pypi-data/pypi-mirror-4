Usage: SiVaC.py [-h] [-f FILE] [-m MODE] [-c COMPRESSEDFILE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  interaction mode: filename [default: dataset/citation-
                        PaperJSON_199star.graph.txt]
  -m MODE, --mode MODE  interaction mode: checkAllEdges, testGetIncoming,
                        testGetOutgoing, testGetAll,
                        testPercentageOfDiagonals, or testExists [default:
                        checkAllEdges]
  -c COMPRESSEDFILE, --compressedfile COMPRESSEDFILE
                        interaction mode: compressed filename [default: None]

=============================================================================

By default, using SiVaC as described above will provide statistics for each
mode based on random input values of nodes and arcs.

For example:
$ ./SiVaC.py -c dataset/citation-PaperJSON_199star.graph.txt.xA8 -m testExists
index length is 68
index size in memory is 3352
Average time for checking if a random edge exists 0.000617676019669

In the example above, SiVaC computes the average time of checking whether an
arc exists in the graph by performing a check for 1000 random arcs.

For the purposes of the data challenge [1], one has to customize the code to provide
his own input. A commented code snippet is provided for modes testGetIncoming, 
testGetOutgoing, testGetAll, and testExists in the main function of SiVaC.

For example, to directly access all the out-neighbors of node handler 6, you would
need to change and uncomment the respective code snippet to the following snippet:
testGetOutgoing(compressed,n,k,mySortedIndex,[6])

For sequential access of node handlers 2,5,1,6, you would need to change and uncomment 
the respective code snippet to the following snippet:
testGetOutgoing(compressed,n,k,mySortedIndex,[2,5,1,6])

Of course, after each such customisation, remember to run SiVaC specifying
the appropriate mode. For the examples above, you would need to run SiVaC
in the following manner:
$ ./SiVaC.py -c dataset/citation-PaperJSON_199star.graph.txt.xA8 -m testGetOutgoing

[1] http://www.wsdm2013.org/index.php/authors/data-challenge
