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
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine

class PopInitializer:
    """
    """

    SMALL_INSTANCE_CATEGORY = "small"
    BIG_INSTANCE_CATEGORY = "big"
    initPoolExpectedSize = None

    def __init__(self, instance_category = BIG_INSTANCE_CATEGORY) -> None:
        """
        """

        self.populations = [Population() for _ in range(ParameterData.instance.nPrimaryThreads)]

        if PopInitializer.initPoolExpectedSize is None:
            PopInitializer.initPoolExpectedSize = initPoolExpectedSize = ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads

        self.initPool = set()
        
        if instance_category == PopInitializer.SMALL_INSTANCE_CATEGORY:
            PopInitializerSmallInstanceApproach(self.initPool)   
        elif instance_category == PopInitializer.BIG_INSTANCE_CATEGORY:
            PopInitializerBigInstanceApproach(self.initPool)     


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




class PopInitializerSmallInstanceApproach:
    """
    """

    def __init__(self, initPool) -> None:
        """
        """

        self.initPool = initPool
        self.initPoolSizeData = {"lock": threading.Lock(), "sizes": defaultdict(lambda: 0)}
        self.process()


    def process(self):
        """
        """

        queue = SearchNode.root().children()
        queues = np.array_split(queue, ParameterData.instance.nReplicaThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # executor.map(self.searchPopThreadTask, [queue])
            print(list(executor.map(self.searchPopThreadTask, queues)))


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

                        if size  >= PopInitializer.initPoolExpectedSize:
                            break



class PopInitializerBigInstanceApproach:
    """
    """

    def __init__(self, initPool) -> None:
        """
        """

        self.initPool = initPool
        self.initPoolLock = threading.Lock()
        self.initPoolStopEvent = threading.Event()
        self.process()


    def process(self):
        """
        """

        queue = SearchNode.root().children()
        queues = np.array_split(queue, ParameterData.instance.nReplicaThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # executor.map(self.searchPopThreadTask, [queue])
            print(list(executor.map(self.searchPopThreadTask, queues)))


    def searchInitPopInstance(self, node):
        """
        """

        if node.period == -1:
            print("Hello : ", node.chromosome)
            node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
            with self.initPoolLock:
                self.initPool.add(node.chromosome)
                if len(self.initPool) >= PopInitializer.initPoolExpectedSize:
                    self.initPoolStopEvent.set()
            self.expandInitPopInstance([node.chromosome])
            return None

        for child in node.generateChild():
            self.searchInitPopInstance(child)
            if self.initPoolStopEvent.is_set():
                return None



    def searchPopThreadTask(self, queue):
        """ Uniform cost search
        """

        threadID = uuid.uuid4()
        queue = list(queue)

        for node in queue:
            self.searchInitPopInstance(node)


        
    def expandInitPopInstance(self, queue):
        """
        """

        queueSet = set(queue)

        while len(queue) > 0:

            queue.sort()

            print("queue : ", len(queue), len(self.initPool))

            chromosome = queue[0]
            # print("nooode : ", node)
            queue = queue[1:]

            # print("coco : ", node)
            print(chromosome)
            mutations = (LocalSearchEngine()).process(chromosome, "population")
            print("mutations : ", mutations)

            with self.initPoolLock:

                for mutation in mutations:
                    if mutation not in queueSet:
                        if len(self.initPool) >= PopInitializer.initPoolExpectedSize:
                            self.initPoolStopEvent.set()
                            return None
                        queue.append(mutation)
                        self.initPool.add(mutation)
                        queueSet.add(mutation)
                        # if len(self.initPool) >= PopInitializer.initPoolExpectedSize:
                        #     self.initPoolStopEvent.set()
                        #     return None

                # self.initPoolSizeData["sizes"][threadID] = len(queue)
                # size = 0
                # for threadId in self.initPoolSizeData["sizes"]:
                #     size += self.initPoolSizeData["sizes"][threadId]

                # for child in children:
                #     if child is not None:
                #         queue.append(child)
                #         self.initPoolSizeData["sizes"][threadID] += 1
                #         size += 1

                #         if size  >= PopInitializer.initPoolExpectedSize:
                #             break

