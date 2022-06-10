from collections import defaultdict
import multiprocessing as mp
import numpy as np
from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
import concurrent.futures
import threading

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.idleGenCounter = defaultdict(lambda: {"fittest": None, "count": 0})
        self.local_optima = defaultdict(lambda: [])


    def localSearchArea(self, popLineageIdentifier):
        """
        """

        result = (LocalSearchEngine().process(self.idleGenCounter[popLineageIdentifier["fittest"]], "absolute_mutation"))
        # result = (LocalSearchEngine().process(chromosome, "positive_mutation"))
        result = chromosome if len(result) == 0 else result[0]

        if result < element["chromosome"]:
            (LspRuntimeMonitor.popsData[popLineageIdentifier]["elites"]).add(result)


    def definePopMetrics(self, population):
        """
        """

        # setting min, max, mean
        if LspRuntimeMonitor.popsData[population.lineageIdentifier] is None:
            LspRuntimeMonitor.popsData[population.lineageIdentifier] = {"min": [], "max": [], "mean": [], "std": [], "elites": set()}

        LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"].append(population.minElement().cost)
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"].append(population.maxElement().cost)

        # Elites
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).union(population.elites())
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = set(sorted(LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])[:Population.eliteSizes[population.lineageIdentifier]])

        population.selectionOperator = SelectionOperator(population)



    def evaluate(self, population, dThreadInputPipeline, generationIndex):
        """
        """

        print("Evaluating ...")

        population.sortedIdentifiers = sorted(population.chromosomes.keys(), key=lambda itemkey: population.chromosomes[itemkey]["chromosome"])

        # Termination values
        if self.idleGenCounter[population.lineageIdentifier]["fittest"] is None:
            self.idleGenCounter[population.lineageIdentifier]["fittest"] = population.minElement()
        else:
            if self.idleGenCounter[population.lineageIdentifier]["fittest"] == population.minElement():
                self.idleGenCounter[population.lineageIdentifier]["count"] += 1
            else:
                self.idleGenCounter[population.lineageIdentifier]["fittest"] = population.minElement()
                self.idleGenCounter[population.lineageIdentifier]["count"] = 0


        with concurrent.futures.ThreadPoolExecutor() as executor:
            # defining metrics
            executor.submit(self.definePopMetrics, population)

            # local search areas
            if self.idleGenCounter[population.lineageIdentifier]["count"] == ParameterData.instance.nIdleGenerations:
                executor.submit(self.localSearchArea, population.lineageIdentifier)

        # Termination
        if len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
