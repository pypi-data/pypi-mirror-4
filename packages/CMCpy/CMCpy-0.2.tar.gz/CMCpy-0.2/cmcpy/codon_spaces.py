import numpy
from math import floor, pow, cos, pi
from cmath import exp
import warnings

class _CodonSpace():
    """
    This private base class weakly enforces a read-only/immutable codon mutation matrix  
    """
    def __init__(self, num_codons, mu):
        if (mu <= 0 or mu >= 1):
            raise ValueError("Mutation parameter mu must be in the noninclusive range (0,1). You passed mu: %f" % (mu))
        if (num_codons < 2 or (num_codons != floor(num_codons))):
            raise ValueError("Parameter num_codons must be an integer >= 2. You passed %f" % (num_codons))
        self.num_codons = num_codons
        self.mu = mu

    def get_mutation_matrix(self):    
        return self._mutation_matrix.copy()

class RingCodonSpace (_CodonSpace):
    """
    Ring codon spaces are wrapped linear mutation spaces where codons mutate only to their two immediate neighbors.
    For ring codon models, mu defines the probability of change to one of two codon neighbors.
    The probability of no change is [1 - (2*mu)]

    >>> codons = RingCodonSpace(num_codons = 5,mu = 0.1)
    >>> mm = codons.get_mutation_matrix()
    >>> mm.round(3)
    array([[ 0.8,  0.1,  0. ,  0. ,  0.1],
           [ 0.1,  0.8,  0.1,  0. ,  0. ],
           [ 0. ,  0.1,  0.8,  0.1,  0. ],
           [ 0. ,  0. ,  0.1,  0.8,  0.1],
           [ 0.1,  0. ,  0. ,  0.1,  0.8]])     
    """
    def __init__(self, num_codons, mu):
        _CodonSpace.__init__(self, num_codons, mu)
        self._mutation_matrix = (numpy.roll(numpy.eye(num_codons),-1,axis=1) +  numpy.roll(numpy.eye(num_codons),1,axis=1)) * mu + (numpy.eye(num_codons) * (1.0 - (2 * mu)))

    def __str__(self, dict):
        data = " ".join([str(dict[i]) for i in xrange(self.num_codons)]) 
        return ''.join(['[',data,']'])

    """ Required for use with the Perturbative method draft"""
    def get_derivative_matrix (self): 
        try:
            return self._derivative_matrix.copy()
        except AttributeError:
            num_codons = self.num_codons
            self._derivative_matrix = ((numpy.roll(numpy.eye(num_codons),-1,axis=1) +  numpy.roll(numpy.eye(num_codons),1,axis=1)) - (numpy.eye(num_codons) * 2))
            return self._derivative_matrix.copy()

    """ Required for use with the Homotopy method"""
    def get_mutation_eigensystem (self):
        try:
            return (self._eigenvalues.copy(),self._eigenvector_matrix.copy())
        except AttributeError:
            ## mumat = self.get_mutation_matrix()
            ## import scipy.linalg as sl
            ## (self._eigenvalues,self._eigenvector_matrix) =  sl.eigh(mumat)
            mu = self.mu
            n = self.num_codons
            jvec = numpy.arange(n)
            svec = (1 - 2*mu) + 2*mu*numpy.cos(2*numpy.pi*jvec/n)
            ymat = numpy.zeros((n,n),dtype=complex)
            omegavec = numpy.exp(2*numpy.pi*1j*jvec/n)
            for j in range(n):
                ymat[:,j] = omegavec[j]**jvec
                
            ymat /= numpy.sqrt(n)
            ymat = numpy.matrix(ymat)
            # sort eigenpairs in order of ascending eigenvalues
            _ind = numpy.argsort(svec)
            svec = svec[_ind]
            ymat = ymat[:,_ind]
            self._eigenvalues = svec
            self._eigenvector_matrix = ymat
            
            return (self._eigenvalues.copy(),self._eigenvector_matrix.copy())
    

    """ This is a pass-through for Ring Models to allow dispatch"""
    def post_process_perturbative_solution (self, lhtopy, vhtopy):
        return (lhtopy,vhtopy)

class WordCodonSpace (_CodonSpace):
    """
    Word codon spaces model natural codons with a finite number of bases and a finite word-length.

    For word codon models, mu defines the total probability of change of a base to any neighbor.
    The probability of no change of a single base is defined as (1 - mu).

    If kappa is not equal to 1.0, then num_bases must be even.

    >>> codons = WordCodonSpace(num_bases = 2,num_positions = 2, mu = 0.1)
    >>> mm = codons.get_mutation_matrix()
    >>> mm.round(3)
    array([[ 0.81,  0.09,  0.09,  0.01],
           [ 0.09,  0.81,  0.01,  0.09],
           [ 0.09,  0.01,  0.81,  0.09],
           [ 0.01,  0.09,  0.09,  0.81]])
    >>> codons = WordCodonSpace(num_bases = 4,num_positions = 2, mu = 0.2,kappa = 2)
    >>> mm = codons.get_mutation_matrix()
    >>> mm.round(3)
    array([[ 0.64 ,  0.08 ,  0.04 ,  0.04 ,  0.08 ,  0.01 ,  0.005,  0.005,
             0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003],
           [ 0.08 ,  0.64 ,  0.04 ,  0.04 ,  0.01 ,  0.08 ,  0.005,  0.005,
             0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003],
           [ 0.04 ,  0.04 ,  0.64 ,  0.08 ,  0.005,  0.005,  0.08 ,  0.01 ,
             0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005],
           [ 0.04 ,  0.04 ,  0.08 ,  0.64 ,  0.005,  0.005,  0.01 ,  0.08 ,
             0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ],
           [ 0.08 ,  0.01 ,  0.005,  0.005,  0.64 ,  0.08 ,  0.04 ,  0.04 ,
             0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003],
           [ 0.01 ,  0.08 ,  0.005,  0.005,  0.08 ,  0.64 ,  0.04 ,  0.04 ,
             0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003],
           [ 0.005,  0.005,  0.08 ,  0.01 ,  0.04 ,  0.04 ,  0.64 ,  0.08 ,
             0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005],
           [ 0.005,  0.005,  0.01 ,  0.08 ,  0.04 ,  0.04 ,  0.08 ,  0.64 ,
             0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ],
           [ 0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,
             0.64 ,  0.08 ,  0.04 ,  0.04 ,  0.08 ,  0.01 ,  0.005,  0.005],
           [ 0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,
             0.08 ,  0.64 ,  0.04 ,  0.04 ,  0.01 ,  0.08 ,  0.005,  0.005],
           [ 0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,
             0.04 ,  0.04 ,  0.64 ,  0.08 ,  0.005,  0.005,  0.08 ,  0.01 ],
           [ 0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,
             0.04 ,  0.04 ,  0.08 ,  0.64 ,  0.005,  0.005,  0.01 ,  0.08 ],
           [ 0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,
             0.08 ,  0.01 ,  0.005,  0.005,  0.64 ,  0.08 ,  0.04 ,  0.04 ],
           [ 0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,
             0.01 ,  0.08 ,  0.005,  0.005,  0.08 ,  0.64 ,  0.04 ,  0.04 ],
           [ 0.003,  0.003,  0.04 ,  0.005,  0.003,  0.003,  0.04 ,  0.005,
             0.005,  0.005,  0.08 ,  0.01 ,  0.04 ,  0.04 ,  0.64 ,  0.08 ],
           [ 0.003,  0.003,  0.005,  0.04 ,  0.003,  0.003,  0.005,  0.04 ,
             0.005,  0.005,  0.01 ,  0.08 ,  0.04 ,  0.04 ,  0.08 ,  0.64 ]])
    """
    def __init__(self, num_bases, num_positions, mu, kappa=1.0):
        if (num_bases != floor(num_bases)):
            warnings.warn("WARNING: num_bases should have an integer value and will be floored. You passed num_bases: %f" % (num_bases))
            num_bases = int(floor(num_bases))
        if (num_positions != floor(num_positions)):
            warnings.warn("WARNING: num_positions should have an integer value and will be floored. You passed num_positions: %f" % (num_positions))
            num_positions = int(floor(num_positions))
        if (kappa < 1):
            raise ValueError("Transition/transversion ratio parameter kappa must be >= 1. You passed kappa: %f" % (kappa))
        if (kappa != 1.0 and (num_bases & 1)):
            raise ValueError("Parameter num_bases must be even if transition/transversion ratio parameter kappa != 1.0. You passed num_bases: %d and kappa: %f" % (num_bases, kappa))
        num_codons = num_bases ** num_positions
        _CodonSpace.__init__(self, num_codons, mu)
        self.num_bases = num_bases
        self.num_positions = num_positions
        self.kappa = kappa
        base_mutation_matrix = numpy.zeros((num_bases,num_bases))
        for i in xrange(num_bases):
            for j in xrange(num_bases):
                value = 0
                if (i == j):
                    value = 1.0 - mu
                elif (not i & 1 and j == (i + 1)): # i is even
                    value = (kappa * mu) / (kappa + (num_bases - 2))
                elif (    i & 1 and j == (i - 1)): # i is odd
                    value = (kappa * mu) / (kappa + (num_bases - 2))                
                else:
                    value = mu / (kappa + (num_bases - 2))
                base_mutation_matrix[i][j] = value
        self._base_mutation_matrix = base_mutation_matrix 
        self._mutation_matrix =  base_mutation_matrix
        for p in xrange(num_positions - 1):
                self._mutation_matrix = numpy.kron(self._mutation_matrix,base_mutation_matrix)

    def get_base_mutation_matrix (self):
        """
        Returns the mutation matrix of bases in one site.
        """
        return self._base_mutation_matrix.copy()


    def get_derivative_matrix (self):
        """
        This function exists to serve the perturbative solution draft in evolvers.py

        """
        try:
            return self._derivative_matrix.copy()
        except AttributeError:
            self._derivative_matrix = self._base_mutation_matrix.copy()
            self._derivative_matrix /= self.mu
            numpy.fill_diagonal(self._derivative_matrix,-1)
            return self._derivative_matrix.copy()


    """ Required for use with the Homotopy method"""
    def get_mutation_eigensystem (self):
        try:
            return (self._eigenvalues.copy(),self._eigenvector_matrix.copy())
        except AttributeError:
            mumat = self.get_base_mutation_matrix()
            raise NotImplementedError, "The Homotopy method has so far only been implemented for ring models."
            #import scipy.linalg as sl
            #(self._eigenvalues,self._eigenvector_matrix) = sl.eigh(mumat)
            #return (self._eigenvalues.copy(),self._eigenvector_matrix.copy())
    

    def post_process_perturbative_solution (self, lpert, vpert):
        np = self.num_positions
        v = vpert 
        for p in xrange(np - 1):
             v = numpy.kron(v,v)
        l = pow(lpert,np)
        return (l,v)

    def __str__(self, dict):
        nb = self.num_bases
        np = self.num_positions
        nc = self.num_codons
        data = []
        for i in xrange(0,nc,nb):
            s = " ".join([str(dict[i]) for i in xrange(i,(i+nb))])
            data.append(''.join(['|',s,'|']))
        return '\n'.join(data)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
