from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from .LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor
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
        while len(chromosomes) < Population.mutatedPoolSize[population.threadIdentifier]:
            
            chromosome = random.choice(population.chromosomes)
            if chromosome.stringIdentifier not in chromosomes:
                (LocalSearchEngine()).process(chromosome, "simple_mutation", {"threadId": population.threadIdentifier})
                chromosomes.add(chromosome.stringIdentifier)
