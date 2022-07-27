from collections import defaultdict
import multiprocessing as mp
import numpy as np
from .Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
import concurrent.futures
import threading
from queue import Queue
import copy

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.idleGenCounter = 0
        self.terminate = False


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

        # population.selectionOperator = SelectionOperator(population)


    # def processPopulation(self, action, population, resultQueues):
    #     """
    #     """

    #     if action == "definePopMetrics":
    #         self.definePopMetrics(population)



    def evaluate(self, population, generationIndex):
        """
        """

        print("Evaluating ...")

        population.sortedIdentifiers = sorted(population.chromosomes.keys(), key=lambda itemkey: population.chromosomes[itemkey]["chromosome"])

        # Termination values
        if population.explored:
            self.idleGenCounter = 0
        else:
            self.idleGenCounter += 1
            if self.idleGenCounter == ParameterData.instance.nIdleGenerations:
                self.terminate = True


        print("Evaluation idleGenCount : ", self.idleGenCounter, population.explored)


        self.definePopMetrics(population)

        # resultQueues = defaultdict(lambda: Queue())
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     executor.map(self.processPopulation, ["searchFitterElement", "definePopMetrics"], [population] * 2, [resultQueues] * 2)


        # Termination
        if self.terminate or len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
