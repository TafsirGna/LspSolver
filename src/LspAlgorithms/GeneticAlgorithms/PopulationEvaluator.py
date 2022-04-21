import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from ParameterSearch.ParameterData import ParameterData

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """
        self.flag50Percentage = False
        self.flag25Percentage = False
        self.popStatistics = {"min": [], "max": [], "mean": [], "std": []}


    def evaluate(self, population):
        """
        """

        # Setting the threshold under which a populatioin is set to have converged
        # threshold = int(ParameterData.instance.convergenceThresholdPercentage * population.popSize)
        # threshold = 1 if threshold < 1 else threshold

        self.popStatistics["min"].append(population.minCostChromosome.cost)
        self.popStatistics["max"].append(population.maxCostChromosome.cost)

        uniquesPercentage = float(len(population.uniques) / population.popSize)

        # #
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage25:
        #     if self.flag25Percentage is False:
        #         ParameterData.instance.mutationRate *= 2
        #         self.flag25Percentage = True

        # #
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage50:
        #     if self.flag50Percentage is False:
        #         ParameterData.instance.mutationRate *= 2
        #         self.flag50Percentage = True

        #
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
        #     population.localSeachOneIndividu()

        #
        if len(population.uniques) == 1:
            return "TERMINATE"

        return "CONTINUE"
        