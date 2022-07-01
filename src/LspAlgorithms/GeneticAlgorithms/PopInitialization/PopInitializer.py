#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import threading
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGenerator import InitNodeGenerator
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.InitNodeGeneratorManager import InitNodeGeneratorManager
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from queue import Queue
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import numpy as np
import concurrent.futures
import uuid
from collections import defaultdict

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
        self.initPoolSizeData = {"lock": threading.Lock(), "sizes": defaultdict(lambda: 0)}

        self.searchInitPop()


    def process(self):
        """
        """

        chromosomes = list(self.initPool)
        chromosomes = np.array_split(chromosomes, ParameterData.instance.nPrimaryThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.stuffPopThreadTask, list(range(ParameterData.instance.nPrimaryThreads)), chromosomes)

        LspRuntimeMonitor.output(str(self.populations))
        return self.populations


    def stuffPopThreadTask(self, popIndex, chromosomes):
        """
        """
        
        for chromosome in chromosomes:
            self.populations[popIndex].add(chromosome)

        Population.popSizes[self.populations[popIndex].lineageIdentifier] = self.populations[popIndex].popLength


    def searchInitPop(self):
        """
        """

        queue = SearchNode.root().children()
        queues = np.array_split(queue, ParameterData.instance.nReplicaThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # executor.map(self.searchPopThreadTask, [queue])
            print(list(executor.map(self.searchPopThreadTask, queues)))

        # print("self.initPool", len(self.initPool))


    def searchPopThreadTask(self, queue):
        """
        """

        threadID = uuid.uuid4()

        queue = list(queue)

        while len(queue) > 0:
            # print("len : ", queue)
            node = queue[0]
            # print("nooode : ", node)
            queue = queue[1:]

            if node.period == -1: # No children
                node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
                self.initPool.add(node.chromosome)

            # print("coco : ", node)
            children = node.children()

            with self.initPoolSizeData["lock"]:

                self.initPoolSizeData["sizes"][threadID] = len(queue)
                size = 0
                for threadId in self.initPoolSizeData["sizes"]:
                    size += self.initPoolSizeData["sizes"][threadId]

                for child in children:
                    if child is not None:
                        queue.append(child)
                        self.initPoolSizeData["sizes"][threadID] += 1
                        size += 1

                        if size  >= self.initPoolExpectedSize:
                            break




    



