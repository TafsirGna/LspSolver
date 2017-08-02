#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_slave_thread import *

#--------------------
# Class : ClspThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class ClspThread(Thread):

	listMainThreads = 0
	NumberOfMigrants = 0
	NbGenToStop = 0
	crossOverRate = 0
	MigrationRate = 0
	NbMaxPopulation = 0
	FITNESS_PADDING = 0

	def __init__(self, threadId, queue):

		Thread.__init__(self)
		self.threadId = threadId
		self.name = "Thread - " + str(threadId)
		self.queue = queue
		self.locker = threading.Lock()
		self.NbGenerations = 0
		self.readyFlag = 0
		self.readyFlagId = 0
		self.readyEvent = Event()
		self.action = 1
		self.finished = False
		self.result = 0
		self.memory = []
		self.popLackingDiversity = False

		self.chromosomes = []
		self.initialChromosomes = []
		self.listFitnessData = []
		self.initialChromData = []
		self.prevChromosomes = []
		self.prevListFitnessData = []

		self.immigrants = []
		self.slaveThreadsManager = SlaveThreadsManager(self) # i initialize a list that's intended to contain all the population's initialization threads 

	def run(self):
		
		if self.action == 1:

			self.slaveThreadsManager.initPop()
			#print (self.name, " ", "Initial Population : ", self.population)
			
			self.getPopImproved()
			self.getFitnessData()
			print (self.name, " ", "Initial Population : ", self.chromosomes)
			print (self.name, " ", "Population Data: ", self.listFitnessData)
			self.initialChromosomes = copy.deepcopy(self.chromosomes)
			self.initialChromData = copy.deepcopy(self.listFitnessData)

			
			# i send the best chromosomes of the population to its neighbors
			self.sendMigrants()

			if self.threadId != 0:
				self.readyFlag.wait()

			if self.chromosomes == []:
				self.action = -1
				self.finished = True
			else:
				self.action = 2

			self.readyFlag = 0
			self.readyEvent.set()
			return


		if self.action == 2 and not self.finished:

			# After the initial population has been created, i launch the search process
			self.locker.acquire()
			if self.immigrants != []:
				#print(self.threadId,'FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK')
				for chromosome in self.immigrants:
					self.replace(chromosome)
				self.listFitnessData = []
				self.chromosomes.sort()
				self.getFitnessData()
			self.immigrants = []
			self.locker.release()
			#print("ok")
			self.prevChromosomes = copy.deepcopy(self.chromosomes)
			self.prevListFitnessData = copy.deepcopy(self.listFitnessData)

			self.chromosomes = []
			self.listFitnessData = []

			#print (self.name, " ", "Prev Population : ", self.prevChromosomes, " + ", self.prevListFitnessData, )
			#print (" ")

			self.slaveThreadsManager.crossoverPop()

			#print (self.name, " ", "Population : ", self.chromosomes, " + ", self.listFitnessData)
			#print (" ")

			if self.popLackingDiversity:

				#print("LACKING DIVERSITY - ", self.name)
				chromosome = copy.deepcopy(self.chromosomes[0])
			
				# i store this local optima in the genetic algorithm's memory to remind me that it's already been visited before

				chromosome.advmutate()
				
				if chromosome == self.chromosomes[0]:

					print (self.name, " ", "Solution : ", chromosome)
					self.result = copy.deepcopy(chromosome)
					self.finished = True

				else:

					#print("Initial1 -----------------", chromosome)
					#print("Initial2 -----------------", self.chromosomes)
					self.chromosomes = copy.deepcopy(self.initialChromosomes)
					self.listFitnessData = copy.deepcopy(self.initialChromData)
					self.replace(chromosome)

					#self.chromosomes[0] = copy.deepcopy(chromosome)
					#print (self.name, " ", self.chromosomes)

					self.listFitnessData = []
					self.getFitnessData()
					self.sendMigrants()
					#self.finished = True

					#self.chromosomes = copy.deepcopy(self.prevChromosomes)

			if self.readyFlag != 0:
				#print(self.readyFlag.isSet(), self.readyFlagId)
				self.readyFlag.wait()

			self.NbGenerations += 1

			self.readyFlag = 0
			self.readyEvent.set()
			#print("Set : ", self.threadId, self.readyEvent.isSet())

			return


	def initSearch(self, queue):
		
		#print("Queue : ", queue)
		queueSize = len(queue)
		indice = randint(0, queueSize - 1)
		currentNode = copy.deepcopy(queue[indice])
		del queue[indice]

		while True:

			if currentNode.isLeaf():
				#print("Yes : ", currentNode)
				if currentNode.isGood():
					c = Chromosome()
					c.init1(list(currentNode.solution), currentNode.fitnessValue)
					#c.advmutate()

					self.locker.acquire()
					#print(self.population.chromosomes)
					if len(self.chromosomes) >= ClspThread.NbMaxPopulation:
						self.locker.release()
						break
					if c not in self.chromosomes:
						self.chromosomes.append(copy.deepcopy(c))
					self.locker.release()

				#print("inter : ", self.queue)
				
			else:

				#print ("current Node : ", currentNode)
				l = currentNode.getChildren()
				#print("Children : ", l)
				#print(" ")
				
				#queueSize1 = len(queue)
				queue += l
				#print("indice : ", currentNode)
				#print("queue : ", queue)

			queueSize = len(queue)
			if queueSize == 0:
				#if self.population.listFitnessData == []:
				#	self.population.getFitnessData()
				break
			
			#queue.sort()
			#queue = list(reversed(queue))

			currentNode = copy.copy(queue[queueSize-1])
			del queue[queueSize-1]

		#print (self.name, " ", "Initial Population : ", self.population)

	def sendMigrants(self):
		
		if self.chromosomes != []:

			chromosomes = []
			i = 0
			while i < ClspThread.NumberOfMigrants:
				chromosomes.append(copy.deepcopy(self.chromosomes[i]))
				i += 1

			for thread in ClspThread.listMainThreads:
				if thread.getName() != self.name:
					thread.receiveMigrants(chromosomes)

			#print("Migrants : ", chromosomes)

	def receiveMigrants(self, chromosomes):
		self.locker.acquire()
		self.immigrants += copy.deepcopy(chromosomes)
		self.locker.release()


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

		if chromosome not in self.chromosomes:

			self.chromosomes.insert(0,copy.deepcopy(chromosome))

			# After inserting a new good chromosome into the population, i remove a bad one
			del self.chromosomes[len(self.chromosomes)-1]

	def getPopImproved(self):

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

				value += ClspThread.FITNESS_PADDING
				self.listFitnessData.append(value)
				sumAllFitnessValues += value

				i += 1
			
			#print(" Fitness Data 1 : ", self.listFitnessData)

			if tmpSumFitness == 0:
				self.popLackingDiversity = True
			
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
		if (randint(0,100) < (ClspThread.crossOverRate*100)):

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
		while j < len(self.prevListFitnessData):
			if (randValue1 >= lbound and randValue1 <= self.prevListFitnessData[j]):
				chromosome1 = self.prevChromosomes[j]
			if (randValue2 >= lbound and randValue2 <= self.prevListFitnessData[j]):
				chromosome2 = self.prevChromosomes[j]
			lbound = self.prevListFitnessData[j]
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

		while True:
			
			self.locker.acquire()

			if len(self.chromosomes) >= len(self.prevChromosomes):
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

		limit = ClspThread.NbMaxPopulation

		if self.prevChromosomes != []:
			limit = len(self.prevChromosomes)
		
		if popSize >= limit:
			self.chromosomes.sort()
			self.getFitnessData()
			self.locker.release()
			return 

		
		if self.prevChromosomes != []:
			chromosome.mutate()
		else:
			if chromosome in self.chromosomes:
				self.locker.release()
				return

		self.chromosomes.append(copy.deepcopy(chromosome))

		#print("Yes ", population.chromosomes)
		# Free lock to release next thread
		self.locker.release()