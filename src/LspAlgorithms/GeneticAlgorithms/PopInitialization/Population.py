from collections import defaultdict
from math import ceil
from queue import Queue
import random
import numpy as np
import threading
import concurrent.futures
import uuid
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    mutatedPoolSize = defaultdict(lambda: 0)

    def __init__(self, threadIdentifier, chromosomes) -> None:
        """
        """

        self.threadIdentifier = threadIdentifier
        self.chromosomes = chromosomes
        self.selectionOperator = SelectionOperator(self)


    # instances = [None] * Population.popSizes[self.lineageIdentifier]
    # instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)
    # resultQueues = [Queue(maxsize=len(instances[replicaIndex])) for replicaIndex in range(ParameterData.instance.nReplicaThreads)]


    def localSearch(self):
        """
        """



    def __repr__(self):
        """
        """
        return "Population : {}".format(self.chromosomes)
