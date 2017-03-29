#!/usr/bin/python
# -*-coding: utf-8 -*

from population import *

#--------------------
# Class : GeneticAlgorithm
# author : Tafsir GNA
# purpose : Describing the structure of the kind of genetic algorithm used in the program
#--------------------

class GeneticAlgorithm:

	#	Class' variables
	NbMaxPopulation = 100
	NbPopulation = 0
	mutationRate = 0.10
	crossOverRate = 0.70
	nbIterations = 20
	nbInitIterations = 50
	MAX_FITNESS = 0
	FITNESS_PADDING = 1

	# Builder
	def __init__(self,inst):

		self.instance = inst
		self.population = [] 
		self.ga_memory = []
		self.hashTable = {}

		# i initialize a list of counters
		self.ItemsCounters = getListCounters(self.instance.nbItems)

		self.ManufactItemsPeriods = getManufactPeriodsGrid(self.instance.nbItems, self.instance.deadlineDemandPeriods)

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def initPopulation(self):

		# i set some class' properties of Chromosome class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = self.instance

		# i set some class' properties of Population class
		Population.nbInitIterations = GeneticAlgorithm.nbInitIterations
		Population.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		Population.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		Population.crossOverRate = GeneticAlgorithm.crossOverRate

		Chromosome.ManufactItemsPeriods = self.ManufactItemsPeriods
		Chromosome.ItemsCounters = self.ItemsCounters
		Chromosome.hashTable = self.hashTable

		# i create a new population from scratch
		self.population = Population()
		#print(self.population)
	
	#--------------------
	# function : process
	# Class : GeneticAlgorithm
	# purpose : Running the process of seeking the optimal solution
	#--------------------
	def process(self):

		it = 0
		while it < GeneticAlgorithm.nbIterations:

			if len(self.ga_memory) == 2:
				break

			self.population = Population(self.population, self.ga_memory)

			it +=1

		#print(" the search stopped at the {} iteration ".format(it))

	#--------------------
	# function : printResults
	# Class : GeneticAlgorithm
	# purpose : This prints the results of the search once the search has ended
	#--------------------
	def printResults(self):

		bestChromosome = self.population.bestChromosome
		print("The best solution found so far is : ", bestChromosome.solution)
		print(self.population)
		print("The fitness of this solution is : ", bestChromosome.valueFitness)
		#print(" Memory : ", self.hashTable)