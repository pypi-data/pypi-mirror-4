"""
#########################################################################
evolvers -- cmcpy module for abstract base class of Ardell Sella Evolvers
#########################################################################
"""
import numpy
import math
import os
import time
import abc # requires python 2.6
import copy
import multiprocessing
import sys
try:                                                                                                 
        import pycuda.driver as cuda                                       
        import pycuda.autoinit                                                   
        from pycuda.compiler import SourceModule            
except:
        pass 

class ArdellSellaEvolverAbstractBase(object):
	"""
	Abstract Base Class for ArdellSellaEvolvers for Code-Message Coevolution corresponding to models published in Ardell and Sella (2001, 2002) and Sella and Ardell (2002, 2006).
	Concrete Implementations subclass from this for different implementations of Eigenvalue solutions.
	"""
	__metaclass__ = abc.ABCMeta
	def __init__(self, initial_code, site_types, delta, epsilon, observables):
		self.code = initial_code
		self.codons = initial_code.codons
		self.site_types = site_types
		self.aas = site_types.aas
		self.num_codons = self.codons.num_codons
		self.num_aas = site_types.num_aas
		self.num_site_types = site_types.num_site_types
		self.mutation_matrix = self.codons.get_mutation_matrix()   ## THIS COMMITS THIS EVOLVER TO STATIC MUTATION
		self.fitness_matrix = site_types.get_fitness_matrix() ## THIS COMMITS THIS EVOLVER TO STATIC FITNESS
		self.delta = delta
		self.epsilon = epsilon
		self.eigenmatrix = numpy.ones((self.num_site_types,self.num_codons)) #.astype(numpy.float32)
		self.eigenvalues = numpy.ones(self.num_site_types)
		self.observables = observables
		self.num_fitter_code_mutants = 0
		self.max_mutant_fitness = 0		
		self.frozen = False
		self.initial_equilibrate_messages()
		self.equilibrated = True
		self._growth_rate_computed = False
		self.print_initial_observables()
		self.print_observables_header()

        
	def get_mutation_selection_matrix(self,alpha):
		mutation = self.mutation_matrix
		code = self.code.get_effective_code_matrix()
		fitness = self.fitness_matrix
		return numpy.dot(mutation, numpy.diag(numpy.dot(code,fitness[alpha])))

	def get_selection_matrix(self,alpha):
		mutation = self.mutation_matrix
		code = self.code.get_effective_code_matrix()
		fitness = self.fitness_matrix
		return numpy.diag(numpy.dot(code,fitness[alpha]))
	
	def get_eigenvalue( self, msm, eigenvec):
		top = numpy.dot(msm,eigenvec) * eigenvec
		bot = eigenvec * eigenvec
		lamda = top.sum() / bot.sum()
		return lamda


	@abc.abstractmethod
	def equilibrate_messages(self):
		'''Compute eigensystems in site-types for an established genetic code.
			
		This finds eigensystems (codon frequencies and growth rates)
		for different site-types given the genetic code. 
			
		Abstract method: subclasses must:

		1) store their results by setting self.eigenvalues and
		self.eigenmatrix

		2) set self.equilibrated to True

		3) call super(<<SubClass>>, self).equilibrate_messages()
		to print observables at end of subclass method where
		<<SubClass>> is the subclass name to print observables.
		'''
		
		pass
	
	def initial_equilibrate_messages(self):
		'''Compute eigensystems in site-types for an established genetic code.
		
		This finds eigensystems (codon frequencies and growth rates)
		for different site-types given the genetic code. 
		'''

		if self.code.is_ambiguous():
			self.eigenmatrix = numpy.ones((self.num_site_types,self.num_codons)) / self.num_codons
			msm = self.get_mutation_selection_matrix(0)
			lamda = self.get_eigenvalue(msm,self.eigenmatrix[0])
			self.eigenvalues = numpy.ones((self.num_site_types,1)) * lamda
			self.equilibrated = True
		else:
			self.equilibrate_messages()
        
	def growth_rate_from_lambda(self):
		if (not(self.equilibrated)) :
			self.equilibrate_messages()
		gr = 1.0
		site_weight = self.site_types.get_site_type_weights()
		for alpha in xrange(self.num_site_types):
			gr *= self.eigenvalues[alpha] ** site_weight[alpha]
		return gr[0]

	def growth_rate(self):
		'''
        
		'''
		if (not(self.equilibrated)):
			self.equilibrate_messages()
		if (self._growth_rate_computed):
			return self._growth_rate
		else:
			self._growth_rate = self.compute_code_fitness_given_messages(self.messages(), self.code.get_effective_code_matrix())
			self._growth_rate_computed = True
			return self._growth_rate

	def messages(self):
		'''
        
		'''
		if (not(self.equilibrated)):
			self.equilibrate_messages()
		return self.eigenmatrix.copy()
		
	def compute_code_fitness_given_messages(self, equilibrated_messages, effective_code_matrix):
		'''

		Implement eg eqns. 2-7 from Sella and Ardell(2006)
		'''
		nc = self.num_codons
		na = self.num_aas
		ns = self.num_site_types

		site_weight = self.site_types.get_site_type_weights()
		u = usage  = equilibrated_messages ## assumed here to be ns x nc
		c = code   = effective_code_matrix ## assumed here to be nc x na
		w = fitness_coef  = self.fitness_matrix   ## assumed here to be ns x na **THIS IS CRITICAL FOR NEW SITE-TYPE SPACE DEFINITIONS**
		## solution number one:
		fit1 = numpy.prod(numpy.sum(u.repeat(na,axis=1) * numpy.tile(c.ravel(),(ns,1)) * numpy.tile(w,(1,nc)),axis=1)** site_weight)
		return fit1
		## ## solution number four:
		## pdb.set_trace()
		## fitness = 1.0
		## for alpha in xrange(ns):
		##     fitness_per_site_type = 0.0
		##     for codon in xrange(nc):
		##         #                fitness_per_codon_per_site_type = 0.0
		##         for aa in xrange (na):
		##             #                    fitness_per_codon_per_site_type += code[codon][aa] * fitness_coef[alpha][aa]
		##             #fitness_per_site_type += fitness_per_codon_per_site_type * usage[alpha][codon]
		##             fitness_per_site_type  += code[codon][aa] * fitness_coef[alpha][aa] * usage[alpha][codon]
		##     fitness *=  fitness_per_site_type ** site_weight[alpha]
                ## return fitness

	def compute_max_fitness_code_mutation(self):
		'''
		'''
		if (not(self.equilibrated)):
			self.equilibrate_messages()
		code_mutation = None
		mutation_num = 0
		max_mutant_fitness = 0
		max_mutation_num = 0
		max_fitness_code_mutation = None
		num_fitter_code_mutants = 0
		self.num_fitter_code_mutants = 0
		
		for codon in xrange(self.num_codons):
			for aa in xrange(self.num_aas):
				if self.code.encodes(codon,aa):
					continue
				else:
					code_mutation = self.code.mutate(codon,aa)
					mutant_fitness = self.compute_code_fitness_given_messages(self.messages(), code_mutation.get_effective_code_matrix())

					if (mutant_fitness > self.growth_rate()):
						num_fitter_code_mutants += 1
						if (mutant_fitness > max_mutant_fitness and math.fabs(mutant_fitness - max_mutant_fitness) > self.epsilon):
							max_mutant_fitness = mutant_fitness
							max_fitness_code_mutation = code_mutation

		self.num_fitter_code_mutants =  num_fitter_code_mutants
		return (max_mutant_fitness,max_fitness_code_mutation)

	def evolve_code_unless_frozen(self):
		'''
		Mutate genetic code.
		
		Unless genetic code is frozen, mutate it according to
		the Ardell and Sella models, and update code to most
		fit mutant if it exists. If no more fit mutant
		code exists, set the "frozen" attribute to True.
		
		'''
		if (not(self.frozen)):
			(max_mutant_fitness, max_fitness_code_mutation) = self.compute_max_fitness_code_mutation()
			if (max_mutant_fitness > self.growth_rate()):
				self.code.update(max_fitness_code_mutation)
				self._growth_rate_computed = False
				self.equilibrated = False
				self.max_mutant_fitness = max_mutant_fitness
			else:
				self.frozen = True
                
	def evolve_one_step(self):
		'''
		Mutate genetic code and equilibrate messages.
		
		Unless genetic code is frozen, mutate it according to
		the Ardell and Sella models, update code to most fit
		mutant if it exists, and equilibrate messages to the
		new mutant genetic code. If no more fit mutant code
		exists, set the "frozen" attribute to True.
		'''
		if (not(self.frozen)):
			self.evolve_code_unless_frozen()
			if (not(self.equilibrated)):
				self.equilibrate_messages()
				if not(self.observables.show_frozen_results_only):
					self.print_observables()

            	
	def evolve_until_frozen(self):
		'''
		Iteratively evlove genetic code and messages.
		
		Until genetic code is frozen, mutate it according to
		the Ardell and Sella models, update code to most fit
		mutant if it exists, and equilibrate messages to the
		new mutant genetic code. Once no more fit mutant code
		exists, set the "frozen" attribute to True.
		'''
		while (not(self.frozen)):
			self.evolve_one_step()
		if self.observables.show_frozen_results_only:
			self.print_observables()


	def print_initial_observables(self):
		if (self.observables.show_initial_parameters):
			print '# Delta:{} Epsilon:{}'.format(self.delta,self.epsilon)
		if (self.observables.show_matrix_parameters):
			precision = self.observables.print_precision
			mm = self.codons.get_mutation_matrix()
			print "# Mutation Matrix:\n",mm
			dm = self.aas.get_distance_matrix()
			print "# Distance matrix:\n",dm.round(precision)
			fm = site_types.get_fitness_matrix()
			print "# Fitness matrix:\n",fm.round(precision)
			msm = self.get_mutation_selection_matrix(0)
			print "# Iteration Matrix for site-type 0:\n",msm.round(precision)


	def print_observables_header(self):
		if self.observables.show_code_evolution_statistics or self.observables.show_all:
			print '# RBE = Reassignments Before Explicit'
			print '# RAE = Reassignments After Explicit'
			print '# NAA = Number encoded Amino Acids'
			print '# NER = Normalized Encoded Range (Ardell and Sella, 2001)'
		if self.observables.show_fitness_statistics or self.observables.show_all:
			print '# NFCM = Number Fitter Code Mutants'
			print '# MMF  = Maximum Mutant Fitness'
			print '# GR   = Growth Rate'
			print '# GRFL = Growth Rate from Lambda'
			print '#'
		
		precision = self.observables.print_precision
		width = precision + 8
		print '#{:>{width}s}'.format('STEPS',width=(width-1)),
		if self.observables.show_code_evolution_statistics or self.observables.show_all:
			obs = ['RBE','RAE','NAA','NER']
			print ('{:>{width}s}'*(len(obs))).format(*obs,width=width),
		if self.observables.show_fitness_statistics or self.observables.show_all:
			obs = ['NFCM','MMF','GR','GRFL']
			print ('{:>{width}s}'*(len(obs))).format(*obs,width=width),
		print	      


	def print_observables(self):
		if self.observables.show_codes or self.observables.show_all:
			print '{}'.format(self.code)

		precision = self.observables.print_precision
		width = precision + 8

		print '{:{width}d}'.format(self.code.num_mutations,width=width),

		#if self.observables.show_codes_single_line:
		#	print '{}\t'.format(self.code.as_string),

		if self.observables.show_code_evolution_statistics or self.observables.show_all:
			obs = [self.code.num_reassignments_before_explicit(),self.code.num_reassignments_after_explicit(),self.code.num_encoded_amino_acids()]
			print ('{:>{width}d}'*(len(obs))).format(*obs,width=width),
			ner = self.code.normalized_encoded_range()
			if ner.__class__.__name__ == 'str':
				type = 's'
			else:
				type = 'f'
			print '{:>{width}.{precision}{type}}'.format(self.code.normalized_encoded_range(),width=width-1,precision=precision,type=type),
		if self.observables.show_fitness_statistics or self.observables.show_all:
			print '{:>{width}d}'.format(self.num_fitter_code_mutants,width=width),
			obs = [self.max_mutant_fitness,self.growth_rate(),self.growth_rate_from_lambda()]
			print ('{:>{width}.{precision}f}'*(len(obs))).format(*obs,width=width,precision=precision),
		if self.observables.show_messages:
			print self.messages().round(precision),
		print "\n"

class ArdellSellaEvolverPowerMethod(ArdellSellaEvolverAbstractBase): 
	def __init__(self, initial_code, site_types, num_processes, observables, delta=10**-32, epsilon=10**-12, max_order=5):
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)

	def compute_eigensystem(self, alpha, max_time = 60, numpy_type = numpy.float64):
		msm = self.get_mutation_selection_matrix(alpha).astype(numpy_type)
		eigenvec = numpy.ones(self.num_codons).astype(numpy_type)
		start = time.time()
		error = 1
		while ( ( (time.time() - start) < max_time ) and ( math.fabs(error) > self.delta )):
			eigenvec_old = eigenvec
			eigenvec = numpy.dot( msm, eigenvec_old )
			eigenvec /= eigenvec.sum()
			error = numpy.linalg.norm(eigenvec - eigenvec_old)

		if ( math.fabs(error) > self.delta ):
				print 'Thread time-out occured. Eigenvalue did not converge to specified accuracy %f for site-type %d within time limit.' % (self.delta,alpha)


		self.eigenvalues[alpha] = self.get_eigenvalue(msm,eigenvec)
		self.eigenmatrix[alpha] = eigenvec

	def equilibrate_messages(self):

		for alpha in xrange(self.num_site_types):
			self.compute_eigensystem(alpha)
		self.equilibrated = True
		super(ArdellSellaEvolverPowerMethod, self).equilibrate_messages()

class ArdellSellaEvolverPowerMethodProcessChild(multiprocessing.Process):
	"""
		Finds the eigensystem (message equilibrium and growth rate) for an established genetic code
	"""
	def __init__(self, in_queue, out_queue, num_codons, delta, max_time = 60):
		multiprocessing.Process.__init__(self)
		self.in_queue = in_queue   # holds site type index and (DA: code?) matrix and computeS
		self.out_queue = out_queue # holds site type index leading eigenvalue and corresponding eigenvector
		self.delta = delta         # to what degree of precision user wants to calculate leading eigenvalue
		self.max_time = max_time    # in seconds. Each power fucntion has a time limit default is 1 hour
		self.num_codons = num_codons

	def run(self):
		while True:
			lamda = 987 
			err = self.delta + 1
			alpha, msm  = self.in_queue.get() # alpha indexes the site-type
			eigenvec = numpy.ones(self.num_codons)
			start = time.time()
			convergence = True
			while ( ( (time.time() - start) < self.max_time ) and ( math.fabs(err) > self.delta ) ):
				eigenvec_old = eigenvec
				eigenvec = numpy.dot( msm, eigenvec_old )
				eigenvec /= eigenvec.sum()
				error = numpy.linalg.norm(eigenvec - eigenvec_old)

			if ( math.fabs(error) > self.delta ):
				convergence = False
				# print 'Thread time-out occured. Eigenvalue did not converge to specified accuracy %f for site-type %d within time limit.' % (self.delta,alpha)
			self.out_queue.put((alpha,msm,eigenvec,convergence))
			self.in_queue.task_done()

class ArdellSellaEvolverPowerMulticore (ArdellSellaEvolverAbstractBase): 
	in_queue = multiprocessing.JoinableQueue()
	out_queue = multiprocessing.JoinableQueue()

	def __init__(self, initial_code, site_types, num_processes, observables, delta=10**-32, epsilon=10**-12, num_iterations=1000):
		self.num_processes = num_processes

		for i in range(self.num_processes):
			child = ArdellSellaEvolverPowerMethodProcessChild(ArdellSellaEvolverPowerMulticore.in_queue,ArdellSellaEvolverPowerMulticore.out_queue,self.num_codons,self.delta)
			child.daemon = True
			child.start()
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)
		

	def equilibrate_messages(self):
		for alpha in range(self.num_site_types):
			msm = self.get_mutation_selection_matrix(alpha)
			ArdellSellaEvolverPowerMulticore.in_queue.put((alpha,msm))
		ArdellSellaEvolverPowerMulticore.in_queue.join()
			
		while(not(ArdellSellaEvolverPowerMulticore.out_queue.empty())):
		       	alpha,msm,eigenvec,convergence = ArdellSellaEvolverPowerMulticore.out_queue.get()
		       	if ( not convergence ):
		       		print 'Thread time-out occured. Eigenvalue did not converge to specified accuracy %f for site-type %d within time limit.' % (self.delta,alpha)

			self.eigenvalues[alpha] = self.get_eigenvalue(msm,eigenvec)
		       	self.eigenmatrix[alpha] = eigenvec
				
		self.equilibrated = True
		super(ArdellSellaEvolverPowerMulticore, self).equilibrate_messages()

class ArdellSellaEvolverNumpyProcessChild(multiprocessing.Process):
	"""
		Finds the eigensystem (message equilibrium and growth rate) for an established genetic code
	"""
	def __init__(self, in_queue, out_queue):
		multiprocessing.Process.__init__(self)
		self.in_queue = in_queue   # holds site type index and (DA: code?) matrix and computeS
		self.out_queue = out_queue # holds site type index leading eigenvalue and corresponding eigenvector
		#print "initializing {}".format(self.name)

	def run(self):
		while True:
			#print "running {} and inqueue emptiness is {}".format(self.name,self.in_queue.empty())
			(alpha, msm)  = self.in_queue.get() # alpha indexes the site-type
			#print "processing"
			(eigval,eigmat) = numpy.linalg.eig(msm)
			maxi = numpy.argmax(eigval)
			eigenvec = eigmat[:,maxi]
			eigenvec /= eigenvec.sum()
			eigenval = eigval[maxi]
			self.out_queue.put((alpha,eigenvec,eigenval))
			self.in_queue.task_done()

in_queue = multiprocessing.JoinableQueue()
out_queue = multiprocessing.JoinableQueue()

class ArdellSellaEvolverNumpyMulticore (ArdellSellaEvolverAbstractBase): 


	def __init__(self, initial_code, site_types, num_processes, observables, delta=10**-32, epsilon=10**-12, num_iterations=1000):
		self.num_processes = num_processes
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)


		for i in range(self.num_processes):
			#			child = ArdellSellaEvolverNumpyProcessChild(ArdellSellaEvolverNumpyMulticore.in_queue,ArdellSellaEvolverNumpyMulticore.out_queue)
			child = ArdellSellaEvolverNumpyProcessChild(in_queue,out_queue)
			child.daemon = True
			child.start()
		

	def equilibrate_messages(self):
		for alpha in range(self.num_site_types):
			msm = self.get_mutation_selection_matrix(alpha).astype(numpy.float64)
			in_queue.put((alpha,msm))
			#			ArdellSellaEvolverPowerMulticore.in_queue.put((alpha,msm))

		in_queue.join()
		#		ArdellSellaEvolverNumpyMulticore.in_queue.join()
		#		print "inqueue emptiness is {}".format(ArdellSellaEvolverPowerMulticore.in_queue.empty())
		#print "inqueue emptiness is {}".format(in_queue.empty())

		#		while(not(ArdellSellaEvolverNumpyMulticore.out_queue.empty())):
		while(not(out_queue.empty())):
			#		       	(alpha,eigenvec,eigenval) = ArdellSellaEvolverNumpyMulticore.out_queue.get()
		       	(alpha,eigenvec,eigenval) = out_queue.get()			
			self.eigenvalues[alpha] = eigenval
		       	self.eigenmatrix[alpha] = eigenvec
				
		self.equilibrated = True
		super(ArdellSellaEvolverNumpyMulticore, self).equilibrate_messages()
		

class ArdellSellaEvolverNumpy(ArdellSellaEvolverAbstractBase): 
	def __init__(self, initial_code, site_types, num_processes, observables, delta=10**-32, epsilon=10**-12, num_iterations=1000):
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)

	def compute_eigensystem(self, alpha, max_time = 60, numpy_type = numpy.float64):
		msm = self.get_mutation_selection_matrix(alpha).astype(numpy_type)
		(eigval,eigmat) = numpy.linalg.eig(msm)
		maxi = numpy.argmax(eigval)
		eigenvec = eigmat[:,maxi]
		eigenvec /= eigenvec.sum()
		eigenval = eigval[maxi]

		self.eigenvalues[alpha] = eigenval # self.get_eigenvalue(msm,eigenvec)
		self.eigenmatrix[alpha] = eigenvec

	def equilibrate_messages(self):

		for alpha in xrange(self.num_site_types):
			self.compute_eigensystem(alpha)
		self.equilibrated = True
		super(ArdellSellaEvolverNumpy, self).equilibrate_messages()
		
class ArdellSellaEvolverHomotopy(ArdellSellaEvolverAbstractBase):
	def __init__(self, initial_code, site_types, num_processes, observables, delta=10**-32, epsilon=10**-12, num_iterations=1000):
		self.num_iterations = num_iterations
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)


        def compute_eigensystem(self, alpha, max_time = 60, numpy_type = numpy.float64):
		n = self.num_codons
		codons = self.codons
		mumat = codons.get_mutation_matrix()

		sm = numpy.matrix(self.get_selection_matrix(alpha))
		smdiag = numpy.diag(sm)
		w12 = numpy.matrix(numpy.diag(smdiag**0.5))
		wm12 = numpy.matrix(numpy.diag(smdiag**(-0.5)))
		pmat = w12*mumat*w12 - mumat

		ns = self.num_iterations
		dt = (1.0 / ns)
		my = {'lamb' : 1.0, 'v' :  numpy.matrix(numpy.ones((1,n))), 't' : 0.0}

		while my['t'] < 1.0:
		  dlamb = (my['v']*pmat*my['v'].T)[0,0]/(my['v']*my['v'].T)[0,0]
		  feps = mumat + my['t']*pmat
		  my['lamb'] += dt*dlamb
		  temp = feps - my['lamb']*numpy.matrix(numpy.eye(n))
		  rhs = dlamb*my['v'].T - pmat*my['v'].T
		  dv = numpy.matrix(numpy.linalg.solve(temp,rhs)).T
		  my['v'] += dt*dv
		  my['t'] += dt

		my['v']  = my['v']*wm12
		my['v'] /= my['v'].sum()
		(lhtopy, vhtopy) = codons.post_process_perturbative_solution(my['lamb'],my['v'])

		# DEBUGGING code:
		# UNCOMMENT following 3 lines to print eigenerror to screen
		# musm = self.get_mutation_selection_matrix(alpha)
		# test = musm*vhtopy - lhtopy*vhtopy
		# print(numpy.linalg.norm(test))

		self.eigenvalues[alpha] = lhtopy
		self.eigenmatrix[alpha] = vhtopy


	def equilibrate_messages(self):

		for alpha in xrange(self.num_site_types):
			self.compute_eigensystem(alpha)
		self.equilibrated = True
		super(ArdellSellaEvolverHomotopy, self).equilibrate_messages()



class eigensystem_CUDA_implementation:
	def __init__(self, parent, max_time = 60, delta = 10**(-32)):

		self.verbose = False
                self.converge_cutoff = True
		self.debug_mode = False
		self.starttime=time.time()
		self.max_time=max_time
                self.parent = parent
                self.delta = delta
		self.num_site_types = self.parent.num_site_types
		# create super matrix; dimension (num_site_types)^2 by num_site_types
		self.alpha1msm = self.parent.get_mutation_selection_matrix(0)
		self.msm_dim=numpy.int32(len(self.alpha1msm))
                #self.supermatrix = numpy.zeros((self.msm_dim*self.num_site_types,self.msm_dim)).astype(numpy.float32)
		self.supermatrix = numpy.zeros((self.msm_dim*self.num_site_types,self.msm_dim)).astype(numpy.float64)
		self.supermatrix[(0*self.msm_dim):((0+1)*self.msm_dim)]=self.alpha1msm
		# fill super matrix
                # While this 'for' loop accomplishes the same goal as Python's list comprehension,
                # NumPy's list comprehension capability is unknown.
		for alpha in range(1,self.num_site_types):
			self.supermatrix[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)]=self.parent.get_mutation_selection_matrix(alpha)
		#print 'supermatrix: ',self.supermatrix
		# eigenvector of ones; dimension num_site_types*msm_dim
                #self.eigenvec=numpy.ones(self.num_site_types*self.msm_dim).astype(numpy.float32)
		self.eigenvec=numpy.ones(self.num_site_types*self.msm_dim).astype(numpy.float64)
		self.eigenvec_old=numpy.copy(self.eigenvec)
		## length num_site_types*msm_dim eigenvec will be rearranged into a (num_site_types)by (msm_dim)
                #       eigen matrix -- one of the outputs of this class -- later
                #self.eigenmatrix = numpy.zeros((self.num_site_types,self.msm_dim)).astype(numpy.float32)
		self.eigenmatrix = numpy.zeros((self.num_site_types,self.msm_dim)).astype(numpy.float64)
		self.loop_power=numpy.int32(8)
                # Maximum power of 2 of CUDA kernel loop count;
                # to avoid 'time-out' errors, kernel calls can be kept short by keeping this number low
                # (11 should be fine).  The time difference between two kernel calls of 2^10 loops each
                # and one kernel call of 2^11 loops is negligable.  Of course, the time difference between
                # running 2^11 kernel calls of one loop and one kernel call of 2^11 loops would be significant.
                self.power_max=numpy.int32(13)
		self.loop_total=0
		# memory allocation
		self.cuda_supermatrix=cuda.mem_alloc(self.supermatrix.nbytes)
		self.cuda_loop_power=cuda.mem_alloc(8)
                self.cuda_power_max=cuda.mem_alloc(8)
                self.cuda_msm_dim=cuda.mem_alloc(8)
		self.cuda_eigenvec=cuda.mem_alloc(self.eigenvec.nbytes)
		## sums to normalize by
                #self.cuda_vsum=cuda.mem_alloc(4*self.num_site_types) ## one float for each eigenvector
		self.cuda_vsum=cuda.mem_alloc(8*self.num_site_types) ## one double for each eigenvector
		self.source_module = SourceModule("""
			#include <stdio.h>

			__global__ void eigensystem(double* vector, const double* mat, const int* loop_power,
                        const int* power_max, const int* dim, double* vsum){
				//dimension of individual eigenmatrix
				//const int dim = blockDim.x;
				// one eigenmatrix per block
				const int b = blockIdx.x;
				const int t = threadIdx.x;
				const int block_pos_mat = b*__powf(*dim,2);
				//const int i = block_pos_mat+(t*dim); // i -- row of supermatrix
				const int thread_pos_evec = b*(*dim);
                                int i;
                                int j;
				//const double loop_count = loop;
				//const int loop_count = 3000;
				//unsigned long loop_count = pow(2, loop_power);
                                unsigned int loop_count = 2;
                                if(*loop_power<*power_max){
                                        loop_count = loop_count << (*loop_power);
                                }else{
                                        loop_count = loop_count << (*power_max);
                                }
                                //printf("block.thread %d.%d; #loops: %u\\n", blockIdx.x, threadIdx.x, loop_count);

				unsigned int l;
                                //__shared__ float product[64];
                                __shared__ double product[64];
                                //__shared__ float e_vec_sum; // sum of all dot products on block; used for normalization
                                __shared__ double e_vec_sum; // sum of all dot products on block; used for normalization
				for(l=0;l<loop_count;l++){
					//__shared__ float product[*dim];  //does not work
					//product[t] = 0.0;
					e_vec_sum = 0.0;
                                        /* While CUDA's printf statement can print output from multiple threads and
                                        blocks in one kernel call, this 'if' condition restricts the printing to one
                                        thread of one block.  This is still useful because, so far, the bugs needing 
                                        to be fixed have been shared by all CUDA blocks and threads.Fixing one has
                                        fixed all.
                                        printf here does not work; must be at beginning of kernel...
                                        if(blockIdx.x == 0 && threadIdx.x == 0){
                                                printf("block.thread %d.%d;\\t\\t loop_power: %u power_max: %u
                                                        loop_count: %u  l: %u\\n", blockIdx.x, threadIdx.x,
                                                        *loop_power, *power_max, loop_count, l);
                                        }*/
                                        for(i=0;i<*dim;i++){
                                                product[i] = 0.0;
                                                for(j=0;j<*dim;j++){
                                                        //printf("i: %d  j: %d \\n", i, j);
                                                        //e_vec_sum += mat[i+j]*vector[thread_pos_evec+j];
                                                        //product[t] += mat[i+j]*vector[thread_pos_evec+j];


                                                        double out = mat[block_pos_mat+(i*(*dim))+j]*vector[thread_pos_evec+j];


                                                        //atomicAdd(&e_vec_sum, powf(out,2));
                                                        //atomicAdd(&e_vec_sum, out);
                                                        e_vec_sum += out;
                                                        //atomicAdd(&product[t], out);
                                                        product[i] += out;
                                                }
                                        }
					__syncthreads;
					//vector[thread_pos_evec+t]=product[t];
					// Normalize...
					//vector[thread_pos_evec+t]=vector[thread_pos_evec+t]/powf(e_vec_sum,0.5);
                                        for(i=0;i<*dim;i++){
                                                vector[thread_pos_evec+i]=product[i];
                                                vector[thread_pos_evec+i]=vector[thread_pos_evec+i]/e_vec_sum;
                                        }
				}				
			}
		""")
		## getting reference to kernel
		self.cuda_eigensystem = self.source_module.get_function("eigensystem")
		# moving data into global memory;
		# only done once; subsequent loops kernel calls pick up where the last left off
		cuda.memcpy_htod(self.cuda_eigenvec,self.eigenvec)
		cuda.memcpy_htod(self.cuda_supermatrix, self.supermatrix)
		cuda.memcpy_htod(self.cuda_power_max,self.power_max)
                cuda.memcpy_htod(self.cuda_msm_dim, self.msm_dim)
		
	
	
        def calculate(self):
		# move power of 2 request onto GPU
		cuda.memcpy_htod(self.cuda_loop_power, self.loop_power)
		# calling kernel
		if(self.verbose):
			print "================================== "
			print("""Calling CUDA; %d by %d supermatrix;\neigenvector of length %d;\n%d loops run
                                so far; \n%d loop request...""" % (self.msm_dim*self.num_site_types, self.msm_dim,
                                self.msm_dim*self.num_site_types, self.loop_total, 2**self.loop_power))
			print "Blocks: %d by %d\nThreads/block: %d by %d by %d" % (self.num_site_types,1,
                                self.msm_dim,1,1)
			print "================================== "
                #self.cuda_eigensystem(self.cuda_eigenvec, self.cuda_supermatrix, self.cuda_loop_power,
                #        self.cuda_power_max, self.cuda_vsum, grid=(self.num_site_types,1), block=(self.msm_dim,1,1))
		self.cuda_eigensystem(self.cuda_eigenvec, self.cuda_supermatrix, self.cuda_loop_power,
                        self.cuda_power_max, self.cuda_msm_dim, self.cuda_vsum, grid=(self.num_site_types,1), block=(1,1,1))
		## just called kernel for self. loops; add this to self.loop_total; logging purposes only
		self.loop_total+=2**self.loop_power
		# copy cuda_eigenvec back to main memory
		cuda.memcpy_dtoh(self.eigenvec,self.cuda_eigenvec)
	def get_eigenvalue(self,alpha):
		## use self.subeigenvecrix of self.supermatrix, and subvector of self.eigenvec;
		## direct translation of original 'evolvers' get_eigenvalue( msm, eigenvec)
		self.top = (numpy.dot(self.supermatrix[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)],
                        self.eigenvec[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)])*
                        self.eigenvec[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)])

		self.bottom = (self.eigenvec[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)] *
                        self.eigenvec[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)])
		self.lamda = self.top.sum()/self.bottom.sum()
		#print 'self.lamda =',self.lamda
		return self.lamda
	def get_eigenvalues(self):
		## compute all eigenvalues and put them in an array
		self.eigenvalues = numpy.zeros(self.num_site_types).astype(numpy.float64)
		for alpha in xrange(self.num_site_types):
			self.eigenvalues[alpha]=self.get_eigenvalue(alpha)
                        #if(self.verbose):
                        #        print 'alpha:',alpha,'\teigenvalue: %0.16f' % self.eigenvalues[alpha]
		return self.eigenvalues
	def get_eigenmatrix(self):
		## rearrange eigenvector of length (num_site_types * msm_dim) into eigenmatrix
		for alpha in xrange(self.num_site_types):
			self.eigenmatrix[alpha]=self.eigenvec[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)]
                        #if(self.verbose):
                        #  print 'alpha:',alpha,'\teigenvector:',self.eigenmatrix[alpha]
		return self.eigenmatrix
	def error_check(self):
		self.errorarray = numpy.zeros(self.num_site_types).astype(numpy.float64)
                self.last_max_error = 1 
		for alpha in range(0,self.num_site_types):
			self.errorarray[alpha]=(numpy.linalg.norm(self.eigenvec[
                                (alpha*self.msm_dim):((alpha+1)*self.msm_dim)] -
                                self.eigenvec_old[(alpha*self.msm_dim):((alpha+1)*self.msm_dim)]))
                self.max_error = numpy.abs(max(self.errorarray))
                if(self.verbose):
	                print 'error, length %d: ' % len(self.errorarray), self.errorarray
                if(self.converge_cutoff and self.max_error > 10*self.last_max_error):
                        if(self.verbose):
                                print 'have reached limit of machine precision'
                        return True
                else:
                        self.last_max_error = self.max_error
		if((time.time()-self.starttime)>self.max_time):
			if(self.verbose):
				print 'time out...'
                        return True
		elif(numpy.abs(max(self.errorarray))>self.delta):
                        # Error exceeds threshold
			if(self.verbose):
				print 'error exceeds delta (threshold) of', self.parent.delta
			## increase loop request
                        if(self.loop_power<self.power_max):
                                self.loop_power+=1
			## need to run more loops; copy eigenvec to eigenvec_old
			self.eigenvec_old=numpy.copy(self.eigenvec)
                        return False
		else:
			if(self.verbose):
				print '-=-=-=-=-=-=-=-=-'
				print 'error below delta!'
				print '-=-=-=-=-=-=-=-=-'
                        return True
	def done(self):
		if(self.verbose):
			print 'CUDA loop total (for all site types):\t',self.loop_total
			print 'final maximum error: ',numpy.abs(max(self.errorarray))
		self.parent.eigenvalues = self.get_eigenvalues()
		self.parent.eigenmatrix = self.get_eigenmatrix()
		
class ArdellSellaEvolverPowerCUDA (ArdellSellaEvolverAbstractBase): 
	def __init__(self, initial_code, site_types, delta, num_processes, epsilon, observables, num_iterations=1000):
		ArdellSellaEvolverAbstractBase.__init__(self, initial_code, site_types, delta, epsilon, observables)
                #from pycuda.compiler import SourceModule
                #import pycuda.driver as cuda
                #import pycuda.autoinit

                #SourceModule = __import__(pycuda.compiler.SourceModule)
                #cuda = __import__(pycuda.driver)
                #pycuda = __import__(pycuda.autoinit)

	def equilibrate_messages(self):
		super_matrix_eigen_system = eigensystem_CUDA_implementation(parent=self, delta=self.delta)
                # All function calls have been moved out of the eigensystem_CUDA_implementation class
		super_matrix_eigen_system.calculate()
                converged = super_matrix_eigen_system.error_check()
                while(not converged):
                  #super_matrix_eigen_system.reload()
                  super_matrix_eigen_system.calculate()
                  converged = super_matrix_eigen_system.error_check()
                super_matrix_eigen_system.done()
		del super_matrix_eigen_system
		## CUDA eigensystem solver done; eigenvalues and eigenmatrix have been inserted into this object
		##	by child object (CUDA eigensystem solver)	
		self.equilibrated = True
		super(ArdellSellaEvolverPowerCUDA, self).equilibrate_messages()
