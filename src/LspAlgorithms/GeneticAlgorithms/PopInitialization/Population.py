from collections import defaultdict
from math import ceil
from queue import Queue
import random
import numpy as np
import threading
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

        processes = []
        resultQueues = []
        instances = [None] * Population.popSizes[self.lineageIdentifier]
        instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)
        for processIndex in range(ParameterData.instance.nReplicaThreads):
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ", len(instances[processIndex]))
            resultQueue = mp.Queue(maxsize=len(instances[processIndex]))
            process = mp.Process(target=self.threadTask, args=(self.selectionOperator, resultQueue))
            process.start()
            resultQueues.append(resultQueue)
            processes.append(process)

        # print("bibi")
        for process in processes:
            process.join()

        # print("Priiiince", len(resultQueues))
        for resultQueue in resultQueues:
            # print("Priiiince")
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


    def threadTask(self, selectionOperator, queue):
        """
        """

        threadID = uuid.uuid4()

        while not queue.full():

            # print("booooooooooooooooooooooooo")
            chromosomeA, chromosomeB = selectionOperator.select()
            chromosome = None

            # print("After selection")
            random.seed()
            if (random.random() < ParameterData.instance.crossOverRate):
                chromosome = (CrossOverOperator([chromosomeA, chromosomeB])).process()
                # print("Crossover : ", threadID, chromosomeA, chromosomeB, chromosome, len(newPop.chromosomes))
            else:
                chromosome = chromosomeA if chromosomeA < chromosomeB else chromosomeB

            random.seed()
            # print("After cross over")
            if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                # Proceding to mutate the chromosome
                # print("mutating")
                chromosome = (MutationOperator()).process(chromosome)

            if chromosome is not None:
                # print("Adding new chromosome 1")
                # print(chromosome)
                queue.put(chromosome)
                # print("Adding new chromosome 2")

        # print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ", queue.qsize())

        return None


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
