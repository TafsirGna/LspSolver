from collections import defaultdict
from math import ceil
from queue import Queue
import random
import numpy as np
import threading
import concurrent.futures
import uuid
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    mutatedPoolSize = defaultdict(lambda: 0)
    popEntropySizes = defaultdict(lambda: 0)

    def __init__(self, threadIdentifier) -> None:
        """
        """

        self.threadIdentifier = threadIdentifier
        tempPopSize = (Population.popSizes[threadIdentifier] - Population.popEntropySizes[threadIdentifier])
        chromosomes = sorted({element["value"] for element in Chromosome.pool["content"].values() if element["threadId"] == threadIdentifier})
        self.chromosomes = chromosomes[:tempPopSize]
        self.chromosomes += random.sample(chromosomes[tempPopSize:], k=Population.popEntropySizes[threadIdentifier])
        self.chromosomes.sort()
        self.selectionOperator = SelectionOperator(self)


    # instances = [None] * Population.popSizes[self.lineageIdentifier]
    # instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)
    # resultQueues = [Queue(maxsize=len(instances[replicaIndex])) for replicaIndex in range(ParameterData.instance.nReplicaThreads)]


    def localSearch(self):
        """
        """

        # print("waaaaaaaaaaaaaaaaaaaaaakandaaaaaaaaaaaaaaaaaa")
        for chromosome in self.chromosomes:
            result = (LocalSearchEngine().process(chromosome, "simple_mutation", {"threadId": self.threadIdentifier}))
            if result < chromosome:
                break


    def __repr__(self):
        """
        """
        
        return "Population : {}".format(self.chromosomes)
