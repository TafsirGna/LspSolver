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
from ..LocalSearch.LocalSearchEngine import LocalSearchEngine

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    eliteSizes = defaultdict(lambda: 0)
    initPopLocalOptimaCount = defaultdict(lambda: 0)

    def __init__(self, lineageIdentifier = None) -> None:
        """
        """

        self.chromosomes = defaultdict(lambda: None)
        self.lineageIdentifier = uuid.uuid4() if lineageIdentifier is None else lineageIdentifier
        self.popLength = 0

        self.dThreadOutputPipeline = None
        self.selectionOperator = None
        self.newPopLock = threading.Lock()


    def fill(self, nodeGeneratorManager):
        """
        """

        for instance in nodeGeneratorManager.getInstance():
            if instance is None:
                break
            # if Population.initPopLocalOptimaCount[self.lineageIdentifier] < ParameterData.instance.nInitPopLocalOptima:
            #     result = (LocalSearchEngine().process(instance, "absolute_mutation"))
            #     if len(result) > 0:
            #         instance = result[0]
            #         print("oooooooooooooooooooooooooooooooooooo", instance)
            #         Population.initPopLocalOptimaCount[self.lineageIdentifier] += 1
            result = self.add(instance)
            if result is None:
                break

        Population.popSizes[self.lineageIdentifier] = self.popLength
        # print(self.popLength)


    def evolve(self):
        """
        """

        #
        # checking pipeline status
        # if not self.dThreadOutputPipeline.empty():
        #     chromosome = self.dThreadOutputPipeline.get()
        #     elites.append(chromosome)

        self.selectionOperator = SelectionOperator(self)

        self.newPop = Population(self.lineageIdentifier)
        # filling the elites in the new population
        for chromosome in list(LspRuntimeMonitor.popsData[self.lineageIdentifier]["elites"]):
            self.newPop.add(chromosome)

        # instances = [None] * Population.popSizes[self.lineageIdentifier]
        # instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)
        # resultQueues = [Queue(maxsize=len(instances[replicaIndex])) for replicaIndex in range(ParameterData.instance.nReplicaThreads)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.threadTask, ["placeholder"] * ParameterData.instance.nReplicaThreads)))
            # for i in range(ParameterData.instance.nReplicaThreads):
            #     executor.submit(self.threadTask)

        self.newPop.dThreadOutputPipeline =  self.dThreadOutputPipeline
        return self.newPop


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

        if self.popLength >= Population.popSizes[self.lineageIdentifier]: # - ParameterData.instance.nInitPopLocalOptima:
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


    @classmethod
    def tryMutation(cls, chromosome):
        """
        """
        
        random.seed()
        if random.random() <= ParameterData.instance.mutationRate:
            # print("mutating chromosome")
            chromosome = (MutationOperator()).process(chromosome)


    def threadTask(self, placeholder = None):
        """
        """

        # print("Starting thread")

        threadID = uuid.uuid4()

        queue = Queue(maxsize=4)

        while self.newPop.popLength < Population.popSizes[self.lineageIdentifier]:

            while not queue.full():

                chromosomeA, chromosomeB = self.selectionOperator.select()
                chromosomeC, chromosomeD = chromosomeA, chromosomeB

                # print("After selecting")
                random.seed()
                if (random.random() <= ParameterData.instance.crossOverRate):
                    try:
                        # pass
                        # print("mating")
                        offsprings = (CrossOverOperator([chromosomeA, chromosomeB])).process()
                        # print("offsprings : ", offsprings)
                        chromosomeC, chromosomeD = offsprings
                    except Exception as e:
                        print("Exception")
                        raise e

                # print("after mating")

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(Population.tryMutation, [chromosomeC, chromosomeD])

                # Population.tryMutation(chromosomeC)

                # Population.tryMutation(chromosomeD)

                # print("Queueing C")
                queue.put(chromosomeC)
                # print("Queueing D")
                queue.put(chromosomeD)

            with self.newPopLock:
                while not queue.empty() and self.newPop.popLength < Population.popSizes[self.lineageIdentifier]:
                    self.newPop.add(queue.get())


        # print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ", queue.qsize())
        return None


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
