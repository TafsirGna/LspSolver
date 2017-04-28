 #!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from chromosome import *

#--------------------
# Class : SlaveThreadsManager
# author : Tafsir GNA
# purpose : Describing a the structure of a manager of slave threads that compute chromosomes for main threads and return the results
#--------------------

class SlaveThreadsManager:

	"""docstring for SlaveThreadsManager"""
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

			threadPopulation = param[0]
			popLocker = param[1]
			solution = param[2]	

			c = Chromosome(copy.copy(solution))
			#c.getFeasible()
			c.advmutate()
			#print("Solution found : ", solution, c.solution)	

			#print("Leaf : ", c)

			# Get lock to synchronize threads
			popLocker.acquire()

			if c not in threadPopulation.chromosomes:
				threadPopulation.chromosomes.append(c)
				threadPopulation.NbPopulation += 1

			# i store the value of the highest value of the objective function
			value = c.fitnessValue
			if value > threadPopulation.max_fitness:
				threadPopulation.max_fitness = value

			# i want to store the best chromosome of the population
			if value < threadPopulation.min_fitness:
				threadPopulation.min_fitness = value
				threadPopulation.elite = copy.copy(c)

			# Free lock to release next thread
			popLocker.release()
		
