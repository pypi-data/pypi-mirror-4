import numpy
import codon_spaces
import pdb

class _Misreading():
    """
    This private base class weakly enforces a read-only/immutable codon misreading matrix  
    """
    def __init__(self, codons):
        self.codons = codons

    def get_misreading_matrix(self):    
        return self._misreading_matrix.copy()

class RingMisreading (_Misreading):
    """
    Ring misreading is one-dimensional misreading uniform over all
    other codons.  For ring misreading, (mr/(nc - 1)) is the
    probability of misreading as a specific codon.  The probability of
    no misreading is (1 - (mr)).

    The misreading parameter is a list with one element, mr.

    >>> codons = codon_spaces.RingCodonSpace(num_codons = 5,mu = 0.1)
    >>> misreading = RingMisreading(codons,[0.1])
    >>> mr = misreading.get_misreading_matrix()
    >>> mr.round(3)
    array([[ 0.9  ,  0.025,  0.025,  0.025,  0.025],
           [ 0.025,  0.9  ,  0.025,  0.025,  0.025],
           [ 0.025,  0.025,  0.9  ,  0.025,  0.025],
           [ 0.025,  0.025,  0.025,  0.9  ,  0.025],
           [ 0.025,  0.025,  0.025,  0.025,  0.9  ]])
    """
    def __init__(self, codons, misreading):
        if (len(misreading) != 1):
            raise ValueError("WARNING: misreading should be a list of length 1.")
        _Misreading.__init__(self, codons)
        nc = codons.num_codons
        mr = misreading[0]
        self._misreading_matrix = (numpy.ones((nc,nc)) * (mr / (nc - 1)) + (numpy.eye(nc) * ((1 - mr) - (mr / (nc - 1)))))


class PositionalMisreading (_Misreading):
    """
    Positional misreading models misreading on word codon spaces which
    model natural codons with a finite number of bases and a finite
    word-length.

    For positional misreading, the misreading parameter is a list of
    positional misreading parameters mr_i which define the total
    misreading probability of a base at position i to any neighbor.
    The probability of no misreading of a single base at position i is
    defined as (1 - mr_i).

    >>> codons = codon_spaces.WordCodonSpace(num_bases = 2,num_positions = 2, mu = 0.1)
    >>> misreading = PositionalMisreading(codons,[0.1,0.01])
    >>> mr = misreading.get_misreading_matrix()
    >>> mr.round(3)
    array([[ 0.891,  0.099,  0.009,  0.001],
           [ 0.099,  0.891,  0.001,  0.009],
           [ 0.009,  0.001,  0.891,  0.099],
           [ 0.001,  0.009,  0.099,  0.891]])    
    """
    def __init__(self, codons, misreading):
        nb = codons.num_bases
        np = codons.num_positions
        if (np != len(misreading)):
            raise ValueError("misreading should be a list of length equal to number of positions in codons.")
        nc = nb ** np
        _Misreading.__init__(self, codons)
        nmr = numpy.concatenate((misreading[1:], misreading[0:1]))
        #pdb.set_trace()
        for k in xrange(np):
            base_misreading_matrix = numpy.zeros((nb,nb))
            for i in xrange(nb):
                for j in xrange(nb):
                    value = 0
                    if (i == j):
                        value = 1.0 - nmr[k]
                    else:
                        value = nmr[k] / (nb - 1)
                    base_misreading_matrix[i][j] = value
            if k == 0 :
                self._misreading_matrix = base_misreading_matrix
            else :
                self._misreading_matrix = numpy.kron(self._misreading_matrix,base_misreading_matrix)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
