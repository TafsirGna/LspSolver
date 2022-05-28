from collections import defaultdict
import multiprocessing as mp
import numpy as np
from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from .LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator

class PopulationEvaluator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.minTerminations = defaultdict(lambda: {"minValue": None, "count": 0})


    def localSearchInstance(self, chromosome, population, resultQueue):
        """
        """

        print("Elites", LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"])
        result = (LocalSearchEngine().process(chromosome, "absolute_mutation"))
        result = chromosome if len(result) == 0 else result[0]
        if result < chromosome:
            resultQueue.put(result)


    def definePopMetrics(self, population, resultQueue):
        """
        """

        population.sortedIdentifiers = sorted(population.chromosomes.keys(), key=lambda key: population.chromosomes[key]["chromosome"])

        # setting min, max, mean
        result  = {"min": 0, "max": 0, "mean": 0, "std": 0, "elites": set()}

        result["min"] = population.minElement().cost
        result["max"] = population.maxElement().cost

        # Elites
        result["elites"] = (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).union(population.elites()) if LspRuntimeMonitor.popsData[population.lineageIdentifier] is not None else population.elites()
        result["elites"] = set(sorted(result["elites"])[:Population.eliteSizes[population.lineageIdentifier]])

        result["selectionOperator"] = SelectionOperator(population, result)

        resultQueue.put(result)



    def localSearchInstances(self, population, resultQueue):
        """
        """

        # Performing a local search to all chromosomes with a given percentage of the entire population
        # triggerSize = int(ParameterData.instance.localSearchTriggerSize * Population.popSizes[population.lineageIdentifier])

        # Process code
        processes = []
        queues = []
        for element in population.chromosomes.values():
            if element["size"] >= 2:
                chromosome = element["chromosome"]
                queue = mp.Queue()
                process = mp.Process(target=self.localSearchInstance, args=(chromosome, population, queue))
                process.start()
                processes.append(process)
                queues.append(queue)

        for process in processes:
            process.join()

        # adding the results of the local search to the next whole population
        results = []
        for queue in queues:
            if not queue.empty():
                chromosome = queue.get()
                results.append(chromosome)

        resultQueue.put(results)



    def evaluate(self, population, dThreadInputPipeline, generationIndex):
        """
        """

        # given the population, an evaluation is made to determine some data as min, elites, probabilities (given fitness)
        processAQueue = mp.Queue()
        processA = mp.Process(target=self.definePopMetrics, args=(population, processAQueue))
        processA.start()

        # local search on specific instances
        processBQueue = mp.Queue()
        processB = mp.Process(target=self.localSearchInstances, args=(population, processBQueue))
        processB.start()

        # Joining processes
        processA.join()
        processB.join()

        # reading the queues
        # Process A queue
        resultProcessA = processAQueue.get()

        if LspRuntimeMonitor.popsData[population.lineageIdentifier] is None:
            LspRuntimeMonitor.popsData[population.lineageIdentifier] = {"min": [], "max": [], "mean": [], "std": [], "elites": set()}

        LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"].append(resultProcessA["min"])
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"].append(resultProcessA["max"])
        LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"] = resultProcessA["elites"]

        # Termination values
        if self.minTerminations[population.lineageIdentifier]["minValue"] is None:
            self.minTerminations[population.lineageIdentifier]["minValue"] = LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]
        else:
            if self.minTerminations[population.lineageIdentifier]["minValue"] == LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]:
                self.minTerminations[population.lineageIdentifier]["count"] += 1
            else:
                self.minTerminations[population.lineageIdentifier]["minValue"] = LspRuntimeMonitor.popsData[population.lineageIdentifier]["min"][-1]
                self.minTerminations[population.lineageIdentifier]["count"] = 0

        population.selectionOperator = resultProcessA["selectionOperator"]

        # Process B Queue
        resultProcessB = processBQueue.get()
        for chromosome in resultProcessB:
            (LspRuntimeMonitor.popsData[population.lineageIdentifier]["elites"]).add(chromosome)


        # Determine whether to terminate the whole algorithm or not
        if self.minTerminations[population.lineageIdentifier]["count"] == ParameterData.instance.nIdleGenerations:
            return "TERMINATE"

        # 3rd condition
        if len(population.chromosomes) == 1:
            return "TERMINATE"

        return "CONTINUE"
