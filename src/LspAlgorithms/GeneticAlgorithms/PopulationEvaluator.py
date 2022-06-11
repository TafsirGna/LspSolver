from collections import defaultdict
import multiprocessing as mp
import numpy as np
from .Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
import concurrent.futures
import threading
from queue import Queue

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.idleGenCounter = defaultdict(lambda: {"fittest": None, "count": 0})
        self.local_optima = set()
        self.terminate = False


    def localSearchArea(self, popLineageIdentifier, resultQueue):
        """
        """

        if self.idleGenCounter[popLineageIdentifier]["fittest"] in self.local_optima:
            self.terminate = True
            return None

        result = (LocalSearchEngine().process(self.idleGenCounter[popLineageIdentifier]["fittest"], "absolute_mutation"))
        # result = (LocalSearchEngine().process(Chromosome.createFromIdentifier(stringIdentifier=(0, 0, 2, 2, 3, 1, 2, 1)), "simple_mutation"))
        # result = (LocalSearchEngine().process(chromosome, "positive_mutation"))
        result = chromosome if len(result) == 0 else result[0]

        print("ok 1")
        if self.idleGenCounter[popLineageIdentifier]["fittest"] is not None and result < self.idleGenCounter[popLineageIdentifier]["fittest"]:
            print("ok 2")
            resultQueue.put(result)

            if result not in self.local_optima:
                self.local_optima.add(result)

        print("end")


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


    def processPopulation(self, action, population, resultQueues):
        """
        """

        if action == "definePopMetrics":
            self.definePopMetrics(population)

        if action == "localSearchArea":
            self.localSearchArea(population.lineageIdentifier, resultQueues[action])



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


        resultQueues = defaultdict(lambda: Queue())
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.processPopulation, ["localSearchArea", "definePopMetrics"], [population] * 2, [resultQueues] * 2)))


        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     # local search areas
        #     if self.idleGenCounter[population.lineageIdentifier]["count"] >= ParameterData.instance.nIdleGenerations:
        #         executor.submit(self.localSearchArea, population.lineageIdentifier, resultQueues["localSearchArea"])

        #
        print("flush")
        if not (resultQueues["localSearchArea"]).empty():
            localSearchAreaResult = (resultQueues["localSearchArea"]).get()

            if localSearchAreaResult is not None:
                # (LspRuntimeMonitor.popsData[popLineageIdentifier]["elites"]).add(result)
                population.chromosomes[(self.idleGenCounter[population.lineageIdentifier]["fittest"]).stringIdentifier]["size"] -= 1
                population.add(localSearchAreaResult)


        # Termination
        if self.terminate or len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
