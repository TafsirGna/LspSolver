#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_thread import *

#--------------------
# Class : GeneticAlgorithm
# author : Tafsir GNA
# purpose : Describing the structure of the kind of genetic algorithm used in the program
#--------------------

class GeneticAlgorithm:

	#	Class' variables
	NbMaxPopulation = 35
	mutationRate = 0.05
	crossOverRate = 0.70
	FITNESS_PADDING = 1
	NbMigrants = 3
	MigrationRate = 0

	# Builder
	def __init__(self,inst):

		self.instance = inst
		self.hashTable = {} # hashTable is a dictionnary
		self.ga_memory = []

		# i initialize a list of counters
		self.ItemsCounters = getListCounters(self.instance.nbItems)

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def start(self):

		# i set some class' properties of Chromosome class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = self.instance
		Chromosome.ItemsCounters = self.ItemsCounters
		Chromosome.hashTable = self.hashTable

		# i set some class' properties of Population class
		Population.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		Population.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		Population.crossOverRate = GeneticAlgorithm.crossOverRate
		Population.ga_memory = self.ga_memory

		# i create a new population from scratch
		# In order to create this new population, i use the deep first search(DFS) to create some potential good chromosomes
		locker = threading.Lock()

		item = 1
		period = Chromosome.problem.deadlineDemandPeriods[item-1][0]

		listThreads = []

		i = 0
		while i <= 0:#period:

			# i initialize the node from which the search of each thread will start
			root = Node()
			root.currentItem = 1
			root.currentPeriod = 1

			j = 0
			while j < Chromosome.problem.nbTimes:
				if j == i:
					root.solution.append(1)
				else:
					root.solution.append(0)
				j += 1

			#print(root)

			# i initialize the thread and put it into a list of threads created for this purpose
			clspThread = ClspThread(j, copy.copy(root))
			clspThread.locker = locker
			listThreads.append(copy.copy(clspThread))
			(listThreads[i]).start()

			i += 1

		# i make sure the main process will wait for the threads before exiting
		for thread in listThreads:
			thread.join()

		#Population.startingPopulation = copy.deepcopy(self.population)	
		self.printResults()	
	
	#--------------------
	# function : printResults
	# Class : GeneticAlgorithm
	# purpose : This prints the results of the search once the search has ended
	#--------------------
	def printResults(self):

		#print(self.ga_memory)
		self.bestSolution = self.ga_memory[0] # variable that holds the best solution found so far in the search

		for chromosome in self.ga_memory:
			if chromosome.fitnessValue < self.bestSolution.fitnessValue:
				self.bestSolution = chromosome

		print("The best solution found so far is : ", self.bestSolution.solution)
		#print(self.population)
		print("The fitness of this solution is : ", self.bestSolution.fitnessValue)

		#print(" Memory : ", self.ga_memory)
		#print(self.population)
	