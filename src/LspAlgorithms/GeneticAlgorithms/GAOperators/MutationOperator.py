from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from .LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
import random
# from collections import defaultdict
from ..PopInitialization.Population import Population
# import numpy as np


class MutationOperator:
    """
    """

    def __init__(self, ) -> None:
        """
        """

        pass


    def process(self, chromosome, chromosomes, threadIdentifier):
        """
        """

        result = (LocalSearchEngine()).process(chromosome, "negative", {"threadId": threadIdentifier})
        if result is not None:

            # updating the population
            chromosomes.remove(chromosome)
            chromosomes.add(result)

            if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] :
                LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True

            LspRuntimeMonitor.instance.remainingMutations[threadIdentifier] -= 1


    # def process(self, population):
    #     """ Got to apply mutation corresponding to the set mutation rate
    #     """

    #     selected = set()
    #     chromosomes = list(population.chromosomes)

    #     while len(selected) < Population.mutatedPoolSize[population.threadIdentifier]:
            
    #         # print("population's chromosomes : ", population.chromosomes)
    #         chromosome = random.choice(chromosomes)
    #         print("picked chromosome : ", chromosome)
    #         if chromosome.stringIdentifier not in selected:
    #             result = (LocalSearchEngine()).process(chromosome, "random", {"threadId": population.threadIdentifier})
    #             if result is not None:
    #                 selected.add(chromosome.stringIdentifier)

    #                 # updating the population
    #                 population.chromosomes.remove(chromosome)
    #                 population.chromosomes.add(result)

    #                 if not LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] :
    #                     LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] = True
