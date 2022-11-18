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
            result = (LocalSearchEngine()).process(chromosome, "inexplored", {"threadId": threadIdentifier})
            if result is not None:
                LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] else False
                LspRuntimeMonitor.instance.remainingMutations[threadIdentifier] -= 1
                return result

        return chromosome

