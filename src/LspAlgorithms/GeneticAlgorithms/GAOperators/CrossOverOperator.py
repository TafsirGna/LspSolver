from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .LocalSearchEngine import LocalSearchEngine
from .MutationOperator import MutationOperator
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

        if LocalSearchEngine.localSearchMemory["content"]["visited_genes"] is None:
            LocalSearchEngine.localSearchMemory["content"]["visited_genes"] = dict()

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

            if crossedOver and chromosomeC == chromosomeA:
                # TODO
                pass

            # mutation
            # if (random.random() <= ParameterData.instance.mutationRate):
            #     result = (LocalSearchEngine()).process(chromosomeC, "inexplored", {"threadId": population.threadIdentifier})
            #     chromosomeC = chromosomeC if result is None else result

            self.newChromosomes.add(chromosomeC)

            # if crossedOver and len(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosomeC.stringIdentifier]) == 0 and LspRuntimeMonitor.instance.remainingMutations[population.threadIdentifier] > 0:
            #     (MutationOperator()).process(chromosomeC, chromosomes, population.threadIdentifier)


            # if crossedOver and chromosomeD == chromosomeB:
            #     # TODO
            #     pass

            # # mutation
            # # if (random.random() <= ParameterData.instance.mutationRate):
            # #     result = (LocalSearchEngine()).process(chromosomeC, "inexplored", {"threadId": population.threadIdentifier})
            # #     chromosomeD = chromosomeD if result is None else result

            # self.newChromosomes.add(chromosomeD)

            # # if crossedOver and len(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosomeD.stringIdentifier]) == 0 and LspRuntimeMonitor.instance.remainingMutations[population.threadIdentifier] > 0:
            # #     (MutationOperator()).process(chromosomeD, chromosomes, population.threadIdentifier)

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


    # def searchOffspring(self, offspringIndex):
    #     """
    #     """

    #     threadIdentifier = self.population.threadIdentifier if self.population is not None else 1
    #     target = self.parentChromosomes[0] if offspringIndex == 1 else self.parentChromosomes[1]
    #     print("Begin **********************", self.parentChromosomes[offspringIndex], target)

    #     queue = [self.parentChromosomes[offspringIndex]]
    #     while len(queue) > 0:
    #         chromosome = queue[-1]
    #         # offspring = chromosome
    #         self.offsprings[offspringIndex] = chromosome
    #         queue = queue[:-1] 

    #         if isinstance(chromosome, PseudoChromosome):
    #             chromosome = LocalSearchEngine.switchItems(chromosome.value, self.population.threadIdentifier)

    #         with LocalSearchEngine.localSearchMemory["lock"]:
    #             if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["visited_genes"]:
    #                     LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier] = [gene for itemGenes in chromosome.dnaArray for gene in itemGenes if gene.cost > 0]
    #                     random.shuffle(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier])  

    #         for gene in LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier]:

    #             print("crossing over : ", gene.period, chromosome)
    #             localSearchEngine = LocalSearchEngine()
    #             # improving the current gene respective of the target chromosome
    #             localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target})                        
    #             if localSearchEngine.result is not None:
    #                 queue.append(localSearchEngine.result)
    #                 break

    #             with LocalSearchEngine.localSearchMemory["lock"]:
    #                 (LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier]).remove(gene)

    #     # TO REVIEW
    #     # if self.offsprings[offspringIndex] in self.newChromosomes:
    #     #     self.offsprings[offspringIndex] = self.parentChromosomes[offspringIndex]

    #     if not LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] \
    #         and self.offsprings[offspringIndex] != self.parentChromosomes[offspringIndex]:
    #         LspRuntimeMonitor.instance.newInstanceAdded[self.population.threadIdentifier] = True

    #     print(" xxxxxxxx : ", self.offsprings[offspringIndex])
    #     # return offspring



    def searchOffspring(self, offspringIndex):
        """
        """

        self._stopOffspringSearchEvent = threading.Event()

        target = self.parentChromosomes[0] if offspringIndex == 1 else self.parentChromosomes[1]
        threadIdentifier = self.population.threadIdentifier if self.population is not None else 1
        print("Begin **********************", self.parentChromosomes[offspringIndex])

        self.searchRecursiveOffspring(offspringIndex, self.parentChromosomes[offspringIndex], target, threadIdentifier)


    def searchRecursiveOffspring(self, offspringIndex, chromosome, target, threadIdentifier):
        """
        """

        print("oooooooooooooooooo : ",chromosome)

        if isinstance(chromosome, PseudoChromosome):
            chromosome = LocalSearchEngine.switchItems(chromosome.value, threadIdentifier)

        self.offsprings[offspringIndex] = chromosome

        with LocalSearchEngine.localSearchMemory["lock"]:
            if chromosome.stringIdentifier not in LocalSearchEngine.localSearchMemory["content"]["visited_genes"]:
                LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier] = [gene for itemGenes in chromosome.dnaArray for gene in itemGenes if gene.cost > 0]
                random.shuffle(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier])

        for gene in LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier]:

            print("crossing over : ", gene.period, chromosome)
            localSearchEngine = LocalSearchEngine()
            
            # improving the current gene respective of the target chromosome
            localSearchEngine.improveGene(chromosome, gene, "crossover", None, {"threadId": threadIdentifier, "target": target})                        
            if localSearchEngine.result is not None:
                self.searchRecursiveOffspring(offspringIndex, localSearchEngine.result, target, threadIdentifier)
                if self._stopOffspringSearchEvent.is_set():
                    return
                self.offsprings[offspringIndex] = chromosome

            # with LocalSearchEngine.localSearchMemory["lock"]:
            (LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier]).remove(gene)
            random.shuffle(LocalSearchEngine.localSearchMemory["content"]["visited_genes"][chromosome.stringIdentifier])

        
        if self.offsprings[offspringIndex] not in self.newChromosomes:
            self._stopOffspringSearchEvent.set()

        if not LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] \
            and self.offsprings[offspringIndex] != self.parentChromosomes[offspringIndex]:
            LspRuntimeMonitor.instance.newInstanceAdded[threadIdentifier] = True