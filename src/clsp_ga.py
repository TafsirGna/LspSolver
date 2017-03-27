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
	NbMaxPopulation = 10
	NbPopulation = 0
	mutationRate = 0.15
	crossOverRate = 0.70
	nbIterations = 50
	nbInitIterations = 25
	MAX_FITNESS = 0
	FITNESS_PADDING = 1
	#nbLackDiversity = 0
	#SUM_FITNESS = 0

	# Builder
	def __init__(self,inst):
		self.instance = inst
		self.population = [] 

		# i initialize a list of counters
		self.ItemsCounters = getListCounters(self.instance.nbItems)

		#
		self.ManufactItemsPeriods = getManufactPeriodsGrid(self.instance.nbItems, self.instance.deadlineDemandPeriods)
		
		#print(self.ManufactItemsPeriods)

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
		Population.nbIterations = GeneticAlgorithm.nbIterations
		Population.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		Population.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		Population.crossOverRate = GeneticAlgorithm.crossOverRate

		Chromosome.ManufactItemsPeriods = self.ManufactItemsPeriods
		Chromosome.ItemsCounters = self.ItemsCounters

		# i create a new population from scratch
		self.population = Population()
		#print(self.population)

		'''
		c = Chromosome([2, 2, 2, 1, 0, 1, 3, 0])
		c.advmutate()
		print(" c : ", c, c.valueFitness)
		'''
	
	#--------------------
	# function : process
	# Class : GeneticAlgorithm
	# purpose : Running the process of seeking the optimal solution
	#--------------------
	def process(self):

		it = 0
		while it < GeneticAlgorithm.nbIterations:

			self.population = Population(self.population)
			
			it +=1

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