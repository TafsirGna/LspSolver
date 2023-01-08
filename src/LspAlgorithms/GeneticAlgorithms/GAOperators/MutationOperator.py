# from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
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


    def process(self, chromosome, threadIdentifier):
        """
        """

        result = (LocalSearchEngine()).process(chromosome, "random", {"threadId": threadIdentifier})
        return result
        

    def processPop(self, population):
        """
        """
        
        chromosomes = list(population.chromosomes)
        random.shuffle(chromosomes)

        counter = 0
        for chromosome in chromosomes:

            # print("population's chromosomes : ", population.chromosomes)
            # print("picked chromosome : ", chromosome)

            # result = self.process(chromosome, population.threadIdentifier)
            localSearchEngine = LocalSearchEngine()
            localSearchEngine.population = population
            result = localSearchEngine.process(chromosome, "random", {"threadId": population.threadIdentifier})
            if result is not None:
                counter += 1

                # updating the population
                population.chromosomes.remove(chromosome)
                population.chromosomes.add(result)

                if not LspRuntimeMonitor.instance.newInstanceAdded[population.threadIdentifier] :
                    LspRuntimeMonitor.instance.newInstanceAdded[population.threadIdentifier] = True

            if result and counter >= Population.mutatedPoolSize[population.threadIdentifier]:
                break
