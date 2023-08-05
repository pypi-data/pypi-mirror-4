#!/usr/bin/python

"""
"""

import sys
from Bio import AlignIO
from biofrills.alnutils import sequence_weights

# Load alignment from argv
fname = sys.argv[1]
aln = AlignIO.read(fname,
            ('clustal' if fname.endswith('.aln') else 'fasta'))
weights = sequence_weights(aln)
# Output
for seq, wt in zip(aln, weights):
    print "%f\t%s" % (wt, seq.id)
print "Summed weight:", sum(weights)


