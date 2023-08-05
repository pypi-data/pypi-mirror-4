from optparse import OptionParser, OptionValueError
from types import FloatType
import cmcpy
import pdb
import time
import sys
import multiprocessing
import numpy

def main():
    starttime = time.time()
    if 1 == 1:
        version = 0.1
        prog = 'cmc'
        usage = '''usage: %prog [options]

    Examples:
    %prog -t 10 -b 4 -p 2 -k 9 -m 0.001 -f 0.5 --precision 5 --show-all --show-frozen-results-only | grep -v #
    '''
        parser = OptionParser(usage=usage,version="%prog $version")
        parser.disable_interspersed_args()
        demo_choices = ['ArdellSella01Fig1','ArdellSella01Fig4','ArdellSella01Fig6','SellaArdell02Fig3','ArdellSella02Fig2','ArdellSella02Fig5','SellaArdell06Fig4']
        parser.add_option("--demo", dest="demo", type="choice",
                          choices=demo_choices, default=None,
                          help="run preset simulations by name. Choose from %s" % demo_choices)

        method_choices = ['numpy','power','cuda','powermulticore'] #,'perturbative']

        parser.add_option("--method", dest="method", type="choice",
                          choices=method_choices, default='numpy',
                          help="eigensystem solver method. Choose from %s" % method_choices)

        parser.add_option("-m","--mu",
                          dest="mu", type="float", default=0.1,
                          help="set base or codon (ring model) mutation rate.\n Default: %default")
        parser.add_option("-k","--kappa",
                          dest="kappa", type="float", default=1.0,
                          help="set transition/transversion ratio.\n Default: %default")
        parser.add_option("-f","--phi",
                          dest="phi", type="float", default=0.25,
                          help="set missense tolerance parameter.\n Default: %default")

        parser.add_option("-s","--seed", 
                          dest="seed", type="int",  default=42,
                          help="seed random number generator for amino acid coords. Default: %default")
        parser.add_option("-a","--na","--numaas",
                          dest="na", type="int", default=10,
                          help="set number of amino-acids/site-types. Default: %default")
        parser.add_option("-d","--nd","--numdims",
                          dest="nd", type="int",default=1,
                          help="set dimension of amino-acid/site-type space (not used in double-ring models). Default: %default")

        parser.add_option("-t","--nt", "--numtrials",
                          dest="num_trials", type="int",  default=1,
                          help="set number of simulation trials, each with a different amino-acid/site-type space. Default: %default")

        parser.add_option("-c","--nc","--numcodons",  
                          dest="nc", type="int", default=None,
                          help="set number of codons and execute a \"double ring\" model. Default: %default")

        parser.add_option("-b","--nb","--numbases",
                          dest="nb", type="int",default=4,
                          help="set alphabet size for a word-based codon model. Default: %default")

        parser.add_option("-p","--np","--numpositions",
                          dest="np", type="int",default=None,
                          help="set number of positions for a word-based codon model. Default: %default")

        parser.add_option("--numprocesses",
                          dest="num_processes", type="int", default=8,
                          help="set number of processes for multicore applications. Default: %default")

        parser.add_option("--delta",
                          dest="delta", type="float",  default=10**(-32),
                          help="set eigenvalue convergence threshold for the power-method-based evolver. Default: %default")

        parser.add_option("--epsilon",
                          dest="epsilon", type="float",  default=10**(-12),
                          help="set error tolerance for comparison of mutant fitnesses. Default: %default")

        parser.add_option("--maxord",
                          dest="maxord", type="int",  default=5,
                          help="set maximum order for pertubative approximation to eigensystems using the perturbative method. Default: %default")

        def set_misreading_parameters(option, opt, value, parser):
            assert value is None
            value = []

            def floatable(str):
                try:
                    float(str)
                    return True
                except ValueError:
                    return False

            if parser.values.nc:
                na = 1
            elif not parser.values.np:
                raise OptionValueError("must set either number of positions (with e.g. --np) or number of codons (with --nc) before setting misreading parameters")
            else:
                na = parser.values.np

            for arg in parser.rargs[0:na]:
                if floatable(arg) and arg > 0:
                    value.append(arg)
                else:
                    raise OptionValueError("misreading option (e.g. --mr) requires 1 or more positive float arguments (same as number of positions or 1 for ring models)")

            del parser.rargs[:na]
            setattr(parser.values, option.dest, value)


        parser.add_option("-r","--mr","--misreading", dest="misreading", default=None, 
                          action="callback", callback=set_misreading_parameters,
                          help="set misreading parameters. Must be set after setting #codons (with -c/-nc for ring model) or #positions (with -p/-np). Takes one (ring model) or #positions positive float arguments.")

        parser.set_defaults(show_codes=True,show_messages=False,show_initial_parameters = True, show_matrix_parameters = False,show_fitness_statistics = False, show_code_evolution_statistics = False, show_frozen_results_only = False)
        parser.add_option("--no-show-initial-params", action="store_false", dest="show_initial_parameters", help="turn off printing of initial simulation scalar parameters.")
        parser.add_option("--no-show-codes", action="store_false", dest="show_codes", help="turn off printing of the evolutionary trajectory of genetic codes.")
        parser.add_option("--show-messages", action="store_true", dest="show_messages", help="turn on printing of the evolutionary trajectory of equilibrium message/codon usage frequencies.")
        parser.add_option("--show-matrix-params", action="store_true", dest="show_matrix_parameters", help="turn on printing of initial simulation matrix parameters.")
        parser.add_option("--precision",
                          dest="precision", type="int",  default=4,
                          help="set print precision for parameter printing. Default: %default")

        parser.add_option("--show-fitness-stats", action="store_true", dest="show_fitness_statistics", help="turn on printing of the evolutionary trajectory of fitness statistics.")
        parser.add_option("--show-code-evol-stats", action="store_true", dest="show_code_evolution_statistics", help="turn on printing of the evolutionary trajectory of code evolution statistics.")
        parser.add_option("--show-all", action="store_true", dest="show_all", help="show all statistics except messages")
        parser.add_option("--show-frozen-results-only", action="store_true", dest="show_frozen_results_only", help="only show statistics for final frozen codes (useful for multiple trials).")

        myargv = sys.argv
        (options, args) = parser.parse_args()
        if len(args) != 0:
            parser.error("expects zero arguments")

        print '# {:<3s} version {:3.1f}'.format(prog,version)
        print '# Copyleft (2012) David H. Ardell.'
        print '# All Wrongs Reversed.'
        print '#'
        print '# please cite ...'
        print '#'
        print '# execution command:'
        print '# '+' '.join(myargv)

        observables = cmcpy.observables.Observables(show_codes                     = options.show_codes,
                                                    show_messages                  = options.show_messages,
                                                    show_initial_parameters        = options.show_initial_parameters,
                                                    show_matrix_parameters         = options.show_matrix_parameters,
                                                    show_fitness_statistics        = options.show_fitness_statistics,
                                                    show_code_evolution_statistics = options.show_code_evolution_statistics,
                                                    show_frozen_results_only       = options.show_frozen_results_only,
                                                    show_all                       = options.show_all,
                                                    print_precision                = options.precision)

        ## SELECT CLASS OF EIGENSYSTEM SOLVER IN evolvers.py BASED ON options.method
        class_dictionary = {'numpy':'ArdellSellaEvolverNumpy','multicore':'ArdellSellaEvolverNumpyMulticore','power':'ArdellSellaEvolverPowerMethod','powermulti':'ArdellSellaEvolverPowerMulticore','cuda':'ArdellSellaEvolverPowerCUDA','perturbative':'ArdellSellaEvolverPerturbative'}
        evolverClass = getattr(cmcpy.evolvers, class_dictionary[options.method])

        if options.demo :
            print "# N.B. Results differ trivially from those published because of differences in machine precision and amino acid coordinates.\n" 
            if options.demo == 'ArdellSella01Fig1':
                phi = 0.8
                mu  = 0.0001
                codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = 4, num_positions = 2, mu            = mu)
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(coords = [0.0085,0.0086,0.0886,0.0988,0.1005,0.1363,0.2879,0.3254,0.3424,0.3425,0.3816,0.3817,0.4497,0.5213,0.5963,0.6048,0.7513,0.8637,0.9608,0.9659])
                site_types =  cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                evolver      = evolverClass(initial_code = initial_code, 
                                            site_types   = site_types, 
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon      = options.epsilon,
                                            max_order    = options.maxord,
                                            observables  = observables)

                print "phi: {} mu: {}\n".format(phi,mu)
                print "amino-acid/site-type space: "+str(aas.coords)+"\n"
                evolver.evolve_until_frozen()

            elif options.demo == 'ArdellSella01Fig4':
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(coords = [0.0085,0.0086,0.0886,0.0988,0.1005,0.1363,0.2879,0.3254,0.3424,0.3425,0.3816,0.3817,0.4497,0.5213,0.5963,0.6048,0.7513,0.8637,0.9608,0.9659])
                print "amino-acid/site-type space: "+str(aas.coords)+"\n"
                observables.show_codes = False
                for phi in (0.92, 0.94, 0.99) :
                    for mu in (0.001, 0.005, 0.009) :
                        print "phi: {} mu: {}\n".format(phi,mu)
                        codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = 4, num_positions = 2, mu            = mu)
                        site_types =  cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                        initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                        evolver      = evolverClass(initial_code = initial_code, 
                                            site_types   = site_types, 
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon      = options.epsilon,                                                
                                            observables  = observables)
                        evolver.evolve_until_frozen()
                        print str(evolver.code)+"\n\n"
                    print "\n"

            elif options.demo == 'ArdellSella01Fig6':
                phi = 0.9985
                mu  = 0.0001
                codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = 4, num_positions = 2, mu            = mu)
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(coords = [0.0085,0.0086,0.0886,0.0988,0.1005,0.1363,0.2879,0.3254,0.3424,0.3425,0.3816,0.3817,0.4497,0.5213,0.5963,0.6048,0.7513,0.8637,0.9608,0.9659])
                site_types =  cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                evolver      = evolverClass(initial_code = initial_code, 
                                            site_types   = site_types, 
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon      = options.epsilon,                                        
                                            observables  = observables)

                print "phi: {} mu: {}\n".format(phi,mu)
                print "amino-acid/site-type space: "+str(aas.coords)+"\n"
                print "labels: "+str(aas.labels)+"\n"
                evolver.evolve_until_frozen()

            elif options.demo == 'SellaArdell02Fig3':
                codons       = cmcpy.codon_spaces.RingCodonSpace(num_codons = 5, mu = 0.01)
                aas          = cmcpy.amino_acid_spaces.RingAminoAcidSpace(coords = [0,0.2,0.4,0.6,0.8])
                site_types   = cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = 0.32768, weights = [20,20,20,20,20])
                codeA        = cmcpy.genetic_codes.UserInitializedGeneticCode(codons = codons,amino_acids = aas, code_dict = dict(zip(range(5),range(5))))
                codeB        = cmcpy.genetic_codes.UserInitializedGeneticCode(codons = codons,amino_acids = aas, code_dict = dict(zip(range(5),[0,3,1,4,2])))
                evolverA     = evolverClass(initial_code = codeA, site_types = site_types, num_processes = options.num_processes, delta = options.delta, epsilon = options.epsilon, observables = observables)
                evolverB     = evolverClass(initial_code = codeB, site_types = site_types, num_processes = options.num_processes, delta = options.delta, epsilon = options.epsilon, observables = observables)
                print "mu : 0.01"
                print "phi: 0.32768 = (0.8 ** 5), not 0.8 as reported in Sella and Ardell (2002)"
                print "weights: [20,20,20,20,20]\n"

                print "code A:\n",codeA 
                print "growth rate (lambda): ",evolverA.growth_rate()
                print "usage matrix:"
                print evolverA.messages()

                print "\ncode B:\n",codeB  
                print "growth rate (lambda): ",evolverB.growth_rate()
                print "usage matrix:"
                print evolverB.messages() 
            elif options.demo == 'ArdellSella02Fig2':
                phi = 0.92
                mu  = 0.0006
                kappa = 7
                codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = 4, num_positions = 2, mu            = mu, kappa = kappa)
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(coords = [0.04,0.12,0.123515,0.19,0.29,0.33,0.355,0.42,0.455,0.515184,0.563178,0.58,0.589559,0.668897,0.670356,0.75,0.767591,0.815486,0.943856,0.944])
                site_types =  cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                evolver      = evolverClass(initial_code = initial_code, 
                                            site_types   = site_types, 
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon      = options.epsilon,
                                            observables  = observables)

                print "phi: {} mu: {} kappa: {}\n".format(phi,mu, kappa)
                print "amino-acid/site-type space: "+str(aas.coords)+"\n"
                print "labels: "+str(aas.labels)+"\n"
                evolver.evolve_until_frozen()

            elif options.demo == 'ArdellSella02Fig5':
                phi = 0.92
                mu  = 0.0006
                mr  = [0.0006,0]
                codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = 4, num_positions = 2, mu            = mu)
                misreading = cmcpy.misreading.PositionalMisreading(codons, mr)
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(coords = [0.04,0.12,0.123515,0.19,0.29,0.33,0.355,0.42,0.455,0.515184,0.563178,0.58,0.589559,0.668897,0.670356,0.75,0.767591,0.815486,0.943856,0.944])
                site_types =  cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                evolver      = evolverClass(initial_code = initial_code, 
                                            site_types   = site_types, 
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon      = options.epsilon,
                                            observables  = observables)

                print "phi: {} mu: {}".format(phi,mu)+ " misreading: "+str(mr)+"\n"
                print "amino-acid/site-type space: "+str(aas.coords)+"\n"
                print "labels: "+str(aas.labels)+"\n"
                evolver.evolve_until_frozen()


            elif options.demo == 'SellaArdell06Fig4':			
                codons       = cmcpy.codon_spaces.RingCodonSpace(num_codons = 8, mu = 0.02)
                aas          = cmcpy.amino_acid_spaces.RingAminoAcidSpace(coords = [0.05,0.15,0.24,0.41,0.44,0.51,0.54,0.79,0.83,0.92])
                site_types   = cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = 0.25)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons = codons,amino_acids = aas)
                print "Setting delta = 1e-16\n"
                evolver      = evolverClass(initial_code = initial_code, site_types = site_types, num_processes = options.num_processes,  delta = 1e-16, epsilon = options.epsilon, observables = observables)
                evolver.evolve_until_frozen()

        else:   # run a user-defined simulation 

            if options.nc : # a ring model is requested
                ring = True # used to initialize an aa ring model below
                nc = options.nc
                mu = options.mu
                codons = cmcpy.codon_spaces.RingCodonSpace(num_codons = nc, mu = mu)

            elif not options.np :
                sys.exit("select a demo or set number of codons (for ring model) or number of positions (for word model). Try --help for help.")

            else :    
                ring = False
                nb = options.nb
                np = options.np
                mu = options.mu
                kappa = options.kappa
                codons = cmcpy.codon_spaces.WordCodonSpace(num_bases     = nb,
                                                           num_positions = np,
                                                           mu            = mu,
                                                           kappa         = kappa)

            num_trials = options.num_trials
            na   = options.na
            nd   = options.nd
            seed = options.seed
            phi  = options.phi
            misreading = None

            if ring:
                aas    = cmcpy.amino_acid_spaces.RingAminoAcidSpace(num_aas = na, seed = seed)
                if options.misreading:
                    misreading = cmcpy.misreading.RingMisreading(codons = codons, misreading = options.misreading)

            else:
                aas    = cmcpy.amino_acid_spaces.RegionAminoAcidSpace(num_aas = na, num_dims = nd, seed = seed)
                if options.misreading:
                    misreading = cmcpy.misreading.PositionalMisreading(codons = codons, misreading = options.misreading)

            for trial in xrange(num_trials):
                print "# coords:"+str((aas.coords))
                site_types   = cmcpy.site_type_spaces.MirroringSiteTypeSpace(amino_acids = aas, phi = phi)
                initial_code = cmcpy.genetic_codes.InitiallyAmbiguousGeneticCode(codons      = codons,
                                                                                 amino_acids = aas,
                                                                                 misreading  = misreading)    
                evolver      = evolverClass(initial_code = initial_code,
                                            site_types   = site_types,
                                            num_processes  = options.num_processes,
                                            delta        = options.delta,
                                            epsilon = options.epsilon,
                                            observables  = observables)

                evolver.evolve_until_frozen()
                aas.reinitialize()

    print "# Run time (minutes): ",round((time.time()-starttime)/60,3)

