from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .LocalSearchEngine import LocalSearchEngine
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

        if LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] is None:
            LocalSearchEngine.localSearchMemory["content"]["simple_mutation"] = dict()

        # self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}


    def process(self, population):
        """
        """

        chromosomes = set()
        self.population = population

        while len(chromosomes) < Population.popSizes[population.threadIdentifier]:

            chromosomeA, chromosomeB = population.selectionOperator.select()

            if isinstance(chromosomeA, PseudoChromosome):
                chromosomeA = LocalSearchEngine.switchItems(chromosomeA.value, population.threadIdentifier)
            if isinstance(chromosomeB, PseudoChromosome):
                chromosomeB = LocalSearchEngine.switchItems(chromosomeB.value, population.threadIdentifier)

            chromosomeC = chromosomeA

            if (random.random() <= ParameterData.instance.crossOverRate):
                try:
                    chromosomeC = self.mate([chromosomeA, chromosomeB])
                except Exception as e:
                    raise e

            chromosomes.add(chromosomeC)
            print("chromosomes length : ", len(chromosomes), Population.popSizes[population.threadIdentifier])

        population.chromosomes = chromosomes
        return chromosomes


    def mate(self, parentChromosomes, offspring_result = 1):
        """
        """

        self.parentChromosomes = parentChromosomes

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None

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
        self.searchOffspring(0)


    def searchOffspring(self, offspringIndex):
        """
        """

        threadIdentifier = self.population.threadIdentifier if self.population is not None else 1
        target = self.parentChromosomes[0] if offspringIndex == 1 else self.parentChromosomes[1]
        print("Begin **********************", self.parentChromosomes[offspringIndex], target)

        queue = [self.parentChromosomes[offspringIndex]]
        while len(queue) > 0:
            chromosome = queue[-1]
            # offspring = chromosome
            self.offsprings[offspringIndex] = chromosome
            queue = queue[:-1] 

            if isinstance(chromosome, PseudoChromosome):
                chromosome = LocalSearchEngine.switchItems(chromosome.value, self.population.threadIdentifier)

            sortedGenes = sorted([gene for itemGenes in chromosome.dnaArray for gene in itemGenes])
            # random.shuffle(sortedGenes)

            for gene in reversed(sortedGenes):

                targetGene = target.dnaArray[gene.item][gene.position]
                if gene.period != targetGene.period:
                    print("crossing over : ", gene.period, chromosome)
                    localSearchEngine = LocalSearchEngine()
                    localSearchEngine.improveGene(chromosome, gene, "positive", None, {"threadId": threadIdentifier})                        
                    if localSearchEngine.result is not None:
                        queue.append(localSearchEngine.result)
                        break

        if not LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] \
            and self.offsprings[offspringIndex] not in self.population.chromosomes:
            LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] = True

        # return offspring