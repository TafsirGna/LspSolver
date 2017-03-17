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
	nbInitIterations = 20
	MAX_FITNESS = 0
	FITNESS_PADDING = 1
	#SUM_FITNESS = 0

	# Builder
	def __init__(self,inst):
		self.instance = inst
		self.population = [] 

	#--------------------
	# function : applyCrossOverto
	# Class : GeneticAlgorithm
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------
	'''
	def applyCrossOverto(self, chromosome1, chromosome2):

		chromosome3 = []
		chromosome4 = []

		if (randint(0,100) < (GeneticAlgorithm.crossOverRate*100)):

			# i create and initialize a table of counters
			counters = []
			i = 0
			while i < self.instance.nbItems:
				counters.append(1)
				i+=1

			# i retrieve a table that stores the period each item has been manufactered for
			ranks1 = getItemsRanks(chromosome1, list(counters))
			ranks2 = getItemsRanks(chromosome2, list(counters))

			ranks3 = []
			ranks4 = []

			randomIndice = randint(1,len(chromosome1)-1)


			#print(" ")
			#print(" chromosome1 : ", chromosome1, " chromosome2 : ", chromosome2)
			#print(" randomIndice : ", randomIndice)
			#print(" ranks1 : ", ranks1, " ranks2 : ", ranks2)

			i = 0
			while i < len(chromosome1):

				if i < randomIndice:

					chromosome3.append(chromosome1[i])
					chromosome4.append(chromosome2[i])

					ranks3.append(ranks1[i])
					ranks4.append(ranks2[i])

				else:

					chromosome3.append(chromosome2[i])
					chromosome4.append(chromosome1[i])

					ranks3.append(ranks2[i])
					ranks4.append(ranks1[i])

				i+=1

			#print(" ranks3 : ", ranks3, " ranks4 : ", ranks4)
			#print(" chromosome3 : ", chromosome3, " chromosome4 : ", chromosome4)

			# Once, the two resulting chromosomes have been formed, i make each of them feasible with regards of the constraints

			manufactMatrix = []
			i = 0
			while i < self.instance.nbItems:

				#j = 0
				#while

				i+=1

			chromosome3 = self.makeItFeasible(chromosome3)

			chromosome4 = self.makeItFeasible(chromosome4)

		else:
			chromosome3 = list(chromosome1)
			chromosome4 = list(chromosome2)

		return chromosome3,chromosome4

	def makeItFeasible(chromosome, ranks):
		pass
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

	def printResults(self):

		bestChromosome = self.population.bestChromosome
		print("The best solution found so far is : ", bestChromosome.solution)
		print(self.population)
		print("The fitness of this solution is : ", bestChromosome.valueFitness)

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

		# i create a new population from scratch
		self.population = Population(0)