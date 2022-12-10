# from collections import defaultdict
import random
import threading
# from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
# from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .LocalSearchEngine import LocalSearchEngine
# from .MutationOperator import MutationOperator
from ..PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData
from .LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
import concurrent.futures
import numpy as np

class CrossOverOperator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.parentChromosomes = None
        self.offspring = None
        self.population = None 

        if LocalSearchEngine.localSearchMemory["content"]["left_genes"] is None:
            LocalSearchEngine.localSearchMemory["content"]["left_genes"] = dict()


    def process(self, population):
        """
        """

        self.newChromosomes = set()
        self.population = population
        # prevPopMean = np.mean([chromosome.cost for chromosome in population.chromosomes])

        self.popLock = threading.Lock()
        self.newPopLock = threading.Lock()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.threadProcess, ["args"] * ParameterData.instance.nReplicaThreads)))

        population.chromosomes = self.newChromosomes
        return self.newChromosomes


    def threadProcess(self, args):
        """
        """

        popSize = Population.popSizes[self.population.threadIdentifier]

        while True:

            with self.newPopLock:
                if len(self.newChromosomes) >= popSize:
                    break

            with self.popLock:
                chromosomeA, chromosomeB = self.population.selectionOperator.select()

            if isinstance(chromosomeA, PseudoChromosome):
                chromosomeA = LocalSearchEngine.switchItems(chromosomeA.value, self.population.threadIdentifier)
            if isinstance(chromosomeB, PseudoChromosome):
                chromosomeB = LocalSearchEngine.switchItems(chromosomeB.value, self.population.threadIdentifier)

            chromosomeC = chromosomeA

            # crossedOver = False
            if (random.random() <= ParameterData.instance.crossOverRate):
                try:
                    chromosomeC = self.mate([chromosomeA, chromosomeB])
                    # crossedOver = True
                except Exception as e:
                    raise e                

            with self.newPopLock:
                if len(self.newChromosomes) >= popSize:
                    break
                # if chromosomeC != chromosomeA or (chromosomeC == chromosomeA and chromosomeC.cost < prevPopMean):
                self.newChromosomes.add(chromosomeC)

            # print("chromosomes length : ", len(self.newChromosomes), popSize)


    def mate(self, parentChromosomes, offspring_result = 1):
        """
        """

        self.parentChromosomes = parentChromosomes

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None

        # print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].dnaArray, self.parentChromosomes[1].dnaArray)
        # print("Crossover : ", self.parentChromosomes)

        self.searchOffspring(self.parentChromosomes[0], self.parentChromosomes[1])

        # print("Cross Over result : ", [self.parentChromosomes, self.offspring])

        return self.offspring


    def directionalDeepSearch(self, chromosome, target, threadIdentifier):
        """
        """

        self._stopOffspringSearchEvent = threading.Event()

        self.crossOverCloser(chromosome, target, threadIdentifier)


    def crossOverCloser(self, chromosome, target, threadIdentifier, depthIndex = 0):
        """
        """

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, threadIdentifier)

        with LocalSearchEngine.localSearchMemory["lock"]:
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["left_genes"]:
                LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier] = dict({(gene.item, gene.position): set() for itemGenes in chromosome.dnaArray for gene in itemGenes})

        listItems = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier])
        # random.shuffle(listItems)

        possiblePaths = []

        for (geneItem, genePosition) in listItems:

            gene = chromosome.dnaArray[geneItem][genePosition]

            # print("crossing over : ", gene.period, chromosome)
            localSearchEngine = LocalSearchEngine()
            
            # improving the current gene respective of the target chromosome
            localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target, "closer_anyway": True})                        
            
            # with LocalSearchEngine.localSearchMemory["lock"]:
            if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]) == 0:
                del LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]

            if localSearchEngine.result is not None:
                if localSearchEngine.result <= self.offspring:
                    self.offspring = localSearchEngine.result

                    if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier]:
                        LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True

                    self._stopOffspringSearchEvent.set()
                    return

                possiblePaths.append(localSearchEngine.result)

        possiblePaths.sort()

        for possiblePath in possiblePaths:

            self.crossOverCloser(possiblePath, target, threadIdentifier, depthIndex + 1)
            if self._stopOffspringSearchEvent.is_set():
                return

        self._stopOffspringSearchEvent.set()


    def searchOffspring(self, chromosome, target):
        """
        """

        self._stopOffspringSearchEvent = threading.Event()

        threadIdentifier = self.population.threadIdentifier if self.population is not None else 1
        # print("Begin **********************", chromosome)

        self.searchRecursiveOffspring(chromosome, target, threadIdentifier)


    def searchRecursiveOffspring(self, chromosome, target, threadIdentifier, depthIndex = 0):
        """
        """

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, threadIdentifier)

        self.offspring = chromosome

        with LocalSearchEngine.localSearchMemory["lock"]:
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["left_genes"]:
                LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier] = dict({(gene.item, gene.position): set() for itemGenes in chromosome.dnaArray for gene in itemGenes})

        listItems = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier])
        random.shuffle(listItems)

        for (geneItem, genePosition) in listItems:

            gene = chromosome.dnaArray[geneItem][genePosition]

            # if gene.cost == 0:
            #     continue

            # print("crossing over : ", gene.period, chromosome)
            localSearchEngine = LocalSearchEngine()
            
            # improving the current gene respective of the target chromosome
            localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target})                        

            # with LocalSearchEngine.localSearchMemory["lock"]:
            if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]) == 0:
                del LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]
                # (LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier]).pop((geneItem, genePosition), None)

            if localSearchEngine.result is not None:
                self.searchRecursiveOffspring(localSearchEngine.result, target, threadIdentifier, depthIndex + 1)

                if self._stopOffspringSearchEvent.is_set():
                    return
                self.offspring = chromosome

        if self.offspring == self.parentChromosomes[0]:
            result = (LocalSearchEngine()).process(chromosome, "near_positive", {"threadId": threadIdentifier})
            if result is not None:
                self.searchRecursiveOffspring(result, target, threadIdentifier, depthIndex + 1)
            else:
                self.directionalDeepSearch(chromosome, target, threadIdentifier)
            return

        self._stopOffspringSearchEvent.set()

        if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier]:
            LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True