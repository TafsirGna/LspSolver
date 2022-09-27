from collections import defaultdict
# from math import ceil
import random
# import numpy as np
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
import bisect

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    mutatedPoolSize = defaultdict(lambda: 0)
    popEntropySizes = defaultdict(lambda: 0)

    def __init__(self, threadIdentifier) -> None:
        """
        """

        self.threadIdentifier = threadIdentifier

        self.setChromosomes()
        
        self.selectionOperator = SelectionOperator(self)

    # instances = np.array_split(instances, ParameterData.instance.nReplicaThreads)


    def setChromosomes(self):
        """
        """

        self.chromosomes = list(Chromosome.popByThread[self.threadIdentifier]["sortedList"]["list"])
        identifiers = set(Chromosome.popByThread[self.threadIdentifier]["sortedList"]["identifiers"])
        pool = list((Chromosome.popByThread[self.threadIdentifier]["content"]).values())
        while len(self.chromosomes) < Population.popSizes[self.threadIdentifier]:
            chromosome = random.sample(pool, 1)[0]
            if chromosome.stringIdentifier in identifiers:
                continue
            bisect.insort_left(self.chromosomes, chromosome)
            identifiers.add(chromosome.stringIdentifier)

        print("----------------------------------- : ", len(self.chromosomes), len(Chromosome.popByThread[self.threadIdentifier]["sortedList"]["list"]))


    def localSearch(self):
        """
        """

        for chromosome in self.chromosomes:
            result = (LocalSearchEngine().process(chromosome, "simple_mutation", {"threadId": self.threadIdentifier}))
            if result < chromosome:
                break


    def __repr__(self):
        """
        """
        
        return "Population : {}".format(self.chromosomes)
