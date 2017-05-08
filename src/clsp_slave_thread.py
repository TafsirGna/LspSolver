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
			self.listSlaveThreads.append(slaveThread)
			(self.listSlaveThreads[i]).start()

			i += 1

		for thread in self.listSlaveThreads:
			thread.join()

		self.nextSlaveThread = self.listSlaveThreads[0] # variable that holds a reference to the next thread to which the received solution will be affected


	def compute(self, population, popLocker, solution):

		#print("Solution found : ", solution)

		param = [population, popLocker, solution]

		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)
		self.nextSlaveThread.queueLocker.release()
		self.nextSlaveThread.run()

		# then i compute the next thread which the next solution will be sent to
		minQueueSize = pow(10,6)
		for slaveThread in self.listSlaveThreads:
			slaveThread.queueLocker.acquire()
			queueSize = len(slaveThread.queue) 
			if queueSize < minQueueSize:
				self.nextSlaveThread = slaveThread
				minQueueSize = queueSize
			slaveThread.queueLocker.release()


	def performCrossOver(self, prevPopData, nextPopulation, popLocker, randValue1, randValue2):
		
		previousPopulation = Population()
		previousPopulation.chromosomes = prevPopData[0]
		previousPopulation.listFitnessData = prevPopData[1]

		param = [previousPopulation, nextPopulation, popLocker, randValue1, randValue2]

		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)
		self.nextSlaveThread.queueLocker.release()
		self.nextSlaveThread.run()

		# then i compute the next thread which the next solution will be sent to
		minQueueSize = pow(10,6)
		for slaveThread in self.listSlaveThreads:
			slaveThread.queueLocker.acquire()
			queueSize = len(slaveThread.queue) 
			if queueSize < minQueueSize:
				self.nextSlaveThread = slaveThread
				minQueueSize = queueSize
			slaveThread.queueLocker.release()


class SlaveThread(Thread):

	def __init__(self):

		Thread.__init__(self)
		self.queue = []
		self.queueLocker = threading.Lock()

	def run(self):
		
		param = []
		self.queueLocker.acquire()
		if len(self.queue) > 0:
			param = self.queue[0]
			del self.queue[0]
		self.queueLocker.release()

		while param != []:

			if len(param) == 3:

				c = Chromosome(param[2])
				#c.getFeasible()
				#c.advmutate()

				self.insert(c, param[0], param[1])

			elif len(param) == 5:

				self.applyCrossOver(param[0], param[1], param[2], param[3], param[4])

			param = []
			self.queueLocker.acquire()
			if len(self.queue) > 0:
				param = self.queue[0]
				del self.queue[0]
			self.queueLocker.release()
				
		
	#--------------------
	# function : mate
	# Class : SlaveThread
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

		#print("applyCrossOver 1 : ", randValue1, randValue2, len(previousPopulation.chromosomes), " Statistics : ", len(previousPopulation.listFitnessData))
		#print("applyCrossOver 2 : ", randValue1, randValue2, previousPopulation.chromosomes, " Statistics : ", previousPopulation.listFitnessData)

		j = 0
		lbound = 0
		while j < len(previousPopulation.listFitnessData):
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
		
		self.insert(chromosome3, nextPopulation, popLocker, previousPopulation)
		self.insert(chromosome4, nextPopulation, popLocker, previousPopulation)

		#print ("pop : ", nextPopulation.chromosomes)

	def insert(self, chromosome, population, popLocker, previousPopulation = 0):

		# Get lock to synchronize threads
		popLocker.acquire()
		popSize = len(population.chromosomes)

		limit = Population.NbMaxPopulation

		if previousPopulation != 0:
			limit = len(previousPopulation.chromosomes)
		
		if popSize >= limit:
			population.getFitnessData()
			popLocker.release()
			return 

		
		if previousPopulation != 0:
			chromosome.mutate()
		else:
			if chromosome in population.chromosomes:
				#chromosome.advmutate()
				popLocker.release()
				return

		#print("Insertion : ", chromosome)
		if (population.chromosomes == []):

			population.chromosomes.append(copy.deepcopy(chromosome))
	
		elif popSize == 1 and (population.chromosomes[0]).fitnessValue == 0:

			population.chromosomes.append(copy.deepcopy(chromosome))

		else:

			# i sort the list of zeroperiods from the most convenient place to the least convenient one
			prevValue = 0
			j = 0
			found = False
			while j < popSize:

				if chromosome.fitnessValue >= prevValue and chromosome.fitnessValue <= (population.chromosomes[j]).fitnessValue:
					found = True

					Population.gaMemoryLocker.acquire()
					isElement = chromosome in Population.ga_memory
					Population.gaMemoryLocker.release()

					#print("in ga_memory : ", chromosome, " and ", Population.ga_memory, " and ", isElement)

					if isElement is False:
						population.chromosomes = population.chromosomes[:j] + [copy.deepcopy(chromosome)] + population.chromosomes[j:]
					
					break

				prevValue = (population.chromosomes[j]).fitnessValue

				j += 1

			if found is False:

				
				Population.gaMemoryLocker.acquire()
				isElement = chromosome in Population.ga_memory
				Population.gaMemoryLocker.release()

				#print("in ga_memory : ", chromosome, " and ", Population.ga_memory, " and ", isElement)

				if isElement is False:
					population.chromosomes.append(copy.deepcopy(chromosome))

		#print("Yes ", population.chromosomes)
		# Free lock to release next thread
		popLocker.release()
			
			