#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_main_thread import *

#--------------------
# Class : GeneticAlgorithm
# author : Tafsir GNA
# purpose : Describing the structure of the kind of genetic algorithm used in the program
#--------------------

class GeneticAlgorithm:

	#	Class' variables
	NbMaxPopulation = 25
	mutationRate = 0.05
	crossOverRate = 0.80
	FITNESS_PADDING = 1
	NumberOfMigrants = 1
	MigrationRate = 0 # this variable holds the number of generations needed before a migration occurs during the search
	nbMainThreads = 3
	nbSlavesThread = 3
	NbGenToStop = 7

	# Builder
	def __init__(self, inst):

		self.hashTable = {} #hashTable is a dictionnary
		self.ga_memory = []
		self.listMainThreads = [] # i initialize a list that's intended to contain all the main threads of this genetic algorithm program
		self.moyNbGenerations = 0

		# i impart some parameters to the chromosome class and population class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = inst
		Chromosome.hashTable = self.hashTable

		# i set some class' properties of Population class
		ClspThread.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		#Population.ga_memory = self.ga_memory
		#Population.gaMemoryLocker = threading.Lock()
		ClspThread.MigrationRate = GeneticAlgorithm.MigrationRate
		ClspThread.crossOverRate = GeneticAlgorithm.crossOverRate

		ClspThread.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		ClspThread.listMainThreads = self.listMainThreads
		ClspThread.NbGenToStop = GeneticAlgorithm.NbGenToStop
		SlaveThreadsManager.nbSlavesThread = GeneticAlgorithm.nbSlavesThread
		ClspThread.NumberOfMigrants = GeneticAlgorithm.NumberOfMigrants

		

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def start(self):

		# In order to create this new population, i use the deep first search(DFS) to create some potential good chromosomes
		#print(Chromosome.problem.deadlineDemandPeriods)
		rootPerThread = math.ceil((Chromosome.problem.nbItems + 1) / GeneticAlgorithm.nbMainThreads)
		threadQueue = []
		threadCounter = 0

		prevThread = 0
		for item in range(0, Chromosome.problem.nbItems + 1):

			# i initialize the node from which the search of each thread will start
			root = Node()
			root.currentPeriod = 1

			if item == 0:
				if root.tab[Chromosome.problem.nbItems] != []:
					solution = [0] * Chromosome.problem.nbTimes
					solution[0] = item
					root.solution = solution
					del root.tab[Chromosome.problem.nbItems][0]
					threadQueue.append(copy.deepcopy(root))
			else:
				solution = [0] * Chromosome.problem.nbTimes
				solution[0] = item
				root.solution = solution
				del root.tab[item-1][0]
				#print("Root : ", root)
				threadQueue.append(copy.deepcopy(root))

			if len(threadQueue) == rootPerThread or item == Chromosome.problem.nbItems:

				#print(threadQueue)
				# i initialize the thread and put it into a list of threads created for this purpose
				clspThread = ClspThread(threadCounter, list(threadQueue))
				self.listMainThreads.append(clspThread)

				threadQueue = []
				threadCounter += 1

				if threadCounter == 1:
					prevThread = clspThread
				elif threadCounter > 1:
					clspThread.readyFlag = prevThread.readyEvent
					prevThread = clspThread

				if threadCounter == 3:
					break

		# want to make sure that the parent process will wait for the child threading before exiting
		#(self.listMainThreads[2]).start()
		#(self.listMainThreads[2]).join()
		
		# first, i initialize the population upon which the search will be applied
		for thread in self.listMainThreads:
			thread.start()
			thread.join()

		(self.listMainThreads[len(self.listMainThreads)-1]).readyEvent.wait()

		print("Initialized!!!")

		# then, i launch the search in order to find out the global optima
		ok = True
		it = 0
		while ok:
			print(it)
			for thread in self.listMainThreads:
				thread.run()
				#print("Pop : ", thread.population)

			(self.listMainThreads[len(self.listMainThreads)-1]).readyEvent.wait()

			for thread in self.listMainThreads:
				thread.readyEvent.clear()

			ok = False
			for mainThread in self.listMainThreads:
				if not mainThread.finished:
					ok = True
					break

			if not ok:
				break

			if it == 12:
				break

			it += 1

		
		self.printResults()
	
	#--------------------
	# function : printResults
	# Class : GeneticAlgorithm
	# purpose : This prints the results of the search once the search has ended
	#--------------------
	def printResults(self):

		#print(self.ga_memory)
		if len(self.ga_memory) != 0:

			self.bestSolution = self.ga_memory[0] # variable that holds the best solution found so far in the search

			for chromosome in self.ga_memory:
				if chromosome.fitnessValue < self.bestSolution.fitnessValue:
					self.bestSolution = chromosome

			print("The best solution found so far is : ", self.bestSolution.solution)
			#print(self.population)
			print("The fitness of this solution is : ", self.bestSolution.fitnessValue)

		else:
			
			print("No solutions have been found so far. Please Try again.")

		# i print on the screen the number of generations, the program got through before quiting
		sumNbGenerations = 0
		for thread in self.listMainThreads:
			sumNbGenerations += thread.NbGenerations

		print("The average number of generations produced is : ", math.ceil(sumNbGenerations / (GeneticAlgorithm.nbMainThreads)))
