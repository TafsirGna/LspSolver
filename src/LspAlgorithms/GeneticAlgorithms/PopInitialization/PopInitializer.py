#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading

from numpy import math
from LspAlgorithms.GeneticAlgorithms.PopInitialization.NodeGenerator import NodeGenerator
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.PopInitThread import PopInitThread
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from threading import Thread

class PopInitializer:
    """
    """

    def __init__(self, inputDataInstance, strategy = "DFS", criteria = None) -> None:
        """
        """
        self.inputDataInstance = inputDataInstance
        self.strategy = strategy
        self.threads = []
        self.populations = []

    def process(self):
        """
        """

        nodeGenerators = self.initNodeGenerators()

        for i in range(ParameterData.instance.nPrimaryThreads):
            # thread_T = PopInitThread(i, nodeGenerators[i])
            thread_T = Thread(target=self.searchChromosomes, args=(i, nodeGenerators[i]))
            thread_T.start()
            self.threads.append(thread_T)

        [thread_T.join() for thread_T in self.threads]
        # populations = [popInitThread.population for popInitThread in self.threads]

        print(self.populations)
        return self.populations

    def rootNode(self):
        """
        """
        return SearchNode.root(self.inputDataInstance)


    def initQueue(self):
        """
        """
        queue = self.rootNode().children()
        while len(queue) < ParameterData.instance.nPrimaryThreads:
            node = queue[-1]
            queue = queue[:-1]
            queue += node.children()

        return queue

    def initNodeGenerators(self):
        """
        """

        initQueue = self.initQueue()

        step = math.ceil(float(len(initQueue)) / float(ParameterData.instance.nPrimaryThreads))

        nodeGeneratorQueues = [initQueue[i:i+step] for i in range(0, len(initQueue), step)]
        nodeGenerators = [NodeGenerator(queue) for queue in nodeGeneratorQueues]
        return nodeGenerators



    def searchChromosomes(self, threadIndex, nodeGenerator):
        """
        """

        population = Population([])

        for node in nodeGenerator.generate(): 
            result = None
            # with self._lock:
            result = population.add(node.chromosome)
            if result is None:
                break  

        population.setElites()
        self.populations.append(population)