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
	crossOverRate = 0.80
	FITNESS_PADDING = 1
	NbMigrants = 1
	MigrationRate = 0
	nbMainThreads = 3
	nbSlavesThread = 3

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

		# In order to create this new population, i use the deep first search(DFS) to create some potential good chromosomes

		# i pick the item, i will start the scheduling with
		item = 2#randint(1, Chromosome.problem.nbItems)
		period = Chromosome.problem.deadlineDemandPeriods[item-1][0]
		rootPerThread = math.ceil(period / GeneticAlgorithm.nbMainThreads)

		# i initialize each thread and put it into the corresponding list 
		i = period
		threadQueue = []
		threadCounter = 0

		while i >= 0:

			# i initialize the node from which the search of each thread will start
			root = Node()
			root.currentItem = item
			root.currentPeriod = 1
			root.itemCounter = 1

			root.solution = [0] * Chromosome.problem.nbTimes
			del root.solution[i]
			root.solution.insert(i, item)
			#print(root.solution)

			root.fitnessValue = ClspThread.evaluate(root.solution)
			
			if (threadQueue == []):

				threadQueue.append(root)
				#print(threadQueue)
			
			elif len(threadQueue) == 1 and (threadQueue[0]).fitnessValue == 0:

				threadQueue.append(root)
				#print(threadQueue)

			else:

				# i sort the list of zeroperiods from the most convenient place to the least convenient one

				size = len(threadQueue)
				prevValue = 0
				j = 0
				found = False
				while j < size:
					
					if root.fitnessValue >= prevValue and root.fitnessValue <= (threadQueue[j]).fitnessValue:
						threadQueue = threadQueue[:j] + [root] + threadQueue[j:]
						found = True
						break
					prevValue = (threadQueue[j]).fitnessValue
					j += 1
				if found is False:
					threadQueue.append(root)


			if  len(threadQueue) >= rootPerThread or i == 0:

				# i initialize the thread and put it into a list of threads created for this purpose
				clspThread = ClspThread(threadCounter, list(threadQueue), self.slaveThreadsManager, self.listMainThreads)
				self.listMainThreads.append(clspThread)
				(self.listMainThreads[threadCounter]).start()

				threadQueue = []
				threadCounter += 1

				#if threadCounter == 1:
				#	break

			i -= 1

		# want to make sure that the parent process will wait for the child threading before exiting
		for thread in self.listMainThreads:
			thread.join()

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
	