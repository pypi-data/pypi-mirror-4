import numpy
import pdb
from math import floor
import warnings
import random
import string
import itertools

class _AminoAcidSpace():
    """
    This private base class weakly enforces a read-only/immutable amino acid physicochemical property space.

    Coordinates may be generated randomly. A pseudo-random number generator is initialized with a seed of 42 if
    no seed is passed in. Labels will be lower-case letters unless passed in.
    """
    
    def get_labels (self,string):
        for i in xrange(len(string)):
            yield string[i]
        for label in self.get_labels(string):
            for i in xrange(len(string)):
                yield label + string[i]

    def __init__(self, num_aas, coords, labels, num_dims, seed):
        if (num_aas and num_aas != floor(num_aas)):
            warnings.warn("WARNING: num_aas passed to %s should have an integer value. You passed num_aas: %f. Value will be floored." % (self.__name__,num_aas))
            num_aas = floor(num_aas)
        if (num_aas and coords):
            warnings.warn("WARNING: if you initialize an amino acid space with coords, then any value of num_aas passed in will be ignored.")
            num_aas = len(coords)
        elif not num_aas and coords:
            num_aas = len(coords)
        elif (not num_aas and not coords):
            raise ValueError("Either num_aas or coords must be passed in when initializing an amino acid space.")  
        if (labels and len(labels) != num_aas) :
            raise ValueError("Number of labels passed in must equal number of amino acids.")
        self.num_aas = num_aas
        self.num_amino_acids = num_aas
        self.num_dims = num_dims
        self.seed = seed
        self.random_number_generator = numpy.random.RandomState(seed)
        self.distribution_method =  self.random_number_generator.uniform
        self.distribution_method_args = (0,1)

        if coords:    
            self.coords = coords
        else:
            self._generate_coords()

        self._compute_distances()
        self._compute_maxmin()
        

        if labels:
            self.labels = labels
        else:
            self.labels = list(itertools.islice(self.get_labels(string.ascii_lowercase),0,num_aas))

    def seed(self,seed = None):
        random.seed(seed)

    def _generate_coords(self):
        df  = self.distribution_method
        dfa = self.distribution_method_args
        na = self.num_aas
        nd = self.num_dims
        arglist = list(dfa)
        arglist.append((nd,na))
        variates = df(*arglist)
        self.coords = numpy.vsplit(numpy.transpose(variates),na)
        self.coords.sort(key=lambda e:e[0][0])

    def set_random_coord_distribution(self, distribution_method, distribution_method_args):
        """
        >>> aa = RegionAminoAcidSpace(num_aas = 5)
        >>> aa.seed
        42
        >>> map(lambda x: x.round(3),aa.coords)
        [array([[ 0.156]]), array([[ 0.375]]), array([[ 0.599]]), array([[ 0.732]]), array([[ 0.951]])]
        >>> prng = aa.random_number_generator
        >>> aa.set_random_coord_distribution(prng.normal,(2,1))
        >>> aa.reinitialize()
        >>> map(lambda x: x.round(3),aa.coords)
        [array([[ 1.419]]), array([[ 1.429]]), array([[ 1.475]]), array([[ 2.279]]), array([[ 3.011]])]
        >>> dm = aa.get_distance_matrix()
        >>> dm.round(3)
        array([[ 0.   ,  0.009,  0.056,  0.86 ,  1.591],
               [ 0.009,  0.   ,  0.046,  0.85 ,  1.582],
               [ 0.056,  0.046,  0.   ,  0.804,  1.536],
               [ 0.86 ,  0.85 ,  0.804,  0.   ,  0.731],
               [ 1.591,  1.582,  1.536,  0.731,  0.   ]])
        """
        self.distribution_method =  distribution_method
        self.distribution_method_args = distribution_method_args        

    def reinitialize(self, coords = None): ## NOTE THAT reinitialize() WILL ALTER COORDS EVEN IF THEY ARE SET EXPLICITLY DURING INITIALIZATION
        if coords:    
            self.coords = coords
        else:
            self._generate_coords()
        self._compute_distances()
        self._compute_maxmin()

    def _compute_distances(self):
        raise NotImplementedError

    def _compute_maxmin(self):
        if self.num_dims == 1:
            self.min_coord = min(self.coords)
            self.max_coord = max(self.coords)

    def get_distance_matrix(self):
        return self.distance_matrix.copy()

    def label(self,aa):
        return self.labels[aa]
                

class RingAminoAcidSpace (_AminoAcidSpace):
    """
    Ring amino acid spaces model amino acid (dis)similarities in a one-dimensional circular physicochemical amino acid space

    >>> aa = RingAminoAcidSpace(num_aas = 5)
    >>> map(lambda x: x.round(3),aa.coords)
    [array([[ 0.156]]), array([[ 0.375]]), array([[ 0.599]]), array([[ 0.732]]), array([[ 0.951]])]
    >>> dm = aa.get_distance_matrix()
    >>> dm.round(3)
    array([[ 0.   ,  0.219,  0.443,  0.424,  0.205],
           [ 0.219,  0.   ,  0.224,  0.357,  0.424],
           [ 0.443,  0.224,  0.   ,  0.133,  0.352],
           [ 0.424,  0.357,  0.133,  0.   ,  0.219],
           [ 0.205,  0.424,  0.352,  0.219,  0.   ]])

    """
    def __init__(self, num_aas = None, seed = 42, coords = None, labels = None):
        _AminoAcidSpace.__init__(self, num_aas, coords, labels, num_dims = 1, seed = seed)


    def _compute_distances(self):
        na = self.num_aas
        self.distance_matrix = numpy.zeros((na,na))
        for alpha in range(0,na):
            for beta in range(alpha,na):
                ca = self.coords[alpha]
                cb = self.coords[beta]
                self.distance_matrix[alpha][beta] = self.distance_matrix[beta][alpha] = min ( abs(ca - cb), (1 - abs(ca - cb)) )

        
        
class RegionAminoAcidSpace (_AminoAcidSpace):
    """
    Region amino acid spaces model amino acid (dis)similarities in bounded regions of a finite number of dimensions.

    >>> aa = RegionAminoAcidSpace(num_aas = 5,num_dims = 2)
    >>> map(lambda x:x.round(2),aa.coords)
    [array([[ 0.16,  0.71]]), array([[ 0.37,  0.16]]), array([[ 0.6,  0.6]]), array([[ 0.73,  0.87]]), array([[ 0.95,  0.06]])]
    >>> dm =  aa.get_distance_matrix()
    >>> dm.round(3)
    array([[ 0.   ,  0.594,  0.455,  0.597,  1.027],
           [ 0.594,  0.   ,  0.498,  0.795,  0.584],
           [ 0.455,  0.498,  0.   ,  0.297,  0.647],
           [ 0.597,  0.795,  0.297,  0.   ,  0.837],
           [ 1.027,  0.584,  0.647,  0.837,  0.   ]])
    """
    def __init__(self, num_aas = None, coords = None, num_dims = 1, seed = 42, labels = None):
        _AminoAcidSpace.__init__(self, num_aas, coords, labels, num_dims, seed = seed)


    def _compute_distances(self):
        na = self.num_aas
        self.distance_matrix = numpy.zeros((na,na))
        for alpha in range(0,na):
            for beta in range(alpha,na):
                ca = numpy.array(self.coords[alpha])
                cb = numpy.array(self.coords[beta] )
                self.distance_matrix[alpha][beta] = self.distance_matrix[beta][alpha] = numpy.linalg.norm(ca - cb)      


if __name__ == "__main__":
    import doctest
    doctest.testmod()
