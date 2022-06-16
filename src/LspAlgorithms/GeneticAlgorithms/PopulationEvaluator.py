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
import copy

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.idleGenCounter = defaultdict(lambda: {"fittest": None, "count": 0})
        self.terminate = False


    def localSearchArea(self, population, resultQueue):
        """
        """
        # print("_______________________________", self.idleGenCounter[population.lineageIdentifier]["count"])
        # print("local optima : ", Chromosome.localOptima)

        # if self.idleGenCounter[population.lineageIdentifier]["count"] % ParameterData.instance.nIdleGenerations != 0:
        #     return None

        # elements = sorted(population.chromosomes.values(), key=lambda element: element["size"])

        # for element in reversed(elements):
        #     if element["chromosome"] not in Chromosome.localOptima["values"]:
        #         chromosome = element["chromosome"]
        #         result = (LocalSearchEngine().process(chromosome, "absolute_mutation"))
        #         result = result[0] if len(result) != 0 else chromosome
        #         if result < chromosome and result.stringIdentifier not in population.chromosomes.keys():
        #             resultQueue.put(result)
        #             break

        # print(" last element size : ", elements[-1]["size"], resultQueue.qsize(), float(elements[-1]["size"] / population.popLength))
        # if resultQueue.empty() and float(elements[-1]["size"] / population.popLength) >= 0.6:
        #     self.terminate = True


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
            self.localSearchArea(population, resultQueues[action])



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
            executor.map(self.processPopulation, ["localSearchArea", "definePopMetrics"], [population] * 2, [resultQueues] * 2)

        #
        if not (resultQueues["localSearchArea"]).empty():
            localSearchAreaResult = (resultQueues["localSearchArea"]).get()
            print("rude", localSearchAreaResult)

            elites = sorted(LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])
            if localSearchAreaResult < elites[-1]:
                (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).add(localSearchAreaResult)

            population.chromosomes[(self.idleGenCounter[population.lineageIdentifier]["fittest"]).stringIdentifier]["size"] -= 1
            population.popLength -= 1
            population.add(localSearchAreaResult)
            # print("poppp : ", population)


        # Termination
        if self.terminate or len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
