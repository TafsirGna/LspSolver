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
	NbMaxPopulation = 30
	mutationRate = 0.15
	crossOverRate = 0.70
	nbInitIterations = 50
	FITNESS_PADDING = 1

	# Builder
	def __init__(self,inst):

		self.instance = inst
		self.population = [] 
		self.ga_memory = []
		self.hashTable = {} # hashTable is a dictionnary

		# i initialize a list of counters
		self.ItemsCounters = getListCounters(self.instance.nbItems)

		#self.ManufactItemsPeriods = getManufactPeriodsGrid(self.instance.nbItems, self.instance.deadlineDemandPeriods)
		self.stopFlag = [False] # flag that indicates if it's time to stop searching.

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def initPopulation(self):

		# i set some class' properties of Chromosome class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = self.instance
		#Chromosome.ManufactItemsPeriods = self.ManufactItemsPeriods
		Chromosome.ItemsCounters = self.ItemsCounters
		Chromosome.hashTable = self.hashTable

		# i set some class' properties of Population class
		Population.nbInitIterations = GeneticAlgorithm.nbInitIterations
		Population.NbMaxPopulation = GeneticAlgorithm.NbMaxPopulation
		Population.FITNESS_PADDING = GeneticAlgorithm.FITNESS_PADDING
		Population.crossOverRate = GeneticAlgorithm.crossOverRate
		Population.ga_memory = self.ga_memory
		Population.stopFlag = self.stopFlag

		# i create a new population from scratch
		self.population = Population()
		Population.startingPopulation = self.population
		#print(" Fitness Data : ", self.population.listFitnessData)
		
		
		#c = Chromosome([3, 1, 1, 2, 2, 0, 2, 0])
		#c.mutate()
		#print(c, c.hashSolution)
		
	
	#--------------------
	# function : process
	# Class : GeneticAlgorithm
	# purpose : Running the process of seeking the optimal solution
	#--------------------
	def process(self):

		#i = 0
		while len(self.ga_memory) < 3 and self.stopFlag[0] is False:

		#	if i == 2:
		#		break 

			self.population = Population(self.population)
		#	i+=1

	#--------------------
	# function : printResults
	# Class : GeneticAlgorithm
	# purpose : This prints the results of the search once the search has ended
	#--------------------
	def printResults(self):

		#print(self.ga_memory)
		self.bestSolution = self.ga_memory[0] # varaible that holds the best solution found so far in the search

		for chromosome in self.ga_memory:
			if chromosome.fitnessValue < self.bestSolution.fitnessValue:
				self.bestSolution = chromosome

		print("The best solution found so far is : ", self.bestSolution.solution)
		#print(self.population)
		print("The fitness of this solution is : ", self.bestSolution.fitnessValue)

		#print(" Memory : ", self.ga_memory)
		#print(self.population)
	