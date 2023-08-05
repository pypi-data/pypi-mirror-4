import numpy
import copy

class GeneticCodeMutation():
    def __init__(self, code, codon, aa):
        self.code_matrix = code.get_code_matrix()
        self.code_matrix[codon,:] = 0
        self.code_matrix[codon][aa] = 1
        if code.misreading:
            misreading_matrix = code.misreading.get_misreading_matrix()
            self.effective_code_matrix = numpy.dot(self.code_matrix, misreading_matrix)
        else:
            self.effective_code_matrix = self.code_matrix
        self.event = {codon: aa}
        self.codon = codon
        self.amino_acid = aa

    def get_effective_code_matrix(self):
        return self.effective_code_matrix.copy()

class _GeneticCode():
    """
    This private base class  
    """
    def __init__(self, codons, amino_acids, misreading):
        self.codons = codons
        self.num_codons = codons.num_codons
        self.amino_acids = amino_acids
        self.num_amino_acids = amino_acids.num_amino_acids
        self.misreading = misreading
        self.mutation_history = []
        self.num_mutations = 0
        self.num_mutations_by_codon = [0] * self.num_codons
        self.redundancy = [0] * self.num_amino_acids
        self.initial_code_as_dict = {}
        self.current_code_as_dict = {}
        self.codon_set      = set(range(self.num_codons))
        self.amino_acid_set = set(range(self.num_amino_acids))
        self.explicit_codons = set()
        self.encoded_amino_acids = set()
        self.reassignments_before_explicit = 0
        self.reassignments_after_explicit  = 0
        
        
    def get_code_matrix(self):    
        return self.code_matrix.copy()

    def get_effective_code_matrix(self):    
        if self.misreading:
            misreading_matrix = self.misreading.get_misreading_matrix()
            ## this mirrors what brian did, but needs to be checked.
            return numpy.dot(self.code_matrix,misreading_matrix)
        else:
            return self.code_matrix.copy()

    def mutate(self, codon, aa):
        return GeneticCodeMutation(self,codon,aa)

    def update(self, code_mutation):
        self.code_matrix = code_mutation.code_matrix
        self.mutation_history.append(code_mutation.event)
        self.num_mutations += 1
        self.num_mutations_by_codon[code_mutation.codon] += 1

        old_encoded_amino_acid = None
        if (code_mutation.codon in self.explicit_codons):
             old_encoded_amino_acid = self.current_code_as_dict[code_mutation.codon]

        self.current_code_as_dict.update(code_mutation.event)

        if self.is_explicit():
            self.reassignments_after_explicit += 1
        elif self.is_explicit(code_mutation.codon):
            self.reassignments_before_explicit += 1 

        if old_encoded_amino_acid:
            self.redundancy[old_encoded_amino_acid] -= 1
            if self.redundancy[old_encoded_amino_acid] == 0:
                self.encoded_amino_acids.discard(old_encoded_amino_acid)

        self.redundancy[code_mutation.amino_acid] += 1

        self.explicit_codons.add(code_mutation.codon)
        self.encoded_amino_acids.add(code_mutation.amino_acid)

    def as_dict(self):
        return self.current_code_as_dict.copy()

    def as_labelled_dict(self):
        current = self.current_code_as_dict.copy()
        for codon in self.explicit_codons:
            current[codon] = self.amino_acids.label(current[codon])
        return current

    def num_ambiguous_codons(self):
        return self.num_codons - len(self.explicit_codons)

    def num_explicit_codons(self):
        return len(self.explicit_codons)

    def num_reassignments(self, codon = None):
        if codon and self.is_explicit(codon):
            return self.num_mutations_by_codon[codon] - 1
        elif codon:
            return 0
        else:
            return self.reassignments_before_explicit + self.reassignments_after_explicit

    def num_reassignments_before_explicit(self):
        return self.reassignments_before_explicit            

    def num_reassignments_after_explicit(self, codon = None):
        return self.reassignments_after_explicit

    def num_encoded_amino_acids(self):
        return len(self.encoded_amino_acids)

    def num_unencoded_amino_acids(self):
        return self.num_amino_acids - len(self.encoded_amino_acids)

    def redundancy(self,amino_acid = None):
        if amino_acid:
            return self.redundancy[amino_acid]
        else:
            return (1 - ((self.num_encoded_amino_acids - 1) / (self.num_codons - 1)))

    def normalized_encoded_range(self):
        if self.amino_acids.__class__.__name__ == 'RingAminoAcidSpace':
            return 'NA'
        if self.amino_acids.num_dims != 1:
            return 'NA'
        mc = self.amino_acids.min_coord
        Mc = self.amino_acids.max_coord
        coords = self.amino_acids.coords
        m = min(map (lambda(x):coords[x],self.encoded_amino_acids))
        M = max(map (lambda(x):coords[x],self.encoded_amino_acids))
        return numpy.asscalar((M - m)/(Mc - mc))

    ## def get_reassignments(self,codon):
    ##     pass

    def is_ambiguous(self,codon = None):
        if codon:
            return (codon not in self.explicit_codons)
        else:
            return (len(self.explicit_codons) == 0)
        
    def is_explicit(self,codon = None):
        if codon:
            return (codon in self.explicit_codons)
        else:
            return (self.codon_set == self.explicit_codons)

    def ambiguous_codons(self):
        return (self.codon_set - self.explicit_codons)

    def unencoded_amino_acids(self):
        return (self.amino_acid_set - self.encoded_amino_acids)

    def is_encoded(self,amino_acid):
        return (amino_acid in self.encoded_amino_acids)
        
    def is_unencoded(self,amino_acid):
        return (amino_acid not in self.encoded_amino_acids)

    def encodes(self, codon, aa):
        return (self.code_matrix[codon][aa] == 1)

    def __str__(self):
        return self.codons.__str__(self.as_labelled_dict())

class InitiallyAmbiguousGeneticCode(_GeneticCode):
    def __init__(self, codons, amino_acids, misreading = None):
        _GeneticCode.__init__(self, codons, amino_acids, misreading)
        nc = codons.num_codons
        na = amino_acids.num_aas
        self.code_matrix = numpy.ones((nc,na)) / na
        for c in xrange(nc):
            self.initial_code_as_dict[c] = '*'
        self.current_code_as_dict = self.initial_code_as_dict.copy()
        self.explicit_codons      = set()
        self.encoded_amino_acids   = set()    
        

class UserInitializedGeneticCode(_GeneticCode):
    """
    User-Initialized Genetic Codes are initialized with a numpy.ndarray code matrix
    or a dict of codons mapping to indices (not labels) of amino acids
    

    >>> codons = codon_spaces.WordCodonSpace(num_bases = 4,num_positions = 2, mu = 0.2,kappa = 2)
    >>> aas    = amino_acid_spaces.RegionAminoAcidSpace(num_aas = 20, seed = 40)
    >>> cm = numpy.eye(16)
    >>> cm = numpy.hstack((cm,numpy.zeros((16,4))))
    >>> cm.shape
    (16, 20)
    >>> cm[0][1] = 1
    >>> cm /= cm.sum(axis = 1).reshape(16,1)
    >>> gc = UserInitializedGeneticCode(codons,aas,code_matrix = cm)
    >>> gc.num_codons
    16
    >>> gc.num_amino_acids
    20
    >>> gc.ambiguous_codons()
    set([0])
    >>> gc.encoded_aas
    set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    >>> print gc
    |* b c d|
    |e f g h|
    |i j k l|
    |m n o p|
    >>> gc.as_labelled_dict()
    {0: '*', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p'}
    >>> gc.as_dict()
    {0: '*', 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    >>> gc2 = UserInitializedGeneticCode(codons,aas,code_dict = {0: '*', 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15})
    >>> print gc2
    |* b c d|
    |e f g h|
    |i j k l|
    |m n o p|
    >>> print gc2.code_matrix[0]
    [ 0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05
      0.05  0.05  0.05  0.05  0.05  0.05  0.05  0.05]
    """
    def __init__(self, codons, amino_acids, code_matrix = None, code_dict = None, misreading = None):
        _GeneticCode.__init__(self, codons, amino_acids, misreading)
        nc = codons.num_codons
        na = amino_acids.num_aas
        ## check that the passed-in code matrix size fits the aa and codon spaces passed in
        ## accept dictionaries and code matrices
        ## make sure codon vectors add to one
        if not code_matrix == None:
            self.code_matrix = numpy.empty((nc,na))
            self.code_matrix = code_matrix
        ## set _initial_code accordingly
            (explicit_codons,encoded_aas) = numpy.nonzero(code_matrix == 1)
            self.explicit_codons      = set(explicit_codons)
            self.encoded_aas          = set(encoded_aas)
            self.initial_code_as_dict = dict(zip(explicit_codons,encoded_aas))
            for c in self.ambiguous_codons():
                self.initial_code_as_dict[c] = '*'
        elif code_dict:
            self.code_matrix = numpy.zeros((nc,na))
            for (codon, aa) in code_dict.items():
                if aa == '*':
                    self.code_matrix[codon] = numpy.ones((1,na)) / na
                else:
                    self.code_matrix[codon][aa] = 1
                    self.explicit_codons.add(codon)
                    self.encoded_amino_acids.add(aa)
            self.initial_code_as_dict = code_dict.copy()       
        self.current_code_as_dict = self.initial_code_as_dict.copy()


if __name__ == "__main__":
    import doctest
    import amino_acid_spaces
    import codon_spaces
    import numpy
    doctest.testmod()
