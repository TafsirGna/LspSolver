import threading
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
        self.threshold1Event = threading.Event()
        self.threshold2Event = threading.Event()
        self.threshold3Event = threading.Event()


    def evaluate(self, population, generationIndex):
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
            if not self.threshold2Event.is_set():
                print("7555555555555555555555555555555555555555555555555555555555555555555555555", generationIndex)
                ParameterData.instance.mutationRate *= 2
                self.threshold2Event.set()
                LspRuntimeMonitor.mutation_strategy = "positive_mutation"

        #
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
            if not self.threshold3Event.is_set():
                # ParameterData.instance.mutationRate *= 2
                self.threshold3Event.set()
                LspRuntimeMonitor.mutation_strategy = "absolute_mutation"

        #
        if len(population.uniques) == 1:
            return "TERMINATE"

        return "CONTINUE"
        