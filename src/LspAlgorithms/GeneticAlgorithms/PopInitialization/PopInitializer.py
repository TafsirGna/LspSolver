#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import copy

from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputData.LspInputDataInstance import InputDataInstance

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

        rootNode = self.rootNode()

        return self.search(rootNode)

    def rootNode(self):
        """
        """

        return SearchNode.root(self.inputDataInstance)

    def search(self, node):
        """
        """
        
        population = []

        children = node.children()

        self.queue += children

        while len(self.queue) > 0:

            node = self.queue[-1]
            self.queue = self.queue[0:len(self.queue) - 1]

            children = node.children()

            if len(children) == 0: # leaf node
                node.chromosome.cost = Chromosome.calculateCost(node.chromosome.dnaArray, InputDataInstance.instance)
                population.append(node.chromosome)

            self.queue += children

        print(population)

        return population

		
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