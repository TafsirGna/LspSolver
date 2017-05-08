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
		self.listFitnessData = []
		self.lacksDiversity = False
		self.thread_memory = []
		self.slaveThreadsManager = 0


	def initialize(self, previousPopulation):
		
		popLocker = threading.Lock()
		self.startPopData = copy.deepcopy(previousPopulation.startPopData)

		# i select the two chromosomes that'll be mated to produce offsprings
		self.thread_memory = previousPopulation.thread_memory

		self.slaveThreadsManager = previousPopulation.slaveThreadsManager

		# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
		if previousPopulation.lacksDiversity:

			#print(" CONVERGENCE : ", self.startingPopulation.chromosomes)
			chromosome = copy.deepcopy(previousPopulation.chromosomes[0])
			
			# i store this local optima in the genetic algorithm's memory to remind it that it's already visit the solution
			Population.gaMemoryLocker.acquire()

			if chromosome not in Population.ga_memory:
				Population.ga_memory.append(copy.deepcopy(chromosome))
				self.thread_memory.append(copy.deepcopy(chromosome))

			Population.gaMemoryLocker.release()

			chromosome.advmutate()
			
			if chromosome != previousPopulation.chromosomes[0]:
				
				if chromosome not in self.thread_memory:
					del previousPopulation.chromosomes[0]
					previousPopulation.chromosomes.insert(0, chromosome)
					#print (" different !")
				else:

					self.chromosomes = []
					self.listFitnessData = []
					self.lacksDiversity = False
					return

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
			return
		
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

			self.slaveThreadsManager.performCrossOver(copy.deepcopy(prevPopData), self, popLocker, randValue1, randValue2)

			#time.sleep(0.005)
		#self.getFitnessData()

		# When the entire population has been formed, then i compute some statistic data on the given population

	def __repr__(self):
		
		#print("Nb : ", self.NbPopulation, self.chromosomes)
		result = ""
		i = 0
		while i < len(self.chromosomes):

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

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