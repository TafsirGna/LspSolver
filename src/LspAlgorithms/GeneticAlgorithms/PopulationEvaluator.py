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
        self.flag25Percentage = False


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
        elites = population.elites()
        nElites = len(elites)
        LspRuntimeMonitor.popsData[population.threadId]["elites"] += elites
        (LspRuntimeMonitor.popsData[population.threadId]["elites"]).sort()
        LspRuntimeMonitor.popsData[population.threadId]["elites"] = (LspRuntimeMonitor.popsData[population.threadId]["elites"])[:nElites]

        uniquesPercentage = float(len(population.uniques) / population.popSize)

        
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage25:
            if self.flag25Percentage is False:
                ParameterData.instance.mutationRate *= 2
                self.flag25Percentage = True
                LspRuntimeMonitor.mutation_strategy = "positive_mutation"

        
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
        #     population.localSeachOneIndividu()

        #
        if len(population.uniques) == 1:
            return "TERMINATE"

        return "CONTINUE"
        