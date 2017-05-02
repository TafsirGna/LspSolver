#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_main_thread import *
from clsp_slave_thread import *

#--------------------
# Class : GeneticAlgorithm
# author : Tafsir GNA
# purpose : Describing the structure of the kind of genetic algorithm used in the program
#--------------------

class GeneticAlgorithm:

	#	Class' variables
	NbMaxPopulation = 25
	mutationRate = 0.05
	crossOverRate = 0.70
	FITNESS_PADDING = 1
	NbMigrants = 3
	MigrationRate = 0
	nbSlavesThread = 4

	# Builder
	def __init__(self, inst):

		self.instance = inst
		self.hashTable = {} # hashTable is a dictionnary
		self.ga_memory = []
		self.ItemsCounters = getListCounters(self.instance.nbItems)

		# i impart some parameters to the chromosome class and population class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = self.instance
		Chromosome.ItemsCounters = self.ItemsCounters
		Chromosome.hashTable = self.hashTable

		# i set some class' properties of Population class
		Population.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		Population.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		Population.crossOverRate = GeneticAlgorithm.crossOverRate
		Population.ga_memory = self.ga_memory
		Population.gaMemoryLocker = threading.Lock()

		SlaveThreadsManager.crossOverRate = GeneticAlgorithm.crossOverRate

		self.listMainThreads = [] # i initialize a list that's intended to contain all the main threads of this genetic algorithm program
		self.slaveThreadsManager = SlaveThreadsManager(GeneticAlgorithm.nbSlavesThread) # i initialize a list that's intended to contain all the population's initialization threads 

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def start(self):

		# i create a new population from scratch
		# In order to create this new population, i use the deep first search(DFS) to create some potential good chromosomes

		# i pick the item, i will start the scheduling with
		item = 1
		period = Chromosome.problem.deadlineDemandPeriods[item-1][0]

		i = 2
		while i <= Chromosome.problem.nbItems:
			if Chromosome.problem.deadlineDemandPeriods[i-1][0] < period:
				period = Chromosome.problem.deadlineDemandPeriods[i-1][0]
				item = i
			i += 1

		# i initialize each thread and put it into the corresponding list 
		i = 0
		while i <= 1:#period:

			# i initialize the node from which the search of each thread will start
			root = Node()
			root.currentItem = item
			root.currentPeriod = 1
			root.itemCounter = 1

			j = 0
			while j < Chromosome.problem.nbTimes:
				if j == i:
					root.solution.append(item)
				else:
					root.solution.append(0)
				j += 1

			#print(root)

			# i initialize the thread and put it into a list of threads created for this purpose
			clspThread = ClspThread(j, copy.copy(root), self.slaveThreadsManager)
			self.listMainThreads.append(copy.copy(clspThread))
			(self.listMainThreads[i]).start()
			(self.listMainThreads[i]).join()

			i += 1

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
	