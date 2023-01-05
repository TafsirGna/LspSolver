import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .InitSearchNode import SearchNode
from queue import Queue
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import numpy as np
import concurrent.futures
import uuid
from ..PopInitialization.Chromosome import Chromosome
from collections import defaultdict
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine

class PopInitializer:
    """
    """

    SMALL_INSTANCE_CATEGORY = "small"
    BIG_INSTANCE_CATEGORY = "big"
    initPoolExpectedSize = None

    def __init__(self, instance_category = SMALL_INSTANCE_CATEGORY) -> None:
        """
        """

        self.primeThreadIdentifiers = [uuid.uuid4() for _ in range(ParameterData.instance.nPrimaryThreads)]

        if PopInitializer.initPoolExpectedSize is None:
            PopInitializer.initPoolExpectedSize = ParameterData.instance.popSize * ParameterData.instance.nPrimaryThreads

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
            print(list(executor.map(self.stuffPopThreadTask, list(range(ParameterData.instance.nPrimaryThreads)), chromosomes)))

        LspRuntimeMonitor.instance.output(str(Chromosome.pool))
        return self.primeThreadIdentifiers


    def stuffPopThreadTask(self, popIndex, chromosomes):
        """
        """

        Population.popSizes[self.primeThreadIdentifiers[popIndex]] = len(chromosomes)

        for chromosome in chromosomes:
            with Chromosome.pool["lock"]:
                Chromosome.pool["content"][chromosome.stringIdentifier] = set({self.primeThreadIdentifiers[popIndex]})

            Chromosome.popByThread[self.primeThreadIdentifiers[popIndex]]["content"][chromosome.stringIdentifier] = chromosome

        Population.mutatedPoolSize[self.primeThreadIdentifiers[popIndex]] = int(len(Chromosome.popByThread[self.primeThreadIdentifiers[popIndex]]["content"]) * ParameterData.instance.mutationRate)


class PopInitializerSmallInstanceApproach:
    """
    """

    def __init__(self, initPool) -> None:
        """
        """

        self.initPool = initPool
        self.initPoolSizeData = {"lock": threading.Lock(), "size": 0}
        self.process()


    def process(self):
        """
        """

        queue = SearchNode.root().children()
        self.initPoolSizeData["size"] = len(queue)
        queues = np.array_split(queue, ParameterData.instance.nReplicaThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # executor.map(self.searchPopThreadTask, [queue])
            print(list(executor.map(self.searchPopThreadTask, queues)))


    def searchPopThreadTask(self, queue):
        """
        """

        queue = list(queue)
        prevSavedPeriod = InputDataInstance.instance.nPeriods

        while len(queue) > 0:
            # print("len : ", queue)

            # here, I want to sort all queue's elements of the same period before starting processing them 
            if (queue[0]).period != prevSavedPeriod:
                with self.initPoolSizeData["lock"]:
                    poolSize = self.initPoolSizeData["size"]

                if poolSize < PopInitializer.initPoolExpectedSize:
                    period = (queue[0]).period
                    lastIndex = len(queue) - 1
                    for index, element in enumerate(queue):
                        if element.period != period:
                            lastIndex = index

                    sameLevelNodes = queue[0:lastIndex]
                    sameLevelNodes.sort()
                    queue[0:lastIndex] = sameLevelNodes
                    
                prevSavedPeriod = (queue[0]).period

            node = queue[0]
            # print("nooode : ", node)
            queue = queue[1:]

            if node.period == -1: # No children
                node.chromosome.stringIdentifier = tuple(node.chromosome.stringIdentifier)
                self.initPool.add(node.chromosome)
                continue

            # children = node.advancedChildren()
            removed = False
            for child in node.generateChild():
                with self.initPoolSizeData["lock"]:
                    if not removed:
                        self.initPoolSizeData["size"] -= 1
                        removed = True
                    if self.initPoolSizeData["size"] >= PopInitializer.initPoolExpectedSize:
                        break
                    queue.append(child)
                    self.initPoolSizeData["size"] += 1



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
                if len(self.initPool) >= PopInitializer.initPoolExpectedSize:
                    self.initPoolStopEvent.set()
                    return None
                self.initPool.add(node.chromosome)
            self.expandInitPopInstance([node.chromosome])
            return None

        # for child in node.advancedChild():
        for child in node.generateChild():
            # print("prou")
            # print("chop : ", child)
            self.searchInitPopInstance(child)
            if self.initPoolStopEvent.is_set():
                return None



    def searchPopThreadTask(self, queue):
        """ Uniform cost search
        """
        
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

