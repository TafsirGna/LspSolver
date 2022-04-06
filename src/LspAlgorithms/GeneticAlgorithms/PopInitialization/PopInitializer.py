#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading

from numpy import math
from LspAlgorithms.GeneticAlgorithms.PopInitialization.NodeGenerator import NodeGenerator
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
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
        self.population = Population()
        self._lock = threading.Lock()
        self.nodeGenerators = []

    def process(self, inputDataInstance):
        """
        """

        self.inputDataInstance = inputDataInstance

        children = self.rootNode().children()
        step = math.ceil(float(len(children)) / float(ParameterData.instance.nReplicaThreads))


        nodeGenQueues = [children[i:i+step] for i in range(0, len(children), step)]

        for i in range(ParameterData.instance.nReplicaThreads):
            nodeGenerator = NodeGenerator(nodeGenQueues[i])
            thread_T = Thread(target=self.search, args=(nodeGenerator,))
            self.nodeGenerators.append(nodeGenerator)
            thread_T.start()
            thread_T.join()
            self.threads.append(thread_T)

        print(self.population.chromosomes)
        return self.population

    def rootNode(self):
        """
        """

        return SearchNode.root(self.inputDataInstance)

    def search(self, nodeGenerator):
        """
        """

        for node in nodeGenerator.generate(): 
            result = None
            with self._lock:
                result = self.population.add(node.chromosome)
            if result is None:
                break  