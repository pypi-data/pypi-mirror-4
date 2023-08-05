"""
Site-type fitness matrices are intended as site-types over rows and amino acids over columns
"""

import numpy

class MirroringSiteTypeSpace():
    """
    This class models site-types in one-to-one correspondence with amino acids as according to the published models of Ardell and Sella.  

    >>> aa = amino_acid_spaces.RingAminoAcidSpace(num_aas = 5)
    >>> dm = aa.get_distance_matrix()
    >>> dm.round(3)
    array([[ 0.   ,  0.219,  0.443,  0.424,  0.205],
           [ 0.219,  0.   ,  0.224,  0.357,  0.424],
           [ 0.443,  0.224,  0.   ,  0.133,  0.352],
           [ 0.424,  0.357,  0.133,  0.   ,  0.219],
           [ 0.205,  0.424,  0.352,  0.219,  0.   ]])
    >>> st = MirroringSiteTypeSpace(aa,phi = 0.96)
    >>> fm = st.get_fitness_matrix()
    >>> fm.round(3)
    array([[ 1.   ,  0.991,  0.982,  0.983,  0.992],
           [ 0.991,  1.   ,  0.991,  0.986,  0.983],
           [ 0.982,  0.991,  1.   ,  0.995,  0.986],
           [ 0.983,  0.986,  0.995,  1.   ,  0.991],
           [ 0.992,  0.983,  0.986,  0.991,  1.   ]])

    """
    def __init__(self, amino_acids, phi, weights = None):
        self.phi = phi
        self.aas = amino_acids
        ## weights not implemented yet
        self.num_site_types = amino_acids.num_aas
        self.num_aas = amino_acids.num_aas
        self.fitness_matrix = phi ** amino_acids.get_distance_matrix()
        if weights:
            self.site_type_weights = numpy.fromiter(weights,numpy.float)
        else:
            self.site_type_weights = numpy.ones(self.num_site_types)

    def get_fitness_matrix(self):
        return self.fitness_matrix.copy()

    def get_site_type_weights(self):
        return self.site_type_weights.copy()
        

if __name__ == "__main__":
    import doctest
    import amino_acid_spaces
    doctest.testmod()
