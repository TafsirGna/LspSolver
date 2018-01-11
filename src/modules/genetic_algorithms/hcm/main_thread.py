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
	nbTrials = 0
	crossOverRate = 0
	MigrationRate = 0
	NbMaxPopulation = 0
	FITNESS_PADDING = 0
	pickeRandChromGens = 0

	def __init__(self, threadId):

		Thread.__init__(self)
		self.threadId = threadId
		self.name = "Thread - " + str(threadId)
		self.locker = threading.Lock()
		self.NbGenerations = 0
		self.readyFlag = 0
		self.readyFlagId = 0
		self.queue = []
		self.readyEvent = Event()
		self.action = 1
		self.finished = False
		self.result = 0
		self.memory = []
		self.popLackingDiversity = False
		self.nbIdleGens = 0

		self.chromosomes = []
		self.initialChromosomes = []
		self.listFitnessData = []
		self.initialChromData = []
		self.prevChromosomes = []
		self.prevListFitnessData = []
		self.popSize = 0

		self.immigrants = []
		self.slaveThreadsManager = SlaveThreadsManager(self) # i initialize a list that's intended to contain all the population's initialization threads 

	def run(self):
		
		if self.action == 1:

			self.initSearch(self.queue)

			for i in range(1, self.popSize):
				#if not (self.chromosomes[i]).isFeasible():
				#	print("in init 1 : ", (self.chromosomes[i]))
				(self.chromosomes[i]).mutate2()
				#if not (self.chromosomes[i]).isFeasible():
				#	print("in init 2 : ", (self.chromosomes[i]))

			(self.chromosomes[randint(1, self.popSize-1)]).advmutate()
			
			self.chromosomes.sort()
			self.listFitnessData = []
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
			#print ('------------------------- : ', self.chromosomes, " / ", self.listFitnessData)
			self.locker.acquire()
			if self.immigrants != []:

				for chromosome in self.immigrants:
					self.replace(chromosome)
				self.listFitnessData = []

				#(self.chromosomes[randint(0, self.popSize - 1)]).advmutate()

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
			#print("WOOOOOO 1 ")
			self.slaveThreadsManager.crossoverPop()
			#print("WOOOOOO 2 ")

			#print (self.name, " ", self.NbGenerations,  " ", "Population : ", self.chromosomes, " + ", self.listFitnessData)
			#print (" ")

			if self.popLackingDiversity:

				print("LACKING DIVERSITY - ", self.name)
				chromosome = copy.deepcopy(self.chromosomes[0])

				chromosome.advmutate()

				self.chromosomes = copy.deepcopy(self.initialChromosomes)
				self.replace(chromosome)

				for i in range(1, self.popSize):
					(self.chromosomes[i]).mutate2()

				(self.chromosomes[randint(1, self.popSize-1)]).advmutate()
				self.chromosomes.sort()

				self.listFitnessData = []
				self.getFitnessData()
				self.sendMigrants()

				self.initialChromosomes = copy.deepcopy(self.chromosomes)
				self.initialChromData = copy.deepcopy(self.listFitnessData)	
				self.nbIdleGens += 1	

				#if self.NbGenerations % ClspThread.pickeRandChromGens == 0:
				#	(self.chromosomes[randint(0,len(self.chromosomes)-1)]).advmutate()	

				# for the first solution found
				if isinstance(self.result, int):
					self.result = copy.deepcopy(chromosome)
				else:
					if chromosome.fitnessValue < self.result.fitnessValue:
						self.result = copy.deepcopy(chromosome)
						self.nbIdleGens = 0
					if self.nbIdleGens == ClspThread.nbTrials:
						print (self.name, " ", "Solution : ", chromosome)
						self.finished = True		

			if self.readyFlag != 0:
				#print(self.readyFlag.isSet(), self.readyFlagId)
				self.readyFlag.wait()

			self.NbGenerations += 1

			self.readyFlag = 0
			self.readyEvent.set()
			#print("Set : ", self.threadId, self.readyEvent.isSet())

			return

	def exploit(self, chromosome):

		nbResults = 1
		queue = []
		currentNode = AdvMutateNode(chromosome)
		successors = []

		#print ("in exploit : ",chromosome)
		
		while True:

			#print("Current node : ", currentNode)
			child = currentNode.getChild()
			#print("Child : ", child)

			if child != []:
				successors.append(child)
				queue.append(child)

			if queue == []:
				#print ("in exploit : ",currentNode.chromosome)
				break

			currentNode = queue[len(queue)-1]
			del queue[len(queue)-1]

		i = len(successors)-1
		#print("End exploit 1-----------------------", i)
		while i >= 0:
			if (successors[i]).chromosome not in self.chromosomes and self.popSize < ClspThread.NbMaxPopulation:

				self.chromosomes.append((successors[i]).chromosome)
				if (successors[i]).chromosome.fitnessValue != Node.evaluate((successors[i]).chromosome.solution):
					print("COOOOOOOOOOOOOOOOOOOOL")
				self.popSize += 1
			i -= 1

		#print("End exploit-----------------------")

	def initSearch(self, queue):

		#print("ok")
		currentNode = copy.deepcopy(queue[len(queue)-1])
		del queue[len(queue)-1]

		i = 0
		while True:

			if currentNode.isLeaf():

				self.locker.acquire()
				

				if self.popSize >= ClspThread.NbMaxPopulation:
					self.locker.release()
					break

				if currentNode.chromosome not in self.chromosomes:
					#currentNode.chromosome.checkItemRank()

					if currentNode.chromosome.fitnessValue != Node.evaluate(currentNode.chromosome.solution):
						print("COOOOOOOOOOOOOOOOOOOOL")

					self.chromosomes.append(copy.deepcopy(currentNode.chromosome))
					self.popSize += 1
					#self.exploit(currentNode.chromosome)
				self.locker.release()

			#else:
			#print ("current Node : ", currentNode)
			child = currentNode.getChild()
			#print("Child : ", child)
			if child != []:
				queue.append(child)
			#print("Queue : ", queue)
		
			if queue == []:
				#self.chromosomes.sort()
				#print("yes2")
				break

			currentNode = copy.deepcopy(queue[len(queue)-1])
			del queue[len(queue)-1]


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
		while i < self.popSize:

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

	def replace(self, chromosome):

		if chromosome not in self.chromosomes:

			self.chromosomes.insert(0,copy.deepcopy(chromosome))

			# After inserting a new good chromosome into the population, i remove a bad one
			del self.chromosomes[self.popSize-1]

	def getFitnessData(self):

		if self.popSize > 0 and self.listFitnessData == []:

			sumAllFitnessValues = 0
			tmpSumFitness = 0 #variable used to quantify the lack of diversity in the population
			max_fitness = (self.chromosomes[self.popSize-1]).fitnessValue
			
			i = 0
			while i < self.popSize:
				
				chromosome = self.chromosomes[i]
				temp = chromosome.fitnessValue

				value = (max_fitness-temp)
				tmpSumFitness += value

				value += ClspThread.FITNESS_PADDING
				self.listFitnessData.append(value)
				sumAllFitnessValues += value
				#print(" value : ", value, tmpSumFitness)

				i += 1
			
			#print(" Fitness Data 1 : ", self.listFitnessData)
			#print(max_fitness, tmpSumFitness)
			if tmpSumFitness == 0:
				self.popLackingDiversity = True
			
			self.fitnessMean = math.floor(sumAllFitnessValues / self.popSize)

			i = 0
			percentage = 0
			while i < self.popSize:
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
			#print("log getfitnessData: ", self.threadId ," / " , self.chromosomes, " / ",self.listFitnessData , " / ", max_fitness)

	#--------------------
	# function : mate
	# Class : SlaveThread
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------

	def mate(self, chromosome1, chromosome2):

		#chromosome1.checkItemRank()
		#chromosome2.checkItemRank()

		#print("mate 1 : ", chromosome1, chromosome2)
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
			chromosome3.solution = solution3
			chromosome3.itemsRank = ranks3
			#print("chromosome3 1 : ", chromosome3, ranks3)
			#co = copy.deepcopy(chromosome3)
			chromosome3.getFeasible()
			#if not chromosome3.isFeasible():
			#	print("not feasible : ", co, chromosome3)
			#print("chromosome3 2 : ", chromosome3)

			chromosome4 = Chromosome()
			chromosome4.solution = solution4
			chromosome4.itemsRank = ranks4
			#print("chromosome4 1 : ", chromosome4, ranks4)
			#co = copy.deepcopy(chromosome4)
			chromosome4.getFeasible()
			#if not chromosome3.isFeasible():
			#	print("not feasible : ", co, chromosome4)
			#print("chromosome4 2 : ", chromosome4)

			#print(" 2 - solution3 : ", chromosome3.solution, " ranks3 : ", ranks3, " solution4 : ", chromosome4.solution, " ranks4 : ", ranks4)
			

		else:
			chromosome3 = copy.deepcopy(chromosome1)
			chromosome4 = copy.deepcopy(chromosome2)

		#print("mate 2 : ", chromosome1, chromosome2)
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

		#print("chromosomes : ", self.chromosomes)
		#print ("pop : ", nextPopulation.chromosomes)

	def crossPopulation(self):

		while True:
			
			self.locker.acquire()

			if len(self.chromosomes) >= len(self.prevChromosomes):
				#(self.chromosomes[randint(0,len(self.chromosomes)-1)]).advmutate()
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
		
		if popSize >= limit:
			#(self.chromosomes[randint(0,len(self.chromosomes)-1)]).advmutate()
			self.chromosomes.sort()
			self.getFitnessData()
			self.locker.release()
			return 

		#chromosome.checkItemRank()
		self.chromosomes.append(copy.deepcopy(chromosome))

		#print("Yes ", population.chromosomes)
		# Free lock to release next thread
		self.locker.release()