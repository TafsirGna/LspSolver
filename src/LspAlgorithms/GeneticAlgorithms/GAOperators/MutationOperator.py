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

        if LspRuntimeMonitor.instance.remainingMutations[threadIdentifier] > 0:
            result = (LocalSearchEngine()).process(chromosome, "random", {"threadId": threadIdentifier})
            if result is not None:
                LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] else False
                LspRuntimeMonitor.instance.remainingMutations[threadIdentifier] -= 1
                return result

        return chromosome


    def processPop(self, population):
        """
        """


        pickedOnes = set()
        chromosomes = list(population.chromosomes)

        while len(pickedOnes) < Population.mutatedPoolSize[population.threadIdentifier]:

            # print("population's chromosomes : ", population.chromosomes)
            chromosome = random.choice(chromosomes)
            print("picked chromosome : ", chromosome)
            if chromosome.stringIdentifier not in pickedOnes:
                result = (LocalSearchEngine()).process(chromosome, "random", {"threadId": population.threadIdentifier})
                if result is not None:
                    pickedOnes.add(chromosome.stringIdentifier)

                    # updating the population
                    population.chromosomes.remove(chromosome)
                    population.chromosomes.add(result)

                    if not LspRuntimeMonitor.instance.newInstanceAdded[population.threadIdentifier] :
                        LspRuntimeMonitor.instance.newInstanceAdded[population.threadIdentifier] = True