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
	MigrationRate = 0
	slaveThreadsManager = 0

	# builder 
	def __init__(self):
		
		self.chromosomes = []
		self.listFitnessData = []
		self.lacksDiversity = False
		self.thread_memory = []


	def initialize(self, indiceMigration, previousPopulation):
		
		retVal = 0 # variable to be returned at the end

		popLocker = threading.Lock()
		self.startPopData = copy.deepcopy(previousPopulation.startPopData)
		self.thread_memory = previousPopulation.thread_memory

		# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
		if previousPopulation.lacksDiversity:

			#print(" CONVERGENCE : ", self.startingPopulation.chromosomes)
			chromosome = copy.deepcopy(previousPopulation.chromosomes[0])
			
			# i store this local optima in the genetic algorithm's memory to remind me that it's already been visited before
			Population.gaMemoryLocker.acquire()

			if chromosome not in Population.ga_memory:
				Population.ga_memory.append(copy.deepcopy(chromosome))
				self.thread_memory.append(copy.deepcopy(chromosome))
				
			Population.gaMemoryLocker.release()

			chromosome.advmutate()
			
			if chromosome != previousPopulation.chromosomes[0]:
				
				if chromosome not in self.thread_memory:
					previousPopulation.chromosomes[0] = chromosome

					retVal = 1 # this signals it's time for migration

				else:

					self.chromosomes = []
					self.listFitnessData = []
					self.lacksDiversity = False
					return retVal

			else:  

				#if chromosome in self.startingPopulation.chromosomes:
				#	self.startingPopulation.chromosomes.remove(chromosome)

				i = 0
				startPopSize = len(self.startPopData[0])
				while i < startPopSize:
					if chromosome == (self.startPopData[0])[i]:
						del (self.startPopData[0])[i]
						del (self.startPopData[1])[i]
						break
					i += 1

				previousPopulation = Population()
				previousPopulation.chromosomes = list(self.startPopData[0])
				previousPopulation.listFitnessData = list(self.startPopData[1])
				#print("Starting population : ", self.startingPopulation," and ", previousPopulation)
				
			previousPopulation.getFitnessData() # i make calculations over the resulting population

		#print(" Memory : ", Population.ga_memory)
		
		if len(previousPopulation.chromosomes) == 1:

			self.chromosomes = []
			self.listFitnessData = []
			self.lacksDiversity = False
			return retVal
		
		#print("Starting population : ", self.startPopData[0])
		#print ("population inter : ", previousPopulation)
		#print " Percentage : ", previousPopulation.listFitnessData
		# i perform the roulette-wheel method to select the parents
		self.chromosomes = []
		self.chromosomes.append(copy.deepcopy(previousPopulation.chromosomes[0])) # i add the best chromosome of the previous population to the current population

		prevPopData = []
		prevPopData.append(copy.deepcopy(previousPopulation.chromosomes))
		prevPopData.append(copy.deepcopy(previousPopulation.listFitnessData))

		while True:
			
			popLocker.acquire()

			if len(self.chromosomes) >= len(previousPopulation.chromosomes):
				self.getFitnessData()
				popLocker.release()	
				break

			popLocker.release()
			
			randValue1 = randint(1,99)
			randValue2 = randint(1,99)

			#print(randValue1, randValue2, " memory : ", Population.ga_memory, " and ", self.chromosomes)

			Population.slaveThreadsManager.performCrossOver(copy.deepcopy(prevPopData), self, popLocker, randValue1, randValue2)

			#time.sleep(0.005)

		indiceMigration += 1

		if Population.MigrationRate != 0 and indiceMigration == Population.MigrationRate:
			retVal = 1 # this signals it's time for migration
			indiceMigration = 0

		return retVal

	def __repr__(self):
		
		#print("Nb : ", self.NbPopulation, self.chromosomes)
		result = ""
		i = 0
		while i < len(self.chromosomes):

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

	def insertChomosome(self, chromosome):

		if chromosome not in self.chromosomes:

			popSize = len(self.chromosomes)
			if (self.chromosomes == []):

				self.chromosomes.append(copy.deepcopy(chromosome))
		
			elif popSize == 1 and (self.chromosomes[0]).fitnessValue == 0:

				self.chromosomes.append(copy.deepcopy(chromosome))

			else:

				# i sort the list of zeroperiods from the most convenient place to the least convenient one
				prevValue = 0
				j = 0
				found = False
				while j < popSize:

					if chromosome.fitnessValue >= prevValue and chromosome.fitnessValue <= (self.chromosomes[j]).fitnessValue:
						found = True
						self.chromosomes = self.chromosomes[:j] + [copy.deepcopy(chromosome)] + self.chromosomes[j:]
						break

					prevValue = (self.chromosomes[j]).fitnessValue

					j += 1

				if found is False:
					self.chromosomes.append(copy.deepcopy(chromosome))

			# After inserting a new good chromosome into the population, i remove a bad one
			del self.chromosomes[popSize-1]

	def getImproved(self):

		for chromosome in self.chromosomes:
			c = copy.deepcopy(chromosome)
			c.advmutate()

			if c not in self.chromosomes:
				self.insertChomosome(c)

	def getFitnessData(self):

		popSize = len(self.chromosomes)
		
		if popSize > 0 and self.listFitnessData == []:

			sumAllFitnessValues = 0
			tmpSumFitness = 0 #variable used to quantify the lack of diversity in the population
			max_fitness = (self.chromosomes[len(self.chromosomes)-1]).fitnessValue

			
			i = 0
			while i < popSize:
				
				chromosome = self.chromosomes[i]
				temp = chromosome.fitnessValue

				value = (max_fitness-temp)
				tmpSumFitness += value

				value += Population.FITNESS_PADDING
				self.listFitnessData.append(value)
				sumAllFitnessValues += value

				i += 1
			
			#print(" Fitness Data 1 : ", self.listFitnessData)

			if tmpSumFitness == 0:
				self.lacksDiversity = True
			#else:
			#	self.listFitnessData = []
			#	return

			i = 0
			percentage = 0
			while i < popSize:
				temp = self.listFitnessData[i]
				del self.listFitnessData[i]
				if sumAllFitnessValues == 0:
					percentage = 0
				else:
					percentage += (float(temp)/float(sumAllFitnessValues))*100
				#print (" FOO : temp : ", temp, " sumFitness : ", sumFitness, " percentage : ", percentage)
				self.listFitnessData.insert(i, percentage)
				i += 1

			#print("listFitnessData : ", self.listFitnessData)

		#print(" Fitness Data 2 : ", self.listFitnessData)

class Node:

	def __init__(self):

		self.solution = []
		self.currentItem = 0
		self.currentPeriod = 0
		self.itemCounter = 0
		self.fitnessValue = 0

	def __repr__(self):
		return "Chromosome : " + str(self.solution) + ", " + str(self.fitnessValue)
		#" Current Item : " + str(self.currentItem) + " Current Period : " + str(self.currentPeriod) + " Item Counter : " + str(self.itemCounter) + " Fitness value : " + 

	def isLeaf(self):
		
		if self.itemCounter == Chromosome.problem.nbItems and self.currentPeriod == len(Chromosome.problem.deadlineDemandPeriods[self.currentItem-1]):
			return True
		return False