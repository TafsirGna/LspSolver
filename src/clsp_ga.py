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
	mutationRate = 0.25
	crossOverRate = 0.70
	nbIterations = 1
	badFitnessValue = 0

	# Builder
	def __init__(self,inst):
		self.instance = inst
		self.population = [] 

	def initPopulation(self):

		self.initPopulation1()
		if (len(self.population) <= 2):
			self.initPopulation2()

	def initPopulation2(self):

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
		while i < len(list_permutations) :#and len(self.population) <= 10'''

			one_permutation = list(list_permutations[i])

			# i create a chromosome and fill it with some zeros
			chromosome = []
			j = 0
			while j < self.instance.nbTimes:
				chromosome.append('0')
				j+=1

			self.getAllChromosomes(one_permutation,0,chromosome)

			i+=1


		population = list(self.population)
		self.population = []

		i=0
		while i < len(population):
			chromosome = population[i]
			if (chromosome not in self.population):
				self.population.append(chromosome)
			i+=1

		GeneticAlgorithm.NbPopulation = len(self.population)
		#print(self.population)
	

	def getAllChromosomes(self, permutation, indice_item, chromosome):

		item = permutation[indice_item]

		itemDemandPeriods = getDemandPeriods(self.instance.demandsGrid[item-1])
		i = 0
		noManufactPeriods = []
		while i < len(itemDemandPeriods):

			periodI = itemDemandPeriods[i]

			if i == 0:
				lbound = 0
			else:
				lbound = itemDemandPeriods[i-1]+1

			j = periodI
			noManufactPeriodsI = []
			while j >= lbound:
				if (int(chromosome[j],2) == 0):
					noManufactPeriodsI.append(j)
				j-=1

			if (len(noManufactPeriodsI) == 0):
				return []

			noManufactPeriods.append(noManufactPeriodsI)

			i+=1

		# Now, i build the chromosome

		list_compteurs = []
		i = 0
		while i < len(noManufactPeriods):
			list_compteurs.append(len(noManufactPeriods[i]))
			i+=1

		resulting_chromosomes = []
		goOn = True
		while goOn is True:

			chromosome1 = list(chromosome)

			i = 0
			while i < len(noManufactPeriods):
				periodI = noManufactPeriods[i][list_compteurs[i]-1]
				del chromosome1[periodI]
				chromosome1.insert(periodI,(str(bin(item))[2:]))
				i+=1

			resulting_chromosomes.append(chromosome1)
					
			self.decrement(list_compteurs,noManufactPeriods)

			goOn = False
			i = 0
			while i < len(list_compteurs):
				if (list_compteurs[i] != 0):
					goOn = True
				i+=1

		#print ("RESLT_CHROMS : ", resulting_chromosomes)

		if indice_item == len(permutation)-1:
			self.population += resulting_chromosomes
			return []

		i = 0
		while i < len(resulting_chromosomes):

			chromosome2 = list(resulting_chromosomes[i])
			self.getAllChromosomes(permutation,(indice_item+1),chromosome2)

			i+=1


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
		
		#pass

	def getChromosomeFitness(self,chromosome):

		if (self.isFeasible(chromosome)):
			fitness = 0
			grid = self.instance.chanOverGrid
			#print(chromosome)

			# Calculation of all the change-over costs
			
			i = 0
			tmp = 0
			while i < len(chromosome) :

				n = int(chromosome[i],2)
				
				if i == 0 :
					tmp = n
				else:
					if (n != 0):
						if (n != tmp):
							fitness += int((grid[tmp-1])[n-1])
							tmp = n
					else:
						tmp = int(chromosome[i-1],2)

						j=i
						while j < len(chromosome) and int(chromosome[j],2) == 0:
							j+=1
						i=(j-1)
				
				i+=1

			# Calculation of the sum of holding costs

			i=0
			while i < self.instance.nbItems:

				itemDemands = self.instance.demandsGrid[i]

				itemDemandPeriods = getDemandPeriods(itemDemands)

				itemManufactPeriods = getManufactPeriods(chromosome, i+1)

				j = 0
				while j < len(itemDemandPeriods):
					#print(j)
					fitness += int(self.instance.holdingGrid[i])*(itemDemandPeriods[j]-itemManufactPeriods[j])
					j+=1

				i+=1

			#print("FITNESS : ", fitness)

			if (fitness > GeneticAlgorithm.badFitnessValue):
				GeneticAlgorithm.badFitnessValue = fitness

			return (1.0/fitness)
		else:
			return (1.0/GeneticAlgorithm.badFitnessValue)

	
	def applyMutationto(self,chromosome):

		if (randint(0,100) < (GeneticAlgorithm.mutationRate*100)):

			mutated = False

			if ('0' in chromosome):

				while mutated == False:

					# i get the indice of the gene i have to flip
					randomIndice = randint(0,(len(chromosome)-1))

					# i get the number of the product corresponding the gene to be flipped
					product1 = int(chromosome[randomIndice],2)

					demandProduct1 = self.instance.demandsGrid[product1-1]

					demandProduct1Periods = getDemandPeriods(demandProduct1)

					i = 0
					lbound = 0
					while i < len(demandProduct1Periods):
						if (randomIndice >= lbound and randomIndice <= demandProduct1Periods[i]):
							deadline = demandProduct1Periods[i]

							if i == 0:
								lbound = 0
							else:
								lbound = demandProduct1Periods[i-1]

							break
						lbound = demandProduct1Periods[i]
						i+=1

					j = 0
					while j >= lbound and j <= deadline:
						if (int(chromosome[j],2) == 0):
							indice_zero = j
							mutated = True
							break
						j+=1

					if mutated is True:
						return switchGenes(chromosome,randomIndice,indice_zero)


			if ('0' not in chromosome or mutated == False):
				#print("NO MUTATION HAPPENED!!!")
				return chromosome


		else:
			return chromosome
			"""
			# then, i get the number of the product i have to replace the former product at the gene with
			product2 = randint(1,self.nbItems)

			demandProduct1 = self.instance.demandsGrid[product1-1]
			"""

	def applyCrossOverto(self,chromosome1, chromosome2):

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

			"""
			if self.isFeasible(chromosome3) is False:
				chromosome3 = self.makeItFeasible(chromosome3)

			if self.isFeasible(chromosome4) is False:
				chromosome3 = self.makeItFeasible(chromosome3)
			"""

		else:
			chromosome3 = list(chromosome1)
			chromosome4 = list(chromosome2)

		return chromosome3,chromosome4

	def makeItFeasible(self, chromosome):

		
		# i make sure that the number of goods producted aren't more or less than the number of the same goods expected
		i = 0
		while i < self.instance.nbItems:

			itemDemandPeriods =  getDemandPeriods(self.instance.demandsGrid[i])

			itemManufactPeriods = getManufactPeriods(chromosome,i+1)

			j = 0
			while j < len(itemManufactPeriods):

				period = itemManufactPeriods[j]

				k = 0
				n = 0
				indice_periods = []
				while k < period:
					if int(chromosome[k],2) == (i+1):
						indice_periods.append(k)
						n+=1
					k+=1

				if (n > j+1):
					del chromosome[indice_periods[len(indice_periods)-1]]
					chromosome.insert(indice_periods[len(indice_periods)-1], '0')

				j+=1

			i+=1
		
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

			print("Population {0} : ".format(it), self.population )
			print(" ")

			list_fitnesses1 = []
			sum_fitness = 0
			i = 0 
			while i < len(self.population):
				#print("Population One i :", self.population[i], " Iteration : ", it)
				fitness = self.getChromosomeFitness(self.population[i])
				list_fitnesses1.append(fitness)
				sum_fitness += fitness
				i+=1

			list_fitnesses2 = []
			cumul_percentage = 0
			i = 0
			while i < len(list_fitnesses1):
				fitness = list_fitnesses1[i]
				percentage = (fitness *100)/float(sum_fitness)
				cumul_percentage += percentage
				list_fitnesses2.append(cumul_percentage)
				i+=1

			
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

				chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

				if chromosome3 not in population:
					population.append(chromosome3)
					i += 1

				if (i == GeneticAlgorithm.NbPopulation):
					break

				if chromosome4 not in population:
					population.append(chromosome4)
					i += 1

				if (i == GeneticAlgorithm.NbPopulation):
					break

			self.population = []
			i = 0
			while i < len(population):
				self.population.append(self.applyMutationto(population[i]))
				#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
				i+=1		

			print("Population Suite {0} : ".format(it), self.population )
			print(" ")

			#print("C1 : ",chromosome1," C2 : ",chromosome2)

			it +=1


	def initPopulation1(self):

		self.population = []

		listItems = []

		i = 0
		while i < self.instance.nbItems:
			listItems.append(i+1)
			i+=1

		# i generate the differents permutations out of the list of items, this will determine the order in which the items will be placed in the chromosome
		list_permutations = list(permutations(listItems))

		i = 0
		while i < len(list_permutations) and len(self.population) <= 10:

			one_permutation = list(list_permutations[i])

			# i create a chromosome and fill it with some zeros
			chromosome = []
			j = 0
			while j < self.instance.nbTimes:
				chromosome.append('0')
				j+=1

			#print(chromosome)

			quality_chroms = True
			j = 0
			while j < len(one_permutation):

				product = one_permutation[j]

				#print("PRODUCT : ", product)

				demandProductPeriods = getDemandPeriods(self.instance.demandsGrid[product-1])

				#print("DEMANDS : ", demandProductPeriods)

				k = 0
				while k < len(demandProductPeriods):

					place_found = False
					l = demandProductPeriods[k]
					while l >= 0:

						if (int(chromosome[l],2) == 0):
							del chromosome[l]
							chromosome.insert(l,(str(bin(product))[2:]))
							place_found = True
							break

						l-=1

					if (place_found is False):
						quality_chroms = False
						break


					k+=1 

				if (quality_chroms is False):
					#print("FALSE CHROMOSOME : ", chromosome)
					break
				#print("TRUE CHROMOSOME : ", chromosome)

				j+=1

			if (quality_chroms is True):
				self.population.append(chromosome)

			i+=1
		#print(self.population)

	def printResults(self):

		chromosome = self.population[0]
		best_fitness = (1.0/self.getChromosomeFitness(chromosome))
		i = 1
		while i < len(self.population):
			fitness = self.getChromosomeFitness(self.population[i])
			#print("chromosome : ", self.population[i], " Fitness : ", fitness)
			if ((1.0/fitness) < best_fitness):
				best_fitness = 1.0 / fitness 
				chromosome = self.population[i]
			i+=1

		r_chromosome = []
		i = 0
		while i < len(chromosome):
			r_chromosome.append(int(chromosome[i],2))
			i+=1

		print("The best solution found so far is : ", r_chromosome)
		print("The fitness of this solution is : ", best_fitness)