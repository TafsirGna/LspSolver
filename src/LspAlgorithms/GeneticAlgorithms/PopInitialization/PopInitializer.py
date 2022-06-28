#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGenerator import InitNodeGenerator
from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGeneratorManager import InitNodeGeneratorManager
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from queue import Queue
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import numpy as np
import concurrent.futures

class PopInitializer:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.populations = [Population() for _ in range(ParameterData.instance.nPrimaryThreads)]
        
        # NodeGeneratorManager
        # self.nodeGeneratorManager = self.createNodeGeneratorManager()

        self.initPool = set()
        self.initPoolExpectedSize = ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads

        self.searchInitPop()


    def process(self):
        """
        """

        chromosomes = list(self.initPool)
        chromosomes = np.array_split(chromosomes, ParameterData.instance.nPrimaryThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.threadTask, list(range(ParameterData.instance.nPrimaryThreads)), chromosomes)

        LspRuntimeMonitor.output(str(self.populations))
        return self.populations


    def threadTask(self, popIndex, chromosomes):
        """
        """
        
        for chromosome in chromosomes:
            self.populations[popIndex].add(chromosome)

        Population.popSizes[self.populations[popIndex].lineageIdentifier] = self.populations[popIndex].popLength


    def searchInitPop(self):
        """
        """

        queue = SearchNode.root().children()

        while len(queue) > 0:
            # print("len : ", queue)
            node = queue[0]
            # print("nooode : ", node)
            queue = queue[1:]

            if node.period == -1: # No children
                node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
                self.initPool.add(node.chromosome)

            tmpLen = len(queue)
            for child in node.generateChild():
                if child is not None:
                    queue.append(child)
                    if len(queue) >= self.initPoolExpectedSize:
                        break


        # print(self.initPool, len(self.initPool))





    



