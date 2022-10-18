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


    def process(self, population):
        """ Got to apply mutation corresponding to the set mutation rate
        """

        chromosomes = set()
        print("toto", len(chromosomes), Population.mutatedPoolSize[population.threadIdentifier], len(chromosomes) < Population.mutatedPoolSize[population.threadIdentifier])

        while len(chromosomes) < Population.mutatedPoolSize[population.threadIdentifier]:
            
            # print("population's chromosomes : ", population.chromosomes)
            chromosome = random.choice(population.chromosomes)
            print("picked chromosome : ", chromosome)
            if chromosome.stringIdentifier not in chromosomes:
                result = (LocalSearchEngine()).process(chromosome, "random", {"threadId": population.threadIdentifier})
                if result is not None:
                    chromosomes.add(chromosome.stringIdentifier)
