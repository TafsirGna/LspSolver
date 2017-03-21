#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *
from chromosome import *

class Population:

	nbInitIterations = 0
	nbIterations = 0
	NbMaxPopulation = 0
	FITNESS_PADDING = 0
	crossOverRate = 0
	ManufactItemsPeriods = []

	# builder 
	def __init__(self, previousPopulation = []):
		
		self.chromosomes = []
		self.bestChromosome = 0
		self.max_fitness = 0
		self.NbPopulation = 0
		self.min_fitness = math.pow(10,6)

		# i explicit the case where there's no previous population before this one
		if previousPopulation == [] :

			listItems = []

			# i fill the listItem object with the number of the different items
			i = 0
			while i < Chromosome.problem.nbItems:
				listItems.append(i+1)
				i+=1

			# i generate the differents permutations out of the list of items, this will determine the order in which the items will be placed in the chromosome
			list_permutations = list(permutations(listItems))

			i = 0
			while i < Population.nbInitIterations:

				j = 0
				while j < len(list_permutations):

					permutationJ = list_permutations[j] 
					#print(" - ", i, " permutation : ", permutationJ)

					# i create a chromosome and fill it with some zeros
					solution = []
					k = 0
					while k < Chromosome.problem.nbTimes:
						solution.append(0)
						k+=1

					qual_sol = True # boolean variable that determines if the chromosome being formed is good or not

					k = 0
					while k < len(permutationJ):

						itemK = permutationJ[k]
						itemKDemandPeriods = Chromosome.problem.deadlineDemandPeriods[itemK-1]

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
					if qual_sol is True and c not in self.chromosomes:
						c.getFeasible()
						self.chromosomes.append(c)

						# i store the value of the highest value of the objective function
						value = c.valueFitness
						if value > self.max_fitness:
							self.max_fitness = value

						# i store the best chromosome from this population
						if value < self.min_fitness:
							self.bestChromosome = c
							self.min_fitness = value

						# i check that the size of the population don't exceed the maximum number of population retained
						if len(self.chromosomes)>=Population.NbMaxPopulation:
							self.NbPopulation = len(self.chromosomes)
							return

				i+=1

			self.NbPopulation = len(self.chromosomes)

			#print(len(self.chromosomes))

		else:

			# i select the two chromosomes that'll be mated to produce offsprings
			print("Population : ", previousPopulation)
			print(" ")

			self.NbPopulation = previousPopulation.NbPopulation

			sumFitness = 0
			tempSumFitness = 0 # variable used to quantify the lack of diversity in the population
			listFitness = []
			i = 0
			while i < len(previousPopulation.chromosomes):
				#print(" i : ", i)
				chromosome = previousPopulation.chromosomes[i]
				temp = chromosome.valueFitness

				value = (previousPopulation.max_fitness-temp)
				tempSumFitness += value

				value += Population.FITNESS_PADDING
				listFitness.append(value)
				sumFitness += value
				i += 1

			# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
			if tempSumFitness == 0:
				# TODO
				chromosome = previousPopulation.chromosomes[0]
				del previousPopulation.chromosomes[0]
				chromosome.mutate()
				previousPopulation.chromosomes.insert(0, chromosome)

			#print ("Fitness 1 : ", listFitness)
			#print(" ")

			i = 0
			percentage = 0
			while i < len(previousPopulation.chromosomes):
				temp = listFitness[i]
				del listFitness[i]
				percentage += (float(temp)/float(sumFitness))*100
				#print (" FOO : temp : ", temp, " sumFitness : ", sumFitness, " percentage : ", percentage)
				listFitness.insert(i, percentage)
				i += 1

			#print ("Fitness 2 : ", listFitness, " MAX_FITNESS : ", GeneticAlgorithm.MAX_FITNESS)
			#print(" ")

			#print(listFitness)

			# i perform the roulette-wheel method to select the parents
			chromosomes = []
			i = 0
			while i < previousPopulation.NbPopulation:

				rand_prob1 = randint(1,99)
				rand_prob2 = randint(1,99)

				#print(" rand 1 : ", rand_prob1, " rand_prob2 : ", rand_prob2)
				j = 0
				lbound = 0
				while j < len(listFitness):
					if (rand_prob1 >= lbound and rand_prob1 <= listFitness[j]):
						chromosome1 = previousPopulation.chromosomes[j]
					if (rand_prob2 >= lbound and rand_prob2 <= listFitness[j]):
						chromosome2 = previousPopulation.chromosomes[j]
					lbound = listFitness[j]
					j += 1

				#print("CrossOver : ", random_chrom1, " and : " , random_chrom2)

				chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

				#if self.isFeasible(chromosome3) is False or self.isFeasible(chromosome4) is False:
				#	print("c3 : ", c3, " c4 : ", c4)

				chromosomes.append(chromosome3)
				i += 1

				if (i == self.NbPopulation):
					break

				chromosomes.append(chromosome4)
				i += 1

				if (i == self.NbPopulation):
					break

			print("Population inter : ", chromosomes)
			print(" ")

			self.chromosomes = []
			self.max_fitness = 0
			self.min_fitness = math.pow(10,6)

			i = 0
			while i < len(chromosomes):
				chromosome = chromosomes[i]
				chromosome.mutate()
				self.chromosomes.append(chromosome)

				value = chromosome.valueFitness
				if value > self.max_fitness:
					self.max_fitness = value

				# i store the best chromosome from this population
				if value < self.min_fitness:
					self.bestChromosome = chromosome
					self.min_fitness = value

				#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
				i+=1		

			#print("Population Suite {0} : ".format(it), self.population )
			#print(" ")

			#print("C1 : ",chromosome1," C2 : ",chromosome2)

	#--------------------
	# function : applyCrossOverto
	# Class : GeneticAlgorithm
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------

	def applyCrossOverto(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		if (randint(0,100) < (Population.crossOverRate*100)):

			# i retrieve a table that stores the period each item has been manufactered for
			ranks1 = chromosome1.itemsRank
			ranks2 = chromosome2.itemsRank

			ranks3 = []
			ranks4 = []

			randomIndice = randint(1,len(chromosome1.solution)-1)

			#print(" ")
			#print(" chromosome1 : ", chromosome1, " chromosome2 : ", chromosome2)
			#print(" randomIndice : ", randomIndice)
			#print(" ranks1 : ", ranks1, " ranks2 : ", ranks2)

			i = 0
			while i < len(chromosome1.solution):

				if i < randomIndice:

					solution3.append(chromosome1.solution[i])
					solution4.append(chromosome2.solution[i])

					ranks3.append(ranks1[i])
					ranks4.append(ranks2[i])

				else:

					solution3.append(chromosome2.solution[i])
					solution4.append(chromosome1.solution[i])

					ranks3.append(ranks2[i])
					ranks4.append(ranks1[i])

				i+=1

			# Once, the two resulting chromosomes have been formed, i make each of them feasible with regards of the constraints

			#print(" randomIndice : ", randomIndice)
			#print(" 1 - solution3 : ", solution3, " ranks3 : ", ranks3, " solution4 : ", solution4, " ranks4 : ", ranks4)

			chromosome3 = Chromosome(solution3, ranks3)
			chromosome3.getFeasible()

			chromosome4 = Chromosome(solution4, ranks4)
			chromosome4.getFeasible()

			#print(" 2 - solution3 : ", chromosome3.solution, " ranks3 : ", ranks3, " solution4 : ", chromosome3.solution, " ranks4 : ", ranks4)

		else:
			chromosome3 = Chromosome(chromosome1.solution)
			chromosome4 = Chromosome(chromosome2.solution)

		return chromosome3,chromosome4

	'''
	def applyCrossOverto(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		if (randint(0,100) < (Population.crossOverRate*100)):

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
	'''


	def __repr__(self):
		
		result = ""
		i = 0
		while i < len(self.chromosomes):

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.valueFitness) + " , "

			i+=1

		return result
