#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from chromosome import *

class Population:

	NbMaxPopulation = 0
	FITNESS_PADDING = 0
	crossOverRate = 0
	stopFlag = []
	ga_memory = []

	# builder 
	def __init__(self):
		
		self.chromosomes = []
		self.max_fitness = 0
		self.min_fitness = pow(10,6)
		self.NbPopulation = 0
		self.listFitnessData = []
		self.sumAllFitnessValues = 0
		self.elite = []
		self.lacksDiversity = False
		self.thread_memory = []
		self.startingPopulation = 0


	def initialize(self, previousPopulation, locker):
		
		# i select the two chromosomes that'll be mated to produce offsprings
		#print " population 1 : ", previousPopulation#, " starting with :", Population.startingPopulation
		self.thread_memory = previousPopulation.thread_memory
		self.startingPopulation = previousPopulation.startingPopulation

		# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
		if previousPopulation.lacksDiversity:

			#print(" CONVERGENCE !!!")
			chromosome = copy.copy(previousPopulation.chromosomes[0])
			
			# i store this local optima in the genetic algorithm's memory to remind it that it's already visit the solution
			locker.acquire()

			if chromosome not in Population.ga_memory:
				Population.ga_memory.append(copy.deepcopy(chromosome))
				self.thread_memory.append(copy.deepcopy(chromosome))

			locker.release()

			chromosome.advmutate()
			
			if chromosome != previousPopulation.chromosomes[0]:
				del previousPopulation.chromosomes[0]
				previousPopulation.chromosomes.insert(0, chromosome)
				#print (" different !")

			else:  

				#print(" from start to now!")
				#print " not different ! 1 ", Population.startingPopulation 
				i = 0
				while i < self.startingPopulation.NbPopulation:

					if chromosome == self.startingPopulation.chromosomes[i]:
						del self.startingPopulation.chromosomes[i]

						# i decrease the number of the chromosomes of the population
						self.startingPopulation.NbPopulation -= 1

						break
					i+=1

				#print " not different ! 2 ", Population.startingPopulation
				previousPopulation = copy.copy(self.startingPopulation)
				#print("Starting population : ", self.startingPopulation," and ", previousPopulation)

			previousPopulation.getFitnessData() # i make calculations over the resulting population
			previousPopulation.getElite()

		#print(" Memory : ", Population.ga_memory)
			
		self.NbPopulation = previousPopulation.NbPopulation
		
		if previousPopulation.NbPopulation == 1:

			self.chromosomes = []
			self.max_fitness = 0
			self.min_fitness = pow(10,6)
			self.NbPopulation = 0
			self.listFitnessData = []
			self.sumAllFitnessValues = 0
			self.elite = []
			self.lacksDiversity = False
			return
		

		#print " population 2 : ", previousPopulation #, " starting with :", Population.startingPopulation
		#print " Percentage : ", previousPopulation.listFitnessData

		# i perform the roulette-wheel method to select the parents
		chromosomes = []
		chromosomes.append(previousPopulation.elite) # i add the best chromosome of the previous population to the current population

		i = 1
		while i < previousPopulation.NbPopulation:

			rand_prob1 = randint(1,99)
			rand_prob2 = randint(1,99)

			#print(" rand 1 : ", rand_prob1, " rand_prob2 : ", rand_prob2)
			j = 0
			lbound = 0
			while j < previousPopulation.NbPopulation:
				if (rand_prob1 >= lbound and rand_prob1 <= previousPopulation.listFitnessData[j]):
					chromosome1 = previousPopulation.chromosomes[j]
				if (rand_prob2 >= lbound and rand_prob2 <= previousPopulation.listFitnessData[j]):
					chromosome2 = previousPopulation.chromosomes[j]
				lbound = previousPopulation.listFitnessData[j]
				j += 1

			#print("Parent 1 : ", chromosome1, "Parent 2 : ", chromosome2)

			chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

			#print("Child 3 : ", chromosome3, " Child 4 : ", chromosome4)

			# In the following lines, i intend to select the best two chromosomes out of both the parents and the generated offsprings
			tempList = []
			tempList.append(chromosome1)  
			tempList.append(chromosome2)
			tempList.append(chromosome3)
			tempList.append(chromosome4)

			chromosome3, chromosome4 = getBestChroms(tempList)

			#print(" Resulting Child 3 : ", chromosome3, " Resulting Child 4 : ", chromosome4)

			#if self.isFeasible(chromosome3) is False or self.isFeasible(chromosome4) is False:
			#	print("c3 : ", c3, " c4 : ", c4)

			if chromosome3 not in Population.ga_memory:
				chromosomes.append(chromosome3)
				i += 1

			if (i == self.NbPopulation):
				break

			if chromosome4 not in Population.ga_memory:
				chromosomes.append(chromosome4)
				i += 1

			if (i == self.NbPopulation):
				break

		#print("Population inter : ", chromosomes)
		#print(" ")

		self.chromosomes = []
		self.max_fitness = 0

		i = 0
		while i < self.NbPopulation:
			chromosome = chromosomes[i]
			chromosome.mutate()

			#if chromosome.fitnessValue == 0:
			#	print(" Chromosome : ", chromosome.solution, chromosome.itemsRank)

			if chromosome not in Population.ga_memory:
				self.chromosomes.append(chromosome)
			else:
				self.chromosomes.append(chromosomes[i])

			#if chromosome.fitnessValue == 375 and chromosome.solution != [0, 2, 2, 2, 3, 1, 0, 1]:
			#	print("1 : ", chromosome.solution, chromosome.fitnessValue )

			value = chromosome.fitnessValue
			if value > self.max_fitness:
				self.max_fitness = value

			# i want to store the best chromosome of the population
			if value < self.min_fitness:
				self.min_fitness = value
				self.elite = copy.copy(chromosome)

			#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
			i+=1	

		#print " population 3 : ", self #, " starting with :", Population.startingPopulation
		#print " "
		# When the entire population has been formed, then i compute some statistic data on the given population
		self.getFitnessData()	

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

			randomIndice = randint(1,Chromosome.problem.nbTimes-1)

			#print(" ")

			#print(" 1 - solution1 : ", chromosome1.solution, " ranks1 : ", chromosome1.itemsRank, " solution2 : ", chromosome2.solution, " ranks2 : ", chromosome2.itemsRank)
			#print(" randomIndice : ", randomIndice)
			#print(" ranks1 : ", ranks1, " ranks2 : ", ranks2)

			
			solution3 = chromosome1.solution[:randomIndice]
			solution4 = chromosome2.solution[:randomIndice]

			ranks3 = ranks1[:randomIndice]
			ranks4 = ranks2[:randomIndice]


			solution3 += chromosome2.solution[randomIndice:]
			solution4 += chromosome1.solution[randomIndice:]

			ranks3 += ranks2[randomIndice:]
			ranks4 += ranks1[randomIndice:]

			# Once, the two resulting chromosomes have been formed, i make each of them feasible with regards of the constraints

			#print(" randomIndice : ", randomIndice)
			#print(" 2 - solution3 : ", solution3, " ranks3 : ", ranks3, " solution4 : ", solution4, " ranks4 : ", ranks4)

			chromosome3 = Chromosome(solution3, ranks3)
			chromosome3.getFeasible()
			#chromosome3.advmutate()

			chromosome4 = Chromosome(solution4, ranks4)
			chromosome4.getFeasible()
			#chromosome4.advmutate()

			#print(" 2 - solution3 : ", chromosome3.solution, " ranks3 : ", ranks3, " solution4 : ", chromosome4.solution, " ranks4 : ", ranks4)

		else:
			chromosome3 = Chromosome(chromosome1.solution)
			chromosome4 = Chromosome(chromosome2.solution)

		return chromosome3,chromosome4

	def __repr__(self):
		
		#print("Nb : ", self.NbPopulation, self.chromosomes)
		result = ""
		i = 0
		while i < self.NbPopulation:

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

	def getFitnessData(self):

		self.sumAllFitnessValues = 0
		tmpSumFitness = 0 #variable used to quantify the lack of diversity in the population
		self.listFitnessData = []

		i = 0
		while i < self.NbPopulation:
			#print(" i : ", i)
			chromosome = self.chromosomes[i]
			temp = chromosome.fitnessValue

			value = (self.max_fitness-temp)
			tmpSumFitness += value

			value += Population.FITNESS_PADDING
			self.listFitnessData.append(value)
			self.sumAllFitnessValues += value

			i += 1

		#print(" Fitness Data 1 : ", self.listFitnessData)

		if tmpSumFitness == 0:
			self.lacksDiversity = True

		i = 0
		percentage = 0
		while i < self.NbPopulation:
			temp = self.listFitnessData[i]
			del self.listFitnessData[i]
			if self.sumAllFitnessValues == 0:
				percentage = 0
			else:
				percentage += (float(temp)/float(self.sumAllFitnessValues))*100
			#print (" FOO : temp : ", temp, " sumFitness : ", sumFitness, " percentage : ", percentage)
			self.listFitnessData.insert(i, percentage)
			i += 1

		#print(" Fitness Data 2 : ", self.listFitnessData)
		
	def getElite(self):
		
		self.min_fitness = pow(10,6)
		for chromosome in self.chromosomes:
			value = chromosome.fitnessValue
			if value < self.min_fitness:
				self.min_fitness = value
				self.elite = chromosome

class Node:

	def __init__(self):

		self.solution = []
		self.currentItem = 0
		self.currentPeriod = 0
		self.itemCounter = 0

	def __repr__(self):
		return " Chromosome : " + str(self.solution) + " Current Item : " + str(self.currentItem) + " Current Period : " + str(self.currentPeriod) + " Item Counter : " + str(self.itemCounter)

	def isLeaf(self):
		
		if self.itemCounter == Chromosome.problem.nbItems and self.currentPeriod == len(Chromosome.problem.deadlineDemandPeriods[self.currentItem-1]):
			return True
		return False