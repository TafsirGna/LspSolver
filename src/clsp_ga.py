#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *
import time
from random import *

#--------------------
# Class : GeneticAlgorithm
# author : Tafsir GNA
# purpose : Describing the structure of the kind of genetic algorithm used in the programm
#--------------------

class GeneticAlgorithm:

	#	Class' variables
	NbPopulation = 0
	mutationRate = 0.20
	crossOverRate = 0.70
	nbIterations = 100
	nbInitIterations = 100

	# Builder
	def __init__(self,inst):
		self.instance = inst
		self.population = [] 

	def decrement(self, list_compteurs, noManufactPeriods):
		
		i = len(list_compteurs)-1
		while i >=0 :

			if i == (len(list_compteurs)-1):
				
				compteur = list_compteurs[i]
				del list_compteurs[i]
				compteur-=1
				if (compteur < 0):
					compteur = len(noManufactPeriods[i])-1
				list_compteurs.insert(i,compteur)

			else:
				if list_compteurs[i+1] == 0:

					compteur = list_compteurs[i]
					del list_compteurs[i]
					compteur-=1
					if (compteur < 0):
						compteur = len(noManufactPeriods[i])-1
					list_compteurs.insert(i,compteur)

			i-=1
	
	def getChromosomeFitness(self,chromosome):

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

		#print("FITNESS : ", fitness)

		return (1.0/fitness)
	

	
	def applyMutationto(self,chromosome):

		#print("M Start : ", chromosome)

		if (randint(0,100) < (GeneticAlgorithm.mutationRate*100)):

			
			mutated = False

			randomIndice = randint(0,(len(chromosome)-1))
			item1 = chromosome[randomIndice]

			while item1 == 0:
				randomIndice = randint(0,(len(chromosome)-1))
				# i get the item corresponding the gene to be flipped
				item1 = chromosome[randomIndice]

			#print("RandInt : ", randomIndice)

			item1Demands = self.instance.demandsGrid[item1-1]

			item1DemandPeriods = getDemandPeriods(item1Demands)

			#print("Dem : ", item1DemandPeriods)

			i = 0
			zeroperiod = -1
			nbItem1 = 0
			while i <= randomIndice:
				if chromosome[i] == item1 :
					nbItem1 += 1
				if chromosome[i] == 0:
					zeroperiod = i
				i += 1

			if zeroperiod != -1:
				chromosome = switchGenes(chromosome,randomIndice,zeroperiod)
				mutated = True
			elif randomIndice < len(chromosome)-1 :

				i = randomIndice+1
				while  i < item1DemandPeriods[nbItem1-1]:
					if chromosome[i] == 0:
						switchGenes(chromosome,i, randomIndice)
						mutated = True
						break
					i+=1

			#print("M End : ", chromosome)
			return chromosome

		else:
			#print("M End : ", chromosome)
			return chromosome



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

		while self.isFeasible(chromosome) is False:
			#print("F Start : ", chromosome)
			# i make sure that the number of goods producted aren't more than the number expected
			i = 0
			while i < self.instance.nbItems:

				itemDemandPeriods =  getDemandPeriods(self.instance.demandsGrid[i])

				j = 0
				while j < len(itemDemandPeriods):

					period = itemDemandPeriods[j]

					k = 0
					indice_periods = []
					while k <= period:
						if chromosome[k] == (i+1):
							indice_periods.append(k)
						k+=1

					if len(indice_periods) > j+1:
						del chromosome[indice_periods[len(indice_periods)-1]]
						chromosome.insert(indice_periods[len(indice_periods)-1], 0)

					j+=1

				i+=1

			#print(chromosome)
			
			# i make sure that the number of goods producted aren't less than the number expected
			i = 0
			while i < self.instance.nbItems:

				itemDemandPeriods =  getDemandPeriods(self.instance.demandsGrid[i])

				j = 0
				while j < len(itemDemandPeriods):

					period = itemDemandPeriods[j]

					k = 0
					zeroperiods = []
					nbItemPeriods = 0
					while k <= period:
						if chromosome[k] == 0:
							zeroperiods.append(k)
						if chromosome[k] == (i+1):
							nbItemPeriods+=1
						k+=1

					if nbItemPeriods < j+1 and len(zeroperiods) > 0:
						del chromosome[zeroperiods[len(zeroperiods)-1]]
						chromosome.insert(zeroperiods[len(zeroperiods)-1], i+1)

					j+=1

				itemManufactPeriods = getManufactPeriods(chromosome, i+1)
				if len(itemManufactPeriods) > len(itemDemandPeriods):
					del chromosome[itemManufactPeriods[len(itemManufactPeriods)-1]]
					chromosome.insert(itemManufactPeriods[len(itemManufactPeriods)-1], 0)

				i+=1

				# i check the chromosome before returning it

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

	def process(self):

		it = 0
		while it < GeneticAlgorithm.nbIterations:
			# i select the two chromosomes that'll be mated to produce offsprings

			#print("Population {0} : ".format(it), self.population )
			#print(" ")

			sum_fitness, list_fitnesses1 = self.getPopulationFitness()
			list_fitnesses2 = self.getRouletteWheel(list_fitnesses1, sum_fitness)

			#print("LIST FITNESS : ", list_fitnesses2)

			#then, i perform the roulette-wheel method to select the parents
			population = []
			i = 0
			while i < GeneticAlgorithm.NbPopulation:

				random_chrom1 = randint(0,100)
				random_chrom2 = randint(0,100)

				j = 0
				lbound = 0
				while j < len(list_fitnesses2):
					if (random_chrom1 >= lbound and random_chrom1 <= list_fitnesses2[j]):
						chromosome1 = self.population[j]
					if (random_chrom2 >= lbound and random_chrom2 <= list_fitnesses2[j]):
						chromosome2 = self.population[j]
					lbound = list_fitnesses2[j]
					j+=1

				#print("CrossOver : ", random_chrom1, " and : " , random_chrom2)

				chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

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
			i = 0
			while i < len(population):
				self.population.append(self.applyMutationto(population[i]))
				#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
				i+=1		

			#print("Population Suite {0} : ".format(it), self.population )
			#print(" ")

			#print("C1 : ",chromosome1," C2 : ",chromosome2)

			it +=1

	def printResults(self):

		sum_fitness, list_fitness = self.getPopulationFitness()
		chromosome = self.population[0]
		best_fitness = 1.0/list_fitness[0]
		inv_fitness = list_fitness[0]
		i = 1
		while i < len(self.population):
			fitness = 1.0 / list_fitness[i]
			#print("chromosome : ", self.population[i], " Fitness : ", fitness)
			if (fitness < best_fitness):
				best_fitness = fitness
				chromosome = self.population[i]
				inv_fitness = list_fitness[i]
			i+=1

		r_chromosome = []
		i = 0
		while i < len(chromosome):
			r_chromosome.append(chromosome[i])
			i+=1

		print("The best solution found so far is : ", r_chromosome)
		print("The fitness of this solution is : ", best_fitness)
		print("The percentage of the solution is : ", (inv_fitness*100/sum_fitness))

	def getPopulationFitness(self):

		list_fitness = []
		sum_fitness = 0
		i = 0 
		while i < len(self.population):
			fitness = self.getChromosomeFitness(self.population[i])
			list_fitness.append(fitness)
			sum_fitness += fitness
			i+=1
		return sum_fitness, list_fitness

	def getRouletteWheel(self, list_fitness, sum_fitness):

		wheel = []
		cumul_percentage = 0
		i = 0
		while i < len(list_fitness):
			fitness = list_fitness[i]
			percentage = (fitness *100)/float(sum_fitness)
			cumul_percentage += percentage
			wheel.append(cumul_percentage)
			i+=1
		return wheel

	def initPopulation(self):

		self.population = []

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

				if qual_chrom is True:
					self.population.append(chromosome)

			i+=1

		population = list(self.population)
		self.population = []

		i=0
		while i < len(population):
			chromosome = population[i]
			if (chromosome not in self.population):
				self.population.append(chromosome)
				#print(chromosome)
			i+=1

		GeneticAlgorithm.NbPopulation = len(self.population)

		#print(self.population)
		print(len(self.population))