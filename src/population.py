#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from chromosome import *

class Population:

	NbMaxPopulation = 0
	FITNESS_PADDING = 0
	crossOverRate = 0
	ga_memory = []
	gaMemoryLocker = 0
	MigrationRate = 0
	crossOverRate = 0

	# builder 
	def __init__(self):
		
		self.chromosomes = []
		self.listFitnessData = []
		self.lacksDiversity = False
		self.locker = threading.Lock()
		self.previousPopulation = 0
		self.slaveThreadsManager = 0

	def initialize(self, previousPopulation):
		
		self.slaveThreadsManager = previousPopulation.slaveThreadsManager

		self.previousPopulation = previousPopulation

		# i perform the roulette-wheel method to select the parents
		self.chromosomes = []
		self.chromosomes.append(copy.deepcopy(previousPopulation.chromosomes[0])) # i add the best chromosome of the previous population to the current population

		self.prevPopData = []
		self.prevPopData.append(copy.deepcopy(previousPopulation.chromosomes))
		self.prevPopData.append(copy.deepcopy(previousPopulation.listFitnessData))

		self.slaveThreadsManager.crossoverPop(self)
		#self.chromosomes.sort()

	def __repr__(self):
		
		#print("Nb : ", self.NbPopulation, self.chromosomes)
		result = ""
		i = 0
		while i < len(self.chromosomes):

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

	def replace(self, chromosome):

		self.locker.acquire()

		if chromosome not in self.chromosomes:

			self.chromosomes.append(copy.deepcopy(chromosome))

			# After inserting a new good chromosome into the population, i remove a bad one
			del self.chromosomes[len(self.chromosomes)-1]

		self.locker.release()

	def getImproved(self):

		self.slaveThreadsManager.improvePop(self.chromosomes)
		self.chromosomes.sort()
		self.listFitnessData = []

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
			
			self.fitnessMean = math.floor(sumAllFitnessValues / popSize)

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

	#--------------------
	# function : mate
	# Class : SlaveThread
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------

	def mate(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		#print(Population.crossOverRate)
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

			chromosome3 = Chromosome()
			chromosome3.init2(solution3, ranks3)
			#chromosome3.advmutate()

			chromosome4 = Chromosome()
			chromosome4.init2(solution4, ranks4)
			#chromosome4.advmutate()

			#print(" 2 - solution3 : ", chromosome3.solution, " ranks3 : ", ranks3, " solution4 : ", chromosome4.solution, " ranks4 : ", ranks4)
			

		else:
			chromosome3 = copy.deepcopy(chromosome1)
			chromosome4 = copy.deepcopy(chromosome2)

		return chromosome3, chromosome4


	def crossover(self, randValue1, randValue2):

		#print("applyCrossOver 1 : ", randValue1, randValue2, len(previousPopulation.chromosomes), " Statistics : ", len(previousPopulation.listFitnessData))
		#print("applyCrossOver 2 : ", randValue1, randValue2, previousPopulation.chromosomes, " Statistics : ", previousPopulation.listFitnessData)

		j = 0
		lbound = 0
		while j < len(self.previousPopulation.listFitnessData):
			if (randValue1 >= lbound and randValue1 <= self.previousPopulation.listFitnessData[j]):
				chromosome1 = self.previousPopulation.chromosomes[j]
			if (randValue2 >= lbound and randValue2 <= self.previousPopulation.listFitnessData[j]):
				chromosome2 = self.previousPopulation.chromosomes[j]
			lbound = self.previousPopulation.listFitnessData[j]
			j += 1

		#print("Parent 1 : ", chromosome1, "Parent 2 : ", chromosome2)
		
		chromosome3,chromosome4 = self.mate(chromosome1,chromosome2)

		#print("Inter : Child 3 : ", chromosome3, " Child 4 : ", chromosome4)
		
		# In the following lines, i intend to select the best two chromosomes out of both the parents and the generated offsprings
		tempList = []
		tempList.append(chromosome1)  
		tempList.append(chromosome2)
		tempList.append(chromosome3)
		tempList.append(chromosome4)

		chromosome3, chromosome4 = getBestChroms(tempList)

		#print("Finals : Child 3 : ", chromosome3, " Child 4 : ", chromosome4)

		#print(" Resulting Child 3 : ", chromosome3, " Resulting Child 4 : ", chromosome4)
		
		self.insert(chromosome3)
		self.insert(chromosome4)

		#print ("pop : ", nextPopulation.chromosomes)

	def crossPopulation(self):

		prevPopData = copy.deepcopy(self.prevPopData)
		previousPopulation = Population()
		previousPopulation.chromosomes = copy.deepcopy(prevPopData[0])
		previousPopulation.listFitnessData = copy.deepcopy(copy.deepcopy(prevPopData[1]))

		while True:
			
			self.locker.acquire()

			if len(self.chromosomes) >= len(previousPopulation.chromosomes):
				self.chromosomes.sort()
				self.getFitnessData()
				self.locker.release()	
				break

			self.locker.release()
			
			randValue1 = randint(1,99)
			randValue2 = randint(1,99)

			#print(randValue1, randValue2, " memory : ", Population.ga_memory, " and ", self.chromosomes)

			self.crossover(randValue1, randValue2)

	def insert(self, chromosome):

		# Get lock to synchronize threads
		self.locker.acquire()
		popSize = len(self.chromosomes)

		limit = Population.NbMaxPopulation

		if self.previousPopulation != 0:
			limit = len(self.previousPopulation.chromosomes)
		
		if popSize >= limit:
			self.chromosomes.sort()
			self.getFitnessData()
			self.locker.release()
			return 

		
		if self.previousPopulation != 0:
			chromosome.mutate()
		else:
			if chromosome in self.chromosomes:
				self.locker.release()
				return

		self.chromosomes.append(copy.deepcopy(chromosome))

		#print("Yes ", population.chromosomes)
		# Free lock to release next thread
		self.locker.release()