import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from ParameterSearch.ParameterData import ParameterData

class GATerminator:
    """
    """

    def __init__(self) -> None:
        """
        """


    def toTerminate(self, population):
        """
        """

        # Setting the threshold under which a populatioin is set to have converged
        threshold = int(ParameterData.instance.convergenceThresholdPercentage * population.popSize)
        threshold = 1 if threshold < 1 else threshold

        if len(population.uniques) <= threshold:
            return True
        return False
        