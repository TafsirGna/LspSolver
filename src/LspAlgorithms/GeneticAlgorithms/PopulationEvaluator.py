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
        self.threshold1Flag = False
        self.threshold2Flag = False
        self.threshold3Flag = False


    def evaluate(self, population):
        """
        """

        population.completeInit()

        # setting min, max, mean
        if LspRuntimeMonitor.popsData[population.threadId] is None:
            LspRuntimeMonitor.popsData[population.threadId] = {"min": [], "max": [], "mean": [], "std": [], "elites": []}

        LspRuntimeMonitor.popsData[population.threadId]["min"].append(population.minCostChromosome.cost)
        LspRuntimeMonitor.popsData[population.threadId]["max"].append(population.maxCostChromosome.cost)

        # Elites
        nElites = len(population.elites)
        LspRuntimeMonitor.popsData[population.threadId]["elites"] += population.elites
        (LspRuntimeMonitor.popsData[population.threadId]["elites"]).sort()
        LspRuntimeMonitor.popsData[population.threadId]["elites"] = (LspRuntimeMonitor.popsData[population.threadId]["elites"])[:nElites]

        uniquesPercentage = float(len(population.uniques) / population.popSize)

        #
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage25:
            if self.threshold2Flag is False:
                ParameterData.instance.mutationRate *= 2
                self.threshold2Flag = True
                LspRuntimeMonitor.mutation_strategy = "positive_mutation"

        #
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
            if self.threshold3Flag is False:
                # ParameterData.instance.mutationRate *= 2
                self.threshold3Flag = True
                LspRuntimeMonitor.mutation_strategy = "absolute_mutation"

        #
        if len(population.uniques) == 1:
            return "TERMINATE"

        return "CONTINUE"
        