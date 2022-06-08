from collections import defaultdict
from math import ceil
from queue import Queue
import random
import numpy as np
import threading
import concurrent.futures
import uuid
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
import multiprocessing as mp

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    eliteSizes = defaultdict(lambda: 0)

    def __init__(self, lineageIdentifier = None) -> None:
        """
        """

        self.chromosomes = defaultdict(lambda: None)
        self.lineageIdentifier = uuid.uuid4() if lineageIdentifier is None else lineageIdentifier
        self.popLength = 0

        self.dThreadOutputPipeline = None
        self.selectionOperator = None


    def fill(self, nodeGeneratorManager):
        """
        """

        for instance in nodeGeneratorManager.getInstance():
            if instance is None:
                break
            result = self.add(instance)
            if result is None:
                break

        Population.popSizes[self.lineageIdentifier] = self.popLength


    def evolve(self):
        """
        """

        #
        # checking pipeline status
        # if not self.dThreadOutputPipeline.empty():
        #     chromosome = self.dThreadOutputPipeline.get()
        #     elites.append(chromosome)

        newPop = Population(self.lineageIdentifier)
        # filling the elites in the new population
        for chromosome in list(LspRuntimeMonitor.popsData[self.lineageIdentifier]["elites"]):
            newPop.add(chromosome)

        resultQueues = []
        instances = [None] * Population.popSizes[self.lineageIdentifier]
        instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for processIndex in range(ParameterData.instance.nReplicaThreads):
                resultQueue = Queue(maxsize=len(instances[processIndex]))
                executor.submit(self.threadTask, resultQueue)
                resultQueues.append(resultQueue)

        for resultQueue in resultQueues:
            while not resultQueue.empty():
                chromosome = resultQueue.get()
                newPop.add(chromosome)

        newPop.dThreadOutputPipeline =  self.dThreadOutputPipeline
        return newPop


    def elites(self):
        """
        """

        # Elites

        if Population.eliteSizes[self.lineageIdentifier] == 0:
            size = Population.popSizes[self.lineageIdentifier] * ParameterData.instance.elitePercentage
            size = (1 if size < 1 else size)
            Population.eliteSizes[self.lineageIdentifier] = size

        return set([self.chromosomes[key]["chromosome"] for key in self.sortedIdentifiers[:Population.eliteSizes[self.lineageIdentifier]]])


    def maxElement(self):
        """
        """

        return self.chromosomes[self.sortedIdentifiers[-1]]["chromosome"]


    def minElement(self):
        """
        """

        return self.chromosomes[self.sortedIdentifiers[0]]["chromosome"]


    def add(self, chromosome):
        """
        """

        if self.popLength >= Population.popSizes[self.lineageIdentifier]:
            return None

        if self.chromosomes[chromosome.stringIdentifier] is None:
            self.chromosomes[chromosome.stringIdentifier] = {"chromosome": chromosome, "size": 1}
        else:
            self.chromosomes[chromosome.stringIdentifier]["size"] += 1

        self.popLength += 1

        # Chromosome Pool
        if Chromosome.pool[chromosome.stringIdentifier] is None:
            Chromosome.pool[chromosome.stringIdentifier] = chromosome

        return self.chromosomes[chromosome.stringIdentifier]


    def threadTask(self, queue):
        """
        """

        threadID = uuid.uuid4()

        while not queue.full():

            # print("booooooooooooooooooooooooo")
            chromosomeA, chromosomeB = self.selectionOperator.select()
            chromosomeC, chromosomeD = chromosomeA, chromosomeB

            # print("After selection")
            random.seed()
            if (random.random() < ParameterData.instance.crossOverRate):
                chromosomeC, chromosomeD = (CrossOverOperator([chromosomeA, chromosomeB])).process()
                # print("Crossover : ", threadID, chromosomeA, chromosomeB, chromosome, len(newPop.chromosomes))

            # 1rst offspring
            random.seed()
            if random.random() < ParameterData.instance.mutationRate:
                # print("mutating")
                chromosomeC = (MutationOperator()).process(chromosomeC)

            # 2nd offspring
            random.seed()
            if random.random() < ParameterData.instance.mutationRate:
                # print("mutating")
                chromosomeD = (MutationOperator()).process(chromosomeD)

            queue.put(chromosomeC)
            if not queue.full():
                queue.put(chromosomeD)

        # print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ", queue.qsize())

        return None


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
