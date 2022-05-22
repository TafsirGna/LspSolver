from collections import defaultdict
import multiprocessing
import random
import threading
import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .LocalSearch.LocalSearchEngine import LocalSearchEngine
import concurrent.futures

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.minTerminations = defaultdict(lambda: {"minValue": None, "count": 0})


    def performLocalSearch(self, chromosome, population):
        """
        """

        print("Elites", LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])
        result = (LocalSearchEngine().process(chromosome, "absolute_mutation"))
        result = chromosome if len(result) == 0 else result[0]
        if result < chromosome:
            (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).add(result)



    def evaluate(self, population, dThreadInputPipeline, generationIndex):
        """
        """

        population.sortedIdentifiers = sorted(population.chromosomes.keys(), key=lambda key: population.chromosomes[key]["chromosome"])

        if LspRuntimeMonitor.popsData[population.lineageIdentifier] is None:
            LspRuntimeMonitor.popsData[population.lineageIdentifier] = {"min": [], "max": [], "mean": [], "std": [], "elites": set()}

        # setting min, max, mean
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"].append(population.minElement().cost)
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"].append(population.maxElement().cost)

        # Termination values
        if self.minTerminations[population.lineageIdentifier]["minValue"] is None:
            self.minTerminations[population.lineageIdentifier]["minValue"] = LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]
        else:
            if self.minTerminations[population.lineageIdentifier]["minValue"] == LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]:
                self.minTerminations[population.lineageIdentifier]["count"] += 1
            else:
                self.minTerminations[population.lineageIdentifier]["minValue"] = LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]
                self.minTerminations[population.lineageIdentifier]["count"] = 0

        # Elites
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).union(population.elites())
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = set(sorted(LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])[:Population.eliteSizes[population.lineageIdentifier]])


        # Performing a local search to all chromosomes with a given percentage of the entire population
        triggerSize = int(ParameterData.instance.localSearchTriggerSize * Population.popSizes[population.lineageIdentifier])
        # Thread code 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for element in population.chromosomes.values():
                if element["size"] >= triggerSize:
                    chromosome = element["chromosome"]
                    executor.submit(self.performLocalSearch, chromosome, population)

        # Process code
        # processes = []
        # for element in population.chromosomes.values():
        #     if element["size"] >= triggerSize:
        #         chromosome = element["chromosome"]
        #         process = multiprocessing.Process(target=self.performLocalSearch, args=(chromosome, population))
        #         process.start()
        #         processes.append(process)

        # for process in processes:
        #     process.join()


        # Termination condition
        # 1st condition
        uniquePercentage = len(population.chromosomes) / Population.popSizes[population.lineageIdentifier]

        if uniquePercentage <= 0.5:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for element in population.chromosomes.values():
                    chromosome = element["chromosome"]
                    executor.submit(self.performLocalSearch, chromosome, population)
            
            return "TERMINATE"

        # # 2nd condition
        # if self.minTerminations[population.lineageIdentifier]["count"] == ParameterData.instance.nIdleGenerations:
        #     return "TERMINATE"

        # # 3rd condition
        # if len(population.chromosomes) == 1:
        #     return "TERMINATE"

        return "CONTINUE"
        