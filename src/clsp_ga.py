#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *
import time
from random import *

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
	nbIterations = 30
	nbInitIterations = 20
	MAX_FITNESS = 0
	FITNESS_PADDING = 1
	#SUM_FITNESS = 0

	# Builder
	def __init__(self,inst):
		self.instance = inst
		self.population = [] 
		self.popObjValues = []	# variable that contains the value corresponding to the objective function
	
	#--------------------
	# function : getObjectiveValue
	# Class : GeneticAlgorithm
	# purpose : Returning the value corresponding to the objective function
	#--------------------

	def getObjectiveValue(self, chromosome):

		fitness = 0
		grid = self.instance.chanOverGrid
		#print(chromosome)

		# Calculation of all the change-over costs
		
		i = 1
		tmp = chromosome[0]
		while i < len(chromosome) :

			n = chromosome[i]

			if (tmp == 0):
				i+=1
				tmp = n
			else:
				
				if (n != 0):
					if (n != tmp):
						fitness += int((grid[tmp-1])[n-1])
						tmp = n
				else:
					tmp = chromosome[i-1]

					j=i
					while j < len(chromosome) and chromosome[j] == 0:
						j+=1
					i=j-1
				
				i+=1

		# Calculation of the sum of holding costs

		i=0
		while i < self.instance.nbItems:

			itemDemands = self.instance.demandsGrid[i]

			itemDemandPeriods = getDemandPeriods(itemDemands)

			itemManufactPeriods = getManufactPeriods(chromosome, i+1)

			j = 0
			while j < len(itemDemandPeriods):
				fitness += int(self.instance.holdingGrid[i])*(itemDemandPeriods[j]-itemManufactPeriods[j])
				j+=1

			i+=1

		return fitness


	#--------------------
	# function : getChromosomeFitness
	# Class : GeneticAlgorithm
	# purpose : Indicating how fit a chromosome is, given the current problem
	#--------------------

	#def getChromosomeFitness(self,chromosome):
	#	pass	

	#--------------------
	# function : applyMutationto
	# Class : GeneticAlgorithm
	# purpose : Applying mutation to a given chromosome and returning the resulting one
	#--------------------

	def applyMutationto(self,chromosome):

		#print("M Start : ", chromosome)

		if (randint(0,100) < (GeneticAlgorithm.mutationRate*100)):

			mutated = False
			# i make sure that the returned chromosome's been actually mutated
			while mutated is False:

				randomIndice = randint(0,(len(chromosome)-1))
				item1 = chromosome[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(len(chromosome)-1))
					# i get the item corresponding the gene to be flipped
					item1 = chromosome[randomIndice]

				item1DemandPeriods = getDemandPeriods(self.instance.demandsGrid[item1-1])

				i = 0
				nbItem1 = 0
				while i <= randomIndice:
					if chromosome[i] == item1:
						nbItem1 += 1
					i+=1

				deadlineItem1 = item1DemandPeriods[nbItem1-1]

				# i make sure that the second item chosen to replace the first one won't be the same with the item 1.
				item2 = randint(1, self.instance.nbItems)
				while item2 == item1:
					item2 = randint(1, self.instance.nbItems)

				item2ManufactPeriods = getManufactPeriods(chromosome, item2)

				item2DemandPeriods = getDemandPeriods(self.instance.demandsGrid[item2-1])

				#print(" item1 : ", item1, " item2 : ", item2, " randomIndice : ", randomIndice)
				#print(item2DemandPeriods)
				i = 0
				while i < len(item2DemandPeriods):
					if item2DemandPeriods[i] >= randomIndice and deadlineItem1 > item2ManufactPeriods[i]:
						chromosome = switchGenes(chromosome, randomIndice, item2ManufactPeriods[i])
						mutated = True
						break
					i += 1

			return chromosome

		else:
			#print("M End : ", chromosome)
			return chromosome

	#--------------------
	# function : applyMutationto
	# Class : GeneticAlgorithm
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------
	def applyCrossOverto(self, chromosome1, chromosome2):

		chromosome3 = []
		chromosome4 = []

		if (randint(0,100) < (GeneticAlgorithm.crossOverRate*100)):

			randomIndice = randint(0,len(chromosome1))

			i = 0
			while i < randomIndice:
				chromosome3.append(chromosome1[i])
				chromosome4.append(chromosome2[i])
				i+=1

			i = randomIndice
			while i < len(chromosome1):
				chromosome3.append(chromosome2[i])
				chromosome4.append(chromosome1[i])
				i+=1

			chromosome3 = self.makeItFeasible(chromosome3)

			chromosome4 = self.makeItFeasible(chromosome4)

		else:
			chromosome3 = list(chromosome1)
			chromosome4 = list(chromosome2)

		return chromosome3,chromosome4


	def makeItFeasible(self, chromosome):

		if self.isFeasible(chromosome) is False:
			#print("F Start : ", chromosome)
			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < self.instance.nbItems:

				itemDemandPeriods = getDemandPeriods(self.instance.demandsGrid[i])

				j = 0
				nb = 0
				while j <= itemDemandPeriods[len(itemDemandPeriods)-1]:

					if chromosome[j] == i+1 :

						nb += 1
						if nb > len(itemDemandPeriods):

							del chromosome[j]
							chromosome.insert(j,0)

						else:
							if j > itemDemandPeriods[nb-1]:
								del chromosome[j]
								chromosome.insert(j,0)

					j+=1

				i+=1

			#print(chromosome)
			
			# i make sure that the number of items producted isn't inferior to the number expected
			i = 0
			while i < self.instance.nbItems:

				itemDemandPeriods =  getDemandPeriods(self.instance.demandsGrid[i])

				#print("item : ", i+1)

				nb = 0
				j = 0
				while nb < len(itemDemandPeriods) and j < len(chromosome):

					contain = False
					zeroperiods = []
					#print(" item nb : ", itemDemandPeriods[nb], " , ", nb)
					while j <= itemDemandPeriods[nb]:

						if chromosome[j] == 0:
							zeroperiods.append(j)

						if chromosome[j] == i+1 :
							#print("Yes : ", j)
							nb += 1	
							contain = True
							j += 1
							break

						j += 1

					#print("nb : ", nb, " j : ", j, " bool : ", contain, " zeroperiods : ", zeroperiods)

					if contain is False:
						if len(zeroperiods) > 0:
							del chromosome[zeroperiods[0]]
							chromosome.insert(zeroperiods[0], i+1)
							nb += 1
							j = zeroperiods[0]+1

				#print("Inter : ", chromosome)

				i+=1

			#print("F End : ", chromosome)

		return chromosome

	
	def isFeasible(self,chromosome):

		# i check first that there's not shortage or backlogging
		i = 0
		feasible = False
		while i < self.instance.nbItems:

			demandProductPeriods = getDemandPeriods(self.instance.demandsGrid[i])

			manufactProductPeriods = getManufactPeriods(chromosome,i+1)

			if (len(manufactProductPeriods) != len(demandProductPeriods)):
				return False
			else:
				j = 0
				while j < len(manufactProductPeriods):

					if (manufactProductPeriods[j] > demandProductPeriods[j]):
						return False

					j+=1

				feasible = True

			i+=1

		if (feasible is True):
			return True
		return False

	#--------------------
	# function : process
	# Class : GeneticAlgorithm
	# purpose : Running the process of seeking the optimal solution
	#--------------------
	def process(self):

		it = 0
		while it < GeneticAlgorithm.nbIterations:

			# i select the two chromosomes that'll be mated to produce offsprings
			print("Population {0} : ".format(it), self.population )
			print(" ")
			#print(" Values : ", self.popObjValues)
			#print(" ")

			sumFitness = 0
			tempSumFitness = 0 # variable used to quantify the lack of diversity in the population
			listFitness = []
			i = 0
			while i < len(self.population):
				#print(" i : ", i)
				temp = self.popObjValues[i]

				value = (GeneticAlgorithm.MAX_FITNESS-temp)
				tempSumFitness += value

				value += GeneticAlgorithm.FITNESS_PADDING
				listFitness.append(value)
				sumFitness += value
				i += 1

			# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
			if tempSumFitness == 0:
				chromosome = list(self.population[0])
				del self.population[0]
				self.population.insert(0, self.applyMutationto(chromosome))

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
			self.popObjValues = []
			GeneticAlgorithm.MAX_FITNESS = 0
			i = 0
			while i < len(population):
				chromosome = self.applyMutationto(population[i])
				self.population.append(chromosome)
				value = self.getObjectiveValue(chromosome)
				self.popObjValues.append(value)
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
		bestValue = self.popObjValues[0]
		i = 1
		while i < len(self.population):
			value = self.popObjValues[i]
			if (value < bestValue):
				bestValue = value
				chromosome = self.population[i]
			i+=1

		print("The best solution found so far is : ", chromosome)
		print(self.population)
		print("The fitness of this solution is : ", bestValue)

	#--------------------
	# function : initPopulation
	# Class : GeneticAlgorithm
	# purpose : Initializing le population of chromosomes to be processed during the first iteration
	#--------------------

	def initPopulation(self):

		self.population = []
		self.popObjValues = []
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
				chromosome = []
				k = 0
				while k < self.instance.nbTimes:
					chromosome.append(0)
					k+=1

				qual_chrom = True # boolean variable that determines if the chromosome being formed is good or not

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

							if chromosome[m] == 0 : 
								zeroperiods.append(m)

							m+=1

						if len(zeroperiods) == 0:
							qual_chrom = False
							break
						else:
							random_indice = randint(0, len(zeroperiods)-1)
							del chromosome[zeroperiods[random_indice]]
							chromosome.insert(zeroperiods[random_indice],itemK)

						l+=1

					k+=1

					if qual_chrom is False:
						break

				j+=1

				if qual_chrom is True and chromosome not in self.population:
					self.population.append(chromosome)
					value = self.getObjectiveValue(chromosome)
					self.popObjValues.append(value)

					# i store the value of the highest value of the objective function
					if value > GeneticAlgorithm.MAX_FITNESS:
						GeneticAlgorithm.MAX_FITNESS = value

					# i check that the size of the population don't exceed the maximum number of population retained
					if len(self.population)>=GeneticAlgorithm.NbMaxPopulation:
						GeneticAlgorithm.NbPopulation = len(self.population)
						return

			i+=1

		GeneticAlgorithm.NbPopulation = len(self.population)

		#print(self.population)
		print(len(self.population))