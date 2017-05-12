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
	def __init__(self, nbSlaveThreads):

		super(SlaveThreadsManager, self).__init__()
		self.listSlaveThreads = []
		self.locker = threading.Lock()

		i = 0
		while i < nbSlaveThreads:
			
			slaveThread = SlaveThread()
			self.listSlaveThreads.append(slaveThread)
			(self.listSlaveThreads[i]).start()

			i += 1

		for thread in self.listSlaveThreads:
			thread.join()

		self.nextSlaveThread = self.listSlaveThreads[0] # variable that holds a reference to the next thread to which the received solution will be affected


	def handle(self, population, solution):

		param = [population, solution]
		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)

		# weirdly, i have to check if the locker is locked before releasing it
		#if self.nextSlaveThread.queueLocker.locked():
		#	try:
		self.nextSlaveThread.queueLocker.release()
		#	except:
		#		print("DeadLock error : An unlocked thread can't be released")

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


	def crossover(self, population, randValue1, randValue2):
		'''
		previousPopulation = Population()
		previousPopulation.chromosomes = prevPopData[0]
		previousPopulation.listFitnessData = prevPopData[1]
		'''

		param = [population, randValue1, randValue2]

		self.nextSlaveThread.queueLocker.acquire()
		self.nextSlaveThread.queue.append(param)

		# weirdly, i have to check if the locker is locked before releasing it
		#if self.nextSlaveThread.queueLocker.locked():
		#	try:
		self.nextSlaveThread.queueLocker.release()
		#	except:
		#		print("DeadLock error : An unlocked thread can't be released")
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
			param = list(self.queue[0])
			del self.queue[0]
		self.queueLocker.release()

		while param != []:

			if len(param) == 2:

				population = param[0]
				solution = param[1]

				if isinstance(solution, list):
					chromosome = Chromosome(param[1])
					population.insert(chromosome)

				elif isinstance(solution, Chromosome):
					chromosome = copy.deepcopy(param[1])
					chromosome.advmutate()
					population.replace(chromosome)

			elif len(param) == 3:
				population = param[0]
				randValue1 = param[1]
				randValue2 = param[2]

				population.crossover(randValue1, randValue2)

			param = []
			self.queueLocker.acquire()
			if len(self.queue) > 0:
				param = list(self.queue[0])
				del self.queue[0]
			self.queueLocker.release()			