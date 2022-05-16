import random
import threading
import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .LocalSearch.LocalSearchEngine import LocalSearchEngine

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """
        self.threshold1Event = threading.Event()
        self.threshold2Event = threading.Event()
        self.threshold3Event = threading.Event()


    def evaluate(self, population, dThreadInputPipeline, generationIndex):
        """
        """

        if LspRuntimeMonitor.popsData[population.lineageIdentifier] is None:
            LspRuntimeMonitor.popsData[population.lineageIdentifier] = {"min": [], "max": [], "mean": [], "std": [], "elites": set()}

        # setting min, max, mean
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"].append(population.minElement().cost)
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"].append(population.maxElement().cost)

        # Elites
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).union(population.elites())
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = set(sorted(LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])[:Population.eliteSizes[population.lineageIdentifier]])

        #
        uniquesPercentage = float(len(population.chromosomes) / Population.popSizes[population.lineageIdentifier])

        #
        if uniquesPercentage <= ParameterData.instance.popUniquesPercentage50:
            if not self.threshold2Event.is_set():
                print("55555555555555000000000000000000000000000000000000000000000000000000000000", generationIndex)
                old = max(population.chromosomes.values(), key=lambda element: element["size"])
                new = (LocalSearchEngine().process(old["chromosome"], "positive_mutation"))
                new = old["chromosome"] if len(new) == 0 else new[0]
                if new < old["chromosome"]:
                    (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).add(new )
                self.threshold2Event.set()


        #
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage25:
        #     if not self.threshold2Event.is_set():
        #         print("7555555555555555555555555555555555555555555555555555555555555555555555555", generationIndex)
        #         ParameterData.instance.mutationRate *= 2
        #         self.threshold2Event.set()
        #         LspRuntimeMonitor.mutation_strategy = "positive_mutation"
        #     else:
        #         LspRuntimeMonitor.mutation_strategy = "simple_mutation"


        #
        # if uniquesPercentage <= ParameterData.instance.popUniquesPercentage10:
        #     if not self.threshold3Event.is_set():
        #         # ParameterData.instance.mutationRate *= 2
        #         self.threshold3Event.set()
        #         LspRuntimeMonitor.mutation_strategy = "absolute_mutation"
        #         print("9999999999999999990000000000000000000000000000000000000000000000000000000", LspRuntimeMonitor.mutation_strategy, generationIndex)
        #     # else:
        #     #     LspRuntimeMonitor.mutation_strategy = "simple_mutation"

        #
        if len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
        