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

        self.idleGenCounter = defaultdict(lambda: {"fittest": None, "count": 0})
        self.terminate = False


    def searchFitterElement(self, population, resultQueue):
        """
        """

        print("Searching fitter than : ", population.minElement())

        for element in population.chromosomes.values():
            chromosome = element["chromosome"]
            if chromosome == population.minElement():
                continue

            result = (LocalSearchEngine().process(chromosome, "fitter_than", {"fittest": population.minElement()}))
            print("Tralala : ", chromosome, result, population.minElement())
            if result != chromosome and result < population.minElement() and result.stringIdentifier not in population.chromosomes.keys():
                print("Fitter found")
                resultQueue.put(result)
                break



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

        if action == "searchFitterElement":
            self.searchFitterElement(population, resultQueues[action])



    def evaluate(self, population, generationIndex):
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
            executor.map(self.processPopulation, ["searchFitterElement", "definePopMetrics"], [population] * 2, [resultQueues] * 2)


        #
        if not (resultQueues["searchFitterElement"]).empty():
            print("Adding found fitter element")
            fitterElement = (resultQueues["searchFitterElement"]).get()
            print("fitter : ", fitterElement)

            elites = sorted(LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])
            if fitterElement < elites[-1]:
                (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).add(fitterElement)

            population.chromosomes[(self.idleGenCounter[population.lineageIdentifier]["fittest"]).stringIdentifier]["size"] -= 1
            population.popLength -= 1
            population.add(fitterElement)

            print("fitter element added")


        # Termination
        if self.terminate or len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
