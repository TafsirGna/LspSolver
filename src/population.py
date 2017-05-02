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
	gaMemoryLocker = 0

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
		self.slaveThreadsManager = 0


	def initialize(self, previousPopulation):
		
		popLocker = threading.Lock()

		# i select the two chromosomes that'll be mated to produce offsprings
		#print " population 1 : ", previousPopulation#, " starting with :", Population.startingPopulation
		self.thread_memory = previousPopulation.thread_memory
		self.startingPopulation = previousPopulation.startingPopulation
		self.slaveThreadsManager = previousPopulation.slaveThreadsManager

		# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
		if previousPopulation.lacksDiversity:

			#print(" CONVERGENCE !!!")
			chromosome = copy.copy(previousPopulation.chromosomes[0])
			
			# i store this local optima in the genetic algorithm's memory to remind it that it's already visit the solution
			#locker.acquire()

			if chromosome not in Population.ga_memory:
				Population.ga_memory.append(copy.deepcopy(chromosome))
				self.thread_memory.append(copy.deepcopy(chromosome))

			#locker.release()

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
			
		self.NbPopulation = 0 #previousPopulation.NbPopulation
		
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
		self.chromosomes = []
		self.chromosomes.append(copy.copy(previousPopulation.elite)) # i add the best chromosome of the previous population to the current population
		self.elite = copy.copy(previousPopulation.elite)
		self.NbPopulation += 1
		self.max_fitness = previousPopulation.elite.fitnessValue
		self.min_fitness = previousPopulation.elite.fitnessValue

		while True:

			popLocker.acquire()

			if self.NbPopulation >= previousPopulation.NbPopulation:
				break

			popLocker.release()

			randValue1 = randint(1,99)
			randValue2 = randint(1,99)

			#print(randValue1, randValue2)

			self.slaveThreadsManager.performCrossOver(previousPopulation, self, popLocker, randValue1, randValue2)
			#print("nb1 : ", self.NbPopulation, previousPopulation.NbPopulation, self.chromosomes)

		#print("yes in : ", self.chromosomes, ", Elite : ", self.elite)
		#print("Population inter : ", chromosomes)

		'''
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
		'''
		# When the entire population has been formed, then i compute some statistic data on the given population
		self.getFitnessData()	

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