import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """
        self.flag50Percentage = False
        self.flag25Percentage = False
        LspRuntimeMonitor.popStatistics = {"min": [], "max": [], "mean": [], "std": []}


    def evaluate(self, population):
        """
        """

        population.completeInit()

        LspRuntimeMonitor.popStatistics["min"].append(population.minCostChromosome.cost)
        LspRuntimeMonitor.popStatistics["max"].append(population.maxCostChromosome.cost)

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

        
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
            population.localSeachOneIndividu()

        #
        if len(population.uniques) == 1:
            return "TERMINATE"

        return "CONTINUE"
        