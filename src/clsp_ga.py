#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *
import time

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


	#def getChromosomeFitness(self,chromosome):
	#	pass	

	

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

	
	def applyCrossOverto(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		if (randint(0,100) < (GeneticAlgorithm.crossOverRate*100)):

			randomIndice = randint(0,len(chromosome1.solution))

			i = 0
			while i < randomIndice:
				solution3.append(chromosome1.solution[i])
				solution4.append(chromosome2.solution[i])
				i+=1

			i = randomIndice
			while i < len(chromosome1.solution):
				solution3.append(chromosome2.solution[i])
				solution4.append(chromosome1.solution[i])
				i+=1

			chromosome3 = Chromosome(solution3)
			chromosome3.getFeasible()

			chromosome4 = Chromosome(solution4)
			chromosome4.getFeasible()

		else:
			chromosome3 = Chromosome(chromosome1.solution)
			chromosome4 = Chromosome(chromosome2.solution)

		return chromosome3,chromosome4
	

	
	#--------------------
	# function : process
	# Class : GeneticAlgorithm
	# purpose : Running the process of seeking the optimal solution
	#--------------------
	def process(self):

		it = 0
		while it < GeneticAlgorithm.nbIterations:

			# i select the two chromosomes that'll be mated to produce offsprings
			#print("Population {0} : ".format(it), self.population )
			#print(" ")
			#print(" Values : ", self.popObjValues)
			#print(" ")

			sumFitness = 0
			tempSumFitness = 0 # variable used to quantify the lack of diversity in the population
			listFitness = []
			i = 0
			while i < len(self.population):
				#print(" i : ", i)
				chromosome = self.population[i]
				temp = chromosome.valueFitness

				value = (GeneticAlgorithm.MAX_FITNESS-temp)
				tempSumFitness += value

				value += GeneticAlgorithm.FITNESS_PADDING
				listFitness.append(value)
				sumFitness += value
				i += 1

			# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
			if tempSumFitness == 0:
				# TODO
				chromosome = self.population[0]
				del self.population[0]
				chromosome.mutate()
				self.population.insert(0, chromosome)

			#print ("Fitness 1 : ", listFitness)
			#print(" ")

			i = 0
			percentage = 0
			while i < len(self.population):
				temp = listFitness[i]
				del listFitness[i]
				percentage += (float(temp)/float(sumFitness))*100
				#print (" FOO : temp : ", temp, " sumFitness : ", sumFitness, " percentage : ", percentage)
				listFitness.insert(i, percentage)
				i += 1

			#print ("Fitness 2 : ", listFitness, " MAX_FITNESS : ", GeneticAlgorithm.MAX_FITNESS)
			#print(" ")

			# i perform the roulette-wheel method to select the parents
			population = []
			i = 0
			while i < GeneticAlgorithm.NbPopulation:

				random_chrom1 = randint(0,100)
				random_chrom2 = randint(0,100)

				j = 0
				lbound = 0
				while j < len(listFitness):
					if (random_chrom1 >= lbound and random_chrom1 <= listFitness[j]):
						chromosome1 = self.population[j]
					if (random_chrom2 >= lbound and random_chrom2 <= listFitness[j]):
						chromosome2 = self.population[j]
					lbound = listFitness[j]
					j += 1

				#print("CrossOver : ", random_chrom1, " and : " , random_chrom2)

				chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

				#if self.isFeasible(chromosome3) is False or self.isFeasible(chromosome4) is False:
				#	print("c3 : ", c3, " c4 : ", c4)

				population.append(chromosome3)
				i += 1

				if (i == GeneticAlgorithm.NbPopulation):
					break

				population.append(chromosome4)
				i += 1

				if (i == GeneticAlgorithm.NbPopulation):
					break

			#print("Population INter {0} : ".format(it), population )
			#print(" ")

			self.population = []
			GeneticAlgorithm.MAX_FITNESS = 0
			i = 0
			while i < len(population):
				chromosome = population[i]
				chromosome.mutate()
				self.population.append(chromosome)
				value = chromosome.valueFitness
				if value > GeneticAlgorithm.MAX_FITNESS:
						GeneticAlgorithm.MAX_FITNESS = value
				#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
				i+=1		

			#print("Population Suite {0} : ".format(it), self.population )
			#print(" ")

			#print("C1 : ",chromosome1," C2 : ",chromosome2)

			it +=1

	def printResults(self):

		#print(self.population)
		chromosome = self.population[0]
		bestValue = chromosome.valueFitness
		i = 1
		while i < len(self.population):
			c = self.population[i]
			value = c.valueFitness
			if (value < bestValue):
				bestValue = value
				chromosome = c
			i+=1

		print("The best solution found so far is : ", chromosome.solution)
		#print(self.population)
		print("The fitness of this solution is : ", bestValue)

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def initPopulation(self):

		# i set some class' properties of Chromosome class
		Chromosome.mutationRate = GeneticAlgorithm.mutationRate
		Chromosome.problem = self.instance

		self.population = []
		GeneticAlgorithm.MAX_FITNESS = 0

		listItems = []

		# i fill the listItem object with the number of the different items
		i = 0
		while i < self.instance.nbItems:
			listItems.append(i+1)
			i+=1

		# i generate the differents permutations out of the list of items, this will determine the order in which the items will be placed in the chromosome
		list_permutations = list(permutations(listItems))

		i = 0
		while i < GeneticAlgorithm.nbInitIterations:

			j = 0
			while j < len(list_permutations):

				permutationJ = list_permutations[j] 
				#print(" - ", i, " permutation : ", permutationJ)

				# i create a chromosome and fill it with some zeros
				solution = []
				k = 0
				while k < self.instance.nbTimes:
					solution.append(0)
					k+=1

				qual_sol = True # boolean variable that determines if the chromosome being formed is good or not

				k = 0
				while k < len(permutationJ):

					itemK = permutationJ[k]
					itemKDemands = self.instance.demandsGrid[itemK-1]
					itemKDemandPeriods = getDemandPeriods(itemKDemands)

					l = 0
					while l < len(itemKDemandPeriods):

						periodL = itemKDemandPeriods[l]

						m = 0
						zeroperiods = []
						while m <= periodL:

							if solution[m] == 0 : 
								zeroperiods.append(m)

							m+=1

						if len(zeroperiods) == 0:
							qual_sol = False
							break
						else:
							random_indice = randint(0, len(zeroperiods)-1)
							del solution[zeroperiods[random_indice]]
							solution.insert(zeroperiods[random_indice],itemK)

						l+=1

					k+=1

					if qual_sol is False:
						break

				j+=1

				c = Chromosome(solution)
				if qual_sol is True and c not in self.population:
					self.population.append(c)

					# i store the value of the highest value of the objective function
					value = c.valueFitness
					if value > GeneticAlgorithm.MAX_FITNESS:
						GeneticAlgorithm.MAX_FITNESS = value

					# i check that the size of the population don't exceed the maximum number of population retained
					if len(self.population)>=GeneticAlgorithm.NbMaxPopulation:
						GeneticAlgorithm.NbPopulation = len(self.population)
						return

			i+=1

		GeneticAlgorithm.NbPopulation = len(self.population)

		#print(len(self.population))