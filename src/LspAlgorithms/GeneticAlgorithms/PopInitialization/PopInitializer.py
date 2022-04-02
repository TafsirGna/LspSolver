#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspStatistics.LspRuntimeStatisticsMonitor import LspRuntimeStatisticsMonitor
import time
import random

from ParameterSearch.ParameterData import ParameterData

from .InitSearchNode import SearchNode

class PopInitializer:
    """
    """

    def __init__(self, strategy = "DFS", criteria = None) -> None:
        """
        """

        self.strategy = strategy

    def process(self, inputDataInstance):
        """
        """

        self.inputDataInstance = inputDataInstance
        self.queue = []

        ###
        if LspRuntimeStatisticsMonitor.instance:
            LspRuntimeStatisticsMonitor.instance.popInitClockStart = time.clock()
        ###

        rootNode = self.rootNode()

        population = self.search(rootNode)

        ###
        if LspRuntimeStatisticsMonitor.instance:
            LspRuntimeStatisticsMonitor.instance.popInitClockEnd = time.clock()
        ###

        return population

    def rootNode(self):
        """
        """

        return SearchNode.root(self.inputDataInstance)

    def search(self, node):
        """
        """
        
        chromosomes = []

        children = node.children()

        self.queue += children

        while len(self.queue) > 0:

            node = self.queue[-1]
            self.queue = self.queue[0:len(self.queue) - 1]

            children = node.children()

            if len(children) == 0: # leaf node
                # node.chromosome.cost = Chromosome.calculateCost(node.chromosome.dnaArray, InputDataInstance.instance)
                chromosomes.append(node.chromosome)

                ###
                if ParameterData.instance:
                    if len(chromosomes) >= ParameterData.instance.popSize:
                        print(chromosomes)
                        return Population(chromosomes)
                ###

            random.shuffle(children)
            self.queue += children

        print(chromosomes)

        return Population(chromosomes)

		
		# # i make up the queue of each main thread
		# nbChildren = len(children)
		# for i in range(0, nbChildren):
		# 	(self.listMainThreads[i%GeneticAlgorithm.nbMainThreads]).queue.append(copy.deepcopy(children[i]))

		
		# # i set the flags
		# prevThread = self.listMainThreads[0]
		# if GeneticAlgorithm.nbMainThreads > 1:
		# 	for i in range(1, GeneticAlgorithm.nbMainThreads):
		# 		(self.listMainThreads[i]).readyFlag = prevThread.readyEvent
		# 		prevThread = self.listMainThreads[i]

		# # first, i initialize the population upon which the search will be applied
		# for thread in self.listMainThreads:
		# 	thread.start()
		# 	thread.join()

		# (self.listMainThreads[len(self.listMainThreads)-1]).readyEvent.wait()

		# print("Initialized!!!")

        pass