 #!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from population import *

#--------------------
# Class : SlaveThreadsManager
# author : Tafsir GNA
# purpose : Describing a the structure of a manager of slave threads that compute chromosomes for main threads and return the results
#--------------------

class SlaveThreadsManager:

	"""docstring for SlaveThreadsManager"""
	crossOverRate = 0

	def __init__(self, nbSlaveThreads):

		super(SlaveThreadsManager, self).__init__()
		self.listSlaveThreads = []

		i = 0
		while i < nbSlaveThreads:
			
			slaveThread = SlaveThread()
			self.listSlaveThreads.append(copy.copy(slaveThread))
			(self.listSlaveThreads[i]).start()
			(self.listSlaveThreads[i]).join()

			i += 1

		self.nextSlaveThread = self.listSlaveThreads[0] # variable that holds a reference to the next thread to which the received solution will be affected


	def compute(self, threadPopulation, popLocker, solution):

		#print("Solution found : ", solution)

		param = [threadPopulation, popLocker, solution]

		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)
		self.nextSlaveThread.queueSize += 1
		self.nextSlaveThread.queueLocker.release()
		self.nextSlaveThread.run()

		# then i compute the next thread which the next solution will be sent to
		queueSize = pow(10,6)
		for slaveThread in self.listSlaveThreads:
			slaveThread.queueLocker.acquire()
			if slaveThread.queueSize < queueSize:
				self.nextSlaveThread = slaveThread
				queueSize = self.nextSlaveThread.queueSize
			slaveThread.queueLocker.release()


	def performCrossOver(self, previousPopulation, nextPopulation, popLocker, randValue1, randValue2):
		
		param = [previousPopulation, nextPopulation, popLocker, randValue1, randValue2]

		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)
		self.nextSlaveThread.queueSize += 1
		self.nextSlaveThread.queueLocker.release()
		self.nextSlaveThread.run()

		# then i compute the next thread which the next solution will be sent to
		queueSize = pow(10,6)
		for slaveThread in self.listSlaveThreads:
			slaveThread.queueLocker.acquire()
			if slaveThread.queueSize < queueSize:
				self.nextSlaveThread = slaveThread
				queueSize = self.nextSlaveThread.queueSize
			slaveThread.queueLocker.release()


class SlaveThread(Thread):

	def __init__(self):

		Thread.__init__(self)
		self.queue = []
		self.queueSize = 0
		self.queueLocker = threading.Lock()

	def run(self):
		
		#print ("queue's size : ", self.queueSize)
		while self.queueSize > 0:

			self.queueLocker.acquire()
			param = self.queue[0]
			del self.queue[0]
			self.queueSize -= 1
			self.queueLocker.release()

			if len(param) == 3:

				c = Chromosome(copy.copy(param[2]))
				#c.getFeasible()
				c.advmutate()

				self.insert(c, param[0], param[1], 0)

			elif len(param) == 5:

				self.applyCrossOver(param[0], param[1], param[2], param[3], param[4])
				
		
	#--------------------
	# function : mate
	# Class : GeneticAlgorithm
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------

	def mate(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		#print(Population.crossOverRate)
		if (randint(0,100) < (SlaveThreadsManager.crossOverRate*100)):

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

		return chromosome3, chromosome4


	def applyCrossOver(self, previousPopulation, nextPopulation, popLocker, randValue1, randValue2):

		j = 0
		lbound = 0
		while j < previousPopulation.NbPopulation:
			if (randValue1 >= lbound and randValue1 <= previousPopulation.listFitnessData[j]):
				chromosome1 = previousPopulation.chromosomes[j]
			if (randValue2 >= lbound and randValue2 <= previousPopulation.listFitnessData[j]):
				chromosome2 = previousPopulation.chromosomes[j]
			lbound = previousPopulation.listFitnessData[j]
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

		#if self.isFeasible(chromosome3) is False or self.isFeasible(chromosome4) is False:
		#	print("c3 : ", c3, " c4 : ", c4)

		Population.gaMemoryLocker.acquire()
		isElement = chromosome3 not in Population.ga_memory
		Population.gaMemoryLocker.release()

		if isElement:
			self.insert(chromosome3, nextPopulation, popLocker, 1)
			#print( chromosome3, " pop State : ", nextPopulation.chromosomes)

		Population.gaMemoryLocker.acquire()
		isElement = chromosome4 not in Population.ga_memory
		Population.gaMemoryLocker.release()

		if isElement:
			self.insert(chromosome4, nextPopulation, popLocker, 1)
			#print( chromosome4, " pop State : ", nextPopulation.chromosomes)

		#print ("pop : ", nextPopulation.chromosomes)

	def insert(self, chromosome, population, popLocker, state):

		# Get lock to synchronize threads
		popLocker.acquire()

		if state == 0:

			if chromosome not in population.chromosomes:
				population.chromosomes.append(chromosome)
				population.NbPopulation += 1

		elif state == 1:
			
			population.chromosomes.append(chromosome)
			population.NbPopulation += 1

		# i store the value of the highest value of the objective function
		value = chromosome.fitnessValue
		if value > population.max_fitness:
			population.max_fitness = value

		# i want to store the best chromosome of the population
		if value < population.min_fitness:
			population.min_fitness = value
			population.elite = copy.copy(chromosome)

		# Free lock to release next thread
		popLocker.release()
