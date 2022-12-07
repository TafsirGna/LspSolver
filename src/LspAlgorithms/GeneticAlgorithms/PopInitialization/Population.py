from collections import defaultdict
# from math import ceil
# import random
# import numpy as np
# import threading
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
# from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
# from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
# import bisect

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    mutatedPoolSize = defaultdict(lambda: 0)

    def __init__(self, threadIdentifier, chromosomes) -> None:
        """
        """

        self.threadIdentifier = threadIdentifier

        self.best, self.worst = None, None
        self.setChromosomes(chromosomes)

        self.selectionOperator = SelectionOperator(self)

    # def boostChampion(self):
    #     """ Boosting the quality of the best chromosomes in the population
    #     """

    #     result = LocalSearchEngine().refine(self.best, self.threadIdentifier)
    #     if result != self.best:
    #         self.chromosomes.remove(self.best)
    #         self.chromosomes.add(result)
    #         self.best = result

    def setChromosomes(self, chromosomes):
        """
        """

        self.chromosomes = set(chromosomes)
        self.best = min(self.chromosomes)
        self.worst = max(self.chromosomes)
        
    # def localSearch(self):
    #     """
    #     """

    #     for chromosome in self.chromosomes:
    #         result = (LocalSearchEngine().process(chromosome, "crossover", {"threadId": self.threadIdentifier}))
    #         if result is not None and result < chromosome:
    #             break


    def __repr__(self):
        """
        """
        
        return "Population : {}".format(self.chromosomes)
