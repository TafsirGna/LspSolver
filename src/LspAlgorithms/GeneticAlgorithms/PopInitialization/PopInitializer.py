#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading

from numpy import math
from LspAlgorithms.GeneticAlgorithms.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGenerator import InitNodeGenerator
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGeneratorManager import InitNodeGeneratorManager
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from threading import Thread

class PopInitializer:
    """
    """

    def __init__(self, strategy = "DFS", criteria = None) -> None:
        """
        """
        self.strategy = strategy
        self.threads = []
        self.populations = []
        self.lock = threading.Lock()
        self.popsLock = [threading.Lock() for _ in range(ParameterData.instance.nPrimaryThreads)]


    def process(self):
        """
        """

        nodeGeneratorManager = self.createNodeGeneratorManager()

        for i in range(ParameterData.instance.nPrimaryThreads):
            thread_T = Thread(target=self.mainThreadTask, args=(i, nodeGeneratorManager))
            thread_T.start()
            self.threads.append(thread_T)

        [thread_T.join() for thread_T in self.threads]

        LspRuntimeMonitor.output(str(self.populations))
        return self.populations


    def createNodeGeneratorManager(self):
        """ Create a node generator manager
        """

        nodeGenerators = self.initNodeGenerators()
        return InitNodeGeneratorManager(nodeGenerators)


    def rootNode(self):
        """
        """
        return SearchNode.root()


    def initNodeGenerators(self):
        """
        """

        queue = self.rootNode().children()
        nodeGenerators = [InitNodeGenerator([node]) for node in queue]
        return nodeGenerators



    def mainThreadTask(self, threadId, nodeGeneratorManager):
        """Search chromosomes
        """

        population = Population([])
        # population.uniques = []

        replicas = []
        for _ in range(ParameterData.instance.nReplicaThreads):
            replica = Thread(target=self.replicaThreadTask, args=(threadId, population, nodeGeneratorManager))
            replica.start()
            replicas.append(replica)
            
        for replica in replicas:
            replica.join()


        population.popSize = len(population.chromosomes)
        self.populations.append(population)


    def replicaThreadTask(self, mainThreadId, population, nodeGeneratorManager):
        """
        """

        with self.lock:
            node = nodeGeneratorManager.newInstance(mainThreadId)

        while node is not None: 

            result = None
            with self.popsLock[mainThreadId]:
                result = population.add(node.chromosome)
                # (LocalSearchEngine()).process(node.chromosome, "population", [self.popsLock[mainThreadId], population])
            if result is None:
                break  

            with self.lock:
                node = nodeGeneratorManager.newInstance(mainThreadId)
