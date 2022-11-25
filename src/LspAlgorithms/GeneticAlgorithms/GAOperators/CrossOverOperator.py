from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .LocalSearchEngine import LocalSearchEngine
# from .MutationOperator import MutationOperator
from ..PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData
from .LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor

class CrossOverOperator:
    """
    """

    def __init__(self) -> None:
        """
        """

        self.parentChromosomes = None
        self.offsprings = {0: None, 1: None}
        self.population = None 

        if LocalSearchEngine.localSearchMemory["content"]["left_genes"] is None:
            LocalSearchEngine.localSearchMemory["content"]["left_genes"] = dict()

        # self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}


    def process(self, population):
        """
        """

        self.newChromosomes = set()
        self.population = population

        while len(self.newChromosomes) < Population.popSizes[population.threadIdentifier]:

            chromosomeA, chromosomeB = population.selectionOperator.select()

            if isinstance(chromosomeA, PseudoChromosome):
                chromosomeA = LocalSearchEngine.switchItems(chromosomeA.value, population.threadIdentifier)
            if isinstance(chromosomeB, PseudoChromosome):
                chromosomeB = LocalSearchEngine.switchItems(chromosomeB.value, population.threadIdentifier)

            chromosomeC = chromosomeA

            crossedOver = False
            if (random.random() <= ParameterData.instance.crossOverRate):
                try:
                    chromosomeC = self.mate([chromosomeA, chromosomeB])
                    crossedOver = True
                except Exception as e:
                    raise e                

            self.newChromosomes.add(chromosomeC)

            print("chromosomes length : ", len(self.newChromosomes), Population.popSizes[population.threadIdentifier])

        population.chromosomes = self.newChromosomes
        return self.newChromosomes


    def mate(self, parentChromosomes, offspring_result = 1):
        """
        """

        self.parentChromosomes = parentChromosomes

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None, None

        # print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].dnaArray, self.parentChromosomes[1].dnaArray)
        print("Crossover : ", self.parentChromosomes)

        self.setOffsprings()

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        # return tuple(self.offsprings.values())
        return self.offsprings[0]


    def setOffsprings(self):
        """
        """
        
        # for i in [0, 1]:
        for i in [0]:
            self.searchOffspring(i)


    def crossOverCloser(self, chromosome, target, threadIdentifier):
        """
        """

        listItems = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier])
        random.shuffle(listItems)

        for (geneItem, genePosition) in listItems:

            gene = chromosome.dnaArray[geneItem][genePosition]

            print("crossing over : ", gene.period, chromosome)
            localSearchEngine = LocalSearchEngine()
            
            # improving the current gene respective of the target chromosome
            localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target, "closer_anyway": True})                        
            
            if localSearchEngine.result is not None:
                # with LocalSearchEngine.localSearchMemory["lock"]:
                if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]) == 0:
                    del LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]

                return localSearchEngine.result


    def searchOffspring(self, offspringIndex):
        """
        """

        self._stopOffspringSearchEvent = threading.Event()

        target = self.parentChromosomes[0] if offspringIndex == 1 else self.parentChromosomes[1]
        threadIdentifier = self.population.threadIdentifier if self.population is not None else 1
        print("Begin **********************", self.parentChromosomes[offspringIndex])

        self.searchRecursiveOffspring(offspringIndex, self.parentChromosomes[offspringIndex], target, threadIdentifier)


    def searchRecursiveOffspring(self, offspringIndex, chromosome, target, threadIdentifier, depthIndex = 0):
        """
        """

        print("oooooooooooooooooo : ",chromosome)

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, threadIdentifier)

        self.offsprings[offspringIndex] = chromosome

        with LocalSearchEngine.localSearchMemory["lock"]:
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["left_genes"]:
                LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier] = dict({(gene.item, gene.position): set() for itemGenes in chromosome.dnaArray for gene in itemGenes})

        listItems = list(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier])
        random.shuffle(listItems)

        for (geneItem, genePosition) in listItems:

            gene = chromosome.dnaArray[geneItem][genePosition]

            print("crossing over : ", gene.period, chromosome)
            localSearchEngine = LocalSearchEngine()
            
            # improving the current gene respective of the target chromosome
            localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target})                        
            if localSearchEngine.result is not None:
                self.searchRecursiveOffspring(offspringIndex, localSearchEngine.result, target, threadIdentifier, depthIndex + 1)
                if self._stopOffspringSearchEvent.is_set():
                    return
                self.offsprings[offspringIndex] = chromosome

            # with LocalSearchEngine.localSearchMemory["lock"]:
            if len(LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]) == 0:
                del LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier][(geneItem, genePosition)]
                # (LocalSearchEngine.localSearchMemory["content"]["left_genes"][chromosome.stringIdentifier]).pop((geneItem, genePosition), None)

        if self.offsprings[offspringIndex] == self.parentChromosomes[offspringIndex]:
            # result = self.crossOverCloser(self.offsprings[offspringIndex], target, threadIdentifier)
            # self.offsprings[offspringIndex] = self.offsprings[offspringIndex] if result is None else result
            return

        if self.offsprings[offspringIndex] not in self.newChromosomes and self.offsprings[offspringIndex] not in self.population.chromosomes:
            self._stopOffspringSearchEvent.set()

            if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier]:
                LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True